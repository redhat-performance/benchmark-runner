
import json
import os
import time

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.bootstorm_vm import BootstormVM
from benchmark_runner.common.oc.oc import VMStatus, OC


class WinstressVm(BootstormVM):
    """
    This class runs Windows CPU + memory stress test on Windows VMs.
    Same code path for 1 VM and N VMs.
    """
    def __init__(self):
        super().__init__()
        if not self._windows_url:
            raise ValueError('Missing Windows DV URL')
        self.__namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self.__username = self._environment_variables_dict.get('vm_user') or 'Administrator'
        self.__ssh_key_path = self._ssh_key_path
        self.__remote_dir = 'C:/tools/stress'

    def _get_vm_name(self, vm_num: str) -> str:
        if self._scale:
            return f'{self._workload_name}-{self._trunc_uuid}-{vm_num}'
        return f'{self._workload_name}-{self._trunc_uuid}'

    def _get_vm_yaml(self, vm_num: str) -> str:
        if self._scale:
            return os.path.join(self._run_artifacts_path, f'{self._name}_{vm_num}.yaml')
        return os.path.join(self._run_artifacts_path, f'{self._name}.yaml')

    SCP_RETRIES = 3

    def _scp_to_vm_with_verify(self, vm_name: str, local_path: str, remote_path: str):
        """SCP a file to the VM with verification and retry."""
        script = os.path.basename(local_path)
        for attempt in range(1, self.SCP_RETRIES + 1):
            self._virtctl._scp_to_vm(vm_name=vm_name, local_path=local_path,
                                     remote_path=remote_path,
                                     namespace=self.__namespace, key_path=self.__ssh_key_path,
                                     username=self.__username)
            verify = self._virtctl.virtctl_ssh(vm_name=vm_name,
                                               command=f'powershell -Command "if (Test-Path \'{remote_path}\') {{ echo exists }}"',
                                               namespace=self.__namespace, key_path=self.__ssh_key_path,
                                               username=self.__username, timeout=60)
            if verify and 'exists' in verify:
                logger.info(f'Copied and verified {script} on VM {vm_name}')
                return
            logger.warning(f'SCP verify failed for {script} on VM {vm_name} (attempt {attempt}/{self.SCP_RETRIES})')
            time.sleep(5)
        raise RuntimeError(f'Failed to SCP {script} to VM {vm_name} after {self.SCP_RETRIES} attempts')

    def _create_vm(self, vm_num: str):
        try:
            self._oc.create_async(yaml=self._get_vm_yaml(vm_num))
            self._oc.wait_for_vm_status(vm_name=self._get_vm_name(vm_num), status=VMStatus.Stopped)
        except Exception as err:
            self.save_error_logs()
            raise err

    def _prepare_vm(self, vm_num: str):
        try:
            vm_name = self._get_vm_name(vm_num)
            self._virtctl.start_vm_sync(vm_name=vm_name)
            if not self._virtctl._wait_for_virtctl_ssh(vm_name=vm_name, namespace=self.__namespace,
                                                       key_path=self.__ssh_key_path, username=self.__username,
                                                       timeout=OC.SHORT_TIMEOUT):
                logger.warning(f'SSH never became ready on VM {vm_name}, skipping')
                return

        except Exception as err:
            logger.warning(f'Failed to prepare VM {self._get_vm_name(vm_num)}: {err}')

    def _run_stress(self, vm_num: str):
        try:
            vm_name = self._get_vm_name(vm_num)
            self._scp_to_vm_with_verify(vm_name=vm_name,
                                         local_path=os.path.join(self._run_artifacts_path, '01_run_stress.ps1'),
                                         remote_path=f'{self.__remote_dir}/01_run_stress.ps1')
            stress_duration = self._environment_variables_dict.get('stress_duration', 600)
            logger.info(f'Running 01_run_stress.ps1 on VM {vm_name} (stress_duration={stress_duration}s, timeout={self._timeout}s) ...')
            self._virtctl.virtctl_ssh(vm_name=vm_name,
                                     command=f'powershell -NoProfile -ExecutionPolicy Bypass -File {self.__remote_dir}/01_run_stress.ps1',
                                     namespace=self.__namespace, key_path=self.__ssh_key_path,
                                     username=self.__username, timeout=self._timeout)
        except Exception as err:
            logger.warning(f'Stress test failed on VM {self._get_vm_name(vm_num)}: {err}')

    def _collect_results(self, vm_num: str):
        try:
            vm_name = self._get_vm_name(vm_num)
            local_result_json = os.path.join(self._run_artifacts_path, f'{vm_name}.json')

            check_cmd = f'powershell -Command "if (Test-Path \'{self.__remote_dir}/stress_report.json\') {{ echo found }}"'
            for elapsed in range(0, self._timeout, OC.DELAY):
                check = self._virtctl.virtctl_ssh(vm_name=vm_name, command=check_cmd,
                                                  namespace=self.__namespace, key_path=self.__ssh_key_path,
                                                  username=self.__username, timeout=60)
                if check and 'found' in check:
                    break
                logger.info(f'Waiting for stress_report.json on VM {vm_name}... ({elapsed}s)')
                time.sleep(OC.DELAY)

            if not self._virtctl._scp_file(vm_name=vm_name,
                                           remote_path=f'{self.__remote_dir}/stress_report.json',
                                           local_path=local_result_json,
                                           namespace=self.__namespace, key_path=self.__ssh_key_path,
                                           username=self.__username):
                logger.warning(f'Failed to SCP stress_report.json from VM {vm_name}')
                return

            try:
                with open(local_result_json, 'r') as f:
                    report = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f'Failed to parse stress report from {local_result_json}: {e}')
                return

            vm_node = self._oc.get_vm_node(vm_name=vm_name) or ''
            workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
            workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
            run_artifacts_url = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')

            result = {
                'cpu_total': report.get('config', {}).get('cpu_total', 0),
                'cpu_stressed': report.get('config', {}).get('cpu_stressed', 0),
                'stress_cpu_percent': report.get('config', {}).get('stress_cpu_percent', 0),
                'stress_memory_percent': report.get('config', {}).get('stress_memory_percent', 0),
                'duration_sec': report.get('config', {}).get('duration_sec', 0),
                'total_memory_gb': report.get('config', {}).get('total_memory_gb', 0),
                'total_ops': report.get('throughput', {}).get('total_ops', 0),
                'total_ops_per_sec': report.get('throughput', {}).get('total_ops_per_sec', 0),
                'avg_ops_per_cpu': report.get('throughput', {}).get('avg_ops_per_cpu', 0),
                'vm_name': vm_name,
                'node': vm_node,
                'run_artifacts_url': run_artifacts_url,
            }

            with open(local_result_json, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f'Stress results saved to {local_result_json}')
            logger.info(f'  throughput: {result["total_ops_per_sec"]:.0f} ops/sec, avg_per_cpu: {result["avg_ops_per_cpu"]:.0f} ops/sec')

        except Exception as err:
            self.save_error_logs()
            raise err

    def _delete_vm(self, vm_num: str):
        try:
            vm_name = self._get_vm_name(vm_num)
            self._oc.delete_vm_sync(yaml=self._get_vm_yaml(vm_num), vm_name=vm_name)
        except Exception as err:
            self.save_error_logs()
            raise err

    def _upload_results(self, vm_count: int):
        for vm_num in range(vm_count):
            vm_name = self._get_vm_name(str(vm_num))
            local_result_json = os.path.join(self._run_artifacts_path, f'{vm_name}.json')
            if not os.path.exists(local_result_json):
                logger.warning(f'No results file for {vm_name}')
                continue
            try:
                with open(local_result_json, 'r') as f:
                    result = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f'Failed to read results for {vm_name}')
                continue
            self._upload_to_elasticsearch(index=self._es_index, kind=self._kind,
                                          status='complete', result=result)
        self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    def run(self):
        try:
            logger.info(f'Running {self._workload} workload uuid={self._uuid} run_type={self._run_type} scale={self._scale}')
            if self._run_type in ('test_ci', 'chaos_ci', 'func_ci'):
                self._es_index = f"winstress-{self._run_type.replace('_', '-')}-results"
            else:
                self._es_index = 'winstress-results'
            self._name = self._workload
            self._workload_name = self._workload.replace('_', '-')
            self._vm_name = f'{self._workload_name}-{self._trunc_uuid}'
            self._kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'

            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))

            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'windows_dv.yaml'))
            self._oc.wait_for_dv_status(status='Succeeded')

            if self._scale:
                vm_count = self._scale * len(self._scale_node_list)
                threads_limit = self._threads_limit
                bulk_sleep = self._bulk_sleep_time
            else:
                vm_count = 1
                threads_limit = 1
                bulk_sleep = 0

            bulks = tuple(self.split_run_bulks(iterable=range(vm_count), limit=threads_limit))

            steps = [self._create_vm, self._prepare_vm, self._run_stress, self._collect_results]
            if self._delete_all:
                steps.append(self._delete_vm)
            self._run_parallel_phases(steps, bulks, bulk_sleep)

            if self._es_host:
                self._upload_results(vm_count)

            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'windows_dv.yaml'))
                self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            raise err
        except Exception as err:
            self.save_error_logs()
            raise err
