
import json
import os
import time

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.bootstorm_vm import BootstormVM
from benchmark_runner.common.oc.oc import VMStatus, OC


class WinfioVM(BootstormVM):
    """
    This class runs Windows FIO VM workload.
    Same code path for 1 VM and N VMs.
    """
    def __init__(self):
        super().__init__()
        if not self._windows_url:
            raise ValueError('Missing Windows DV URL')
        self.__namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self.__username = self._environment_variables_dict.get('vm_user') or 'Administrator'
        self.__ssh_key_path = self._ssh_key_path
        self.__remote_dir = 'C:/tools/fio'

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

            scripts = ['01_provision-data-disk.ps1', '02_run_fio_benchmark.ps1', '03_parse_fio_results.ps1']
            for script in scripts:
                self._scp_to_vm_with_verify(vm_name=vm_name,
                                            local_path=os.path.join(self._run_artifacts_path, script),
                                            remote_path=f'{self.__remote_dir}/{script}')
            logger.info(f'Running 01_provision-data-disk.ps1 on VM {vm_name} ...')
            self._virtctl.virtctl_ssh(vm_name=vm_name,
                                     command=f'powershell -NoProfile -ExecutionPolicy Bypass -File {self.__remote_dir}/01_provision-data-disk.ps1 -DiskID 1',
                                     namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username)
        except Exception as err:
            logger.warning(f'Failed to prepare VM {self._get_vm_name(vm_num)}: {err}')


    def _run_fio(self, vm_num: str):
        try:
            vm_name = self._get_vm_name(vm_num)
            logger.info(f'Running 02_run_fio_benchmark.ps1 on VM {vm_name} ...')
            self._virtctl.virtctl_ssh(vm_name=vm_name,
                                     command=f'powershell -NoProfile -ExecutionPolicy Bypass -File {self.__remote_dir}/02_run_fio_benchmark.ps1',
                                     namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username,
                                     timeout=self._timeout)
        except Exception as err:
            logger.warning(f'FIO failed on VM {self._get_vm_name(vm_num)}: {err}')

    def _collect_results(self, vm_num: str):
        try:
            vm_name = self._get_vm_name(vm_num)
            local_result_json = os.path.join(self._run_artifacts_path, f'{vm_name}.json')

            check_cmd = f'powershell -Command "if (Test-Path \'{self.__remote_dir}/results/fio_summary.json\') {{ echo found }}"'
            for elapsed in range(0, self._timeout, OC.DELAY):
                check = self._virtctl.virtctl_ssh(vm_name=vm_name, command=check_cmd,
                                                  namespace=self.__namespace, key_path=self.__ssh_key_path,
                                                  username=self.__username, timeout=60)
                if check and 'found' in check:
                    break
                logger.info(f'Waiting for fio_summary.json on VM {vm_name}... ({elapsed}s)')
                time.sleep(OC.DELAY)

            local_log_file = os.path.join(self._run_artifacts_path, f'run_fio_benchmark_{vm_num}.log')
            if self._virtctl._scp_file(vm_name=vm_name,
                                       remote_path=f'{self.__remote_dir}/run_fio_benchmark.log',
                                       local_path=local_log_file,
                                       namespace=self.__namespace, key_path=self.__ssh_key_path,
                                       username=self.__username):
                logger.info(f'run_fio_benchmark.log copied to {local_log_file}')
            else:
                logger.warning(f'Failed to SCP run_fio_benchmark.log from VM {vm_name}')

            if not self._virtctl._scp_file(vm_name=vm_name,
                                           remote_path=f'{self.__remote_dir}/results/fio_summary.json',
                                           local_path=local_result_json,
                                           namespace=self.__namespace, key_path=self.__ssh_key_path,
                                           username=self.__username):
                logger.warning(f'Failed to SCP fio_summary.json from VM {vm_name}')
                return

            try:
                with open(local_result_json, 'r') as f:
                    summary = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f'Failed to parse FIO summary from {local_result_json}: {e}')
                return

            vm_node = self._oc.get_vm_node(vm_name=vm_name) or ''
            workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
            workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
            run_artifacts_url = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')

            result_list = []
            for block_size, ops in summary.items():
                for io_operation, metrics in ops.items():
                    result = {
                        'block_size': block_size,
                        'io_operation': io_operation,
                        'total_iops': metrics.get('TotalIOPS', 0),
                        'total_bw_kbs': metrics.get('TotalBW_KBs', 0),
                        'lat_avg_usec': metrics.get('LatAvg_usec', 0),
                        'lat_p99_usec': metrics.get('LatP99_usec', 0),
                        'vm_name': vm_name,
                        'node': vm_node,
                        'run_artifacts_url': run_artifacts_url,
                    }
                    result_list.append(result)

            with open(local_result_json, 'w') as f:
                json.dump(result_list, f, indent=2)
            logger.info(f'FIO results saved to {local_result_json}')

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
                    result_list = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f'Failed to read results for {vm_name}')
                continue
            for result in result_list:
                self._upload_to_elasticsearch(index=self._es_index, kind=self._kind,
                                              status='complete', result=result)
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    def run(self):
        try:
            logger.info(f'Running {self._workload} workload uuid={self._uuid} run_type={self._run_type} scale={self._scale}')
            if self._run_type in ('test_ci', 'chaos_ci', 'func_ci'):
                self._es_index = f"fio-{self._run_type.replace('_', '-')}-results"
            else:
                self._es_index = 'fio-results'
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

            steps = [self._create_vm, self._prepare_vm, self._run_fio, self._collect_results]
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
