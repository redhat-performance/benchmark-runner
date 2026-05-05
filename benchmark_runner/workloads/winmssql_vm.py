
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.bootstorm_vm import BootstormVM
from benchmark_runner.common.oc.oc import VMStatus, OC
from benchmark_runner.workloads.workloads_exceptions import Windows_HammerDB_NOT_Succeeded


class WinMSSQLVM(BootstormVM):
    """
    This class runs Windows MSSQL VM workload with scale support.
    Same code path for 1 VM and N VMs.
    """
    def __init__(self):
        super().__init__()
        if not self._windows_url:
            raise ValueError('Missing Windows DV URL')
        self.__namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self.__username = self._environment_variables_dict.get('vm_user') or 'Administrator'
        self.__ssh_key_path = self._ssh_key_path
        self.__remote_dir = 'C:/tools/hammerdb-4.12'

    def _get_vm_name(self, vm_num: str) -> str:
        """Return the VM name for the given vm_num, handling both scale and non-scale."""
        if self._scale:
            return f'{self._workload_name}-{self._trunc_uuid}-{vm_num}'
        return f'{self._workload_name}-{self._trunc_uuid}'

    def _get_vm_yaml(self, vm_num: str) -> str:
        """Return the yaml file path for the given vm_num."""
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
        raise Windows_HammerDB_NOT_Succeeded(f'Failed to SCP {script} to VM {vm_name} after {self.SCP_RETRIES} attempts')

    def _create_vm(self, vm_num: str):
        """Phase 1: Create VM and wait for Stopped status."""
        try:
            self._oc.create_async(yaml=self._get_vm_yaml(vm_num))
            self._oc.wait_for_vm_status(vm_name=self._get_vm_name(vm_num), status=VMStatus.Stopped)
        except Exception as err:
            self.save_error_logs()
            raise err

    def _prepare_vm(self, vm_num: str):
        """Phase 2: Start VM, wait for SSH, SCP scripts, run DB preparation."""
        try:
            vm_name = self._get_vm_name(vm_num)
            self._virtctl.start_vm_sync(vm_name=vm_name)

            if not self._virtctl._wait_for_virtctl_ssh(vm_name=vm_name, namespace=self.__namespace,
                                                       key_path=self.__ssh_key_path, username=self.__username,
                                                       timeout=self._timeout):
                raise Windows_HammerDB_NOT_Succeeded(f'SSH never became ready on VM {vm_name}')

            scripts = ['run_prepare_hammerdb.ps1', 'run_hammerdb_benchmark.ps1',
                       '01_provision-data-disk.ps1', '02_create_db.sql',
                       '04_traceflags.sql', '05_hammerdb-auto-runs.ps1', '06_parse_results.ps1']
            for script in scripts:
                self._scp_to_vm_with_verify(vm_name=vm_name,
                                            local_path=os.path.join(self._run_artifacts_path, script),
                                            remote_path=f'{self.__remote_dir}/{script}')

            self._scp_to_vm_with_verify(vm_name=vm_name,
                                        local_path=os.path.join(self._run_artifacts_path, '03_buildschema_mssql.tcl'),
                                        remote_path=f'{self.__remote_dir}/scripts/tcl/mssqls/tprocc/03_buildschema_mssql.tcl')

            logger.info(f'Running run_prepare_hammerdb.ps1 on VM {vm_name} ...')
            self._virtctl.virtctl_ssh(vm_name=vm_name,
                                     command=f'powershell -NoProfile -ExecutionPolicy Bypass -File {self.__remote_dir}/run_prepare_hammerdb.ps1',
                                     namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username,
                                     timeout=self._timeout)
        except Exception as err:
            self.save_error_logs()
            raise err

    def _run_hammerdb(self, vm_num: str):
        """Phase 3: Run HammerDB benchmark (synchronized across all VMs)."""
        try:
            vm_name = self._get_vm_name(vm_num)
            logger.info(f'Running run_hammerdb_benchmark.ps1 on VM {vm_name} ...')
            self._virtctl.virtctl_ssh(vm_name=vm_name,
                                     command=f'powershell -NoProfile -ExecutionPolicy Bypass -File {self.__remote_dir}/run_hammerdb_benchmark.ps1',
                                     namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username,
                                     timeout=self._timeout)
        except Exception as err:
            self.save_error_logs()
            raise err

    def _collect_results(self, vm_num: str):
        """Phase 4: SCP results back and upload to Elasticsearch."""
        try:
            vm_name = self._get_vm_name(vm_num)

            local_result_json = os.path.join(self._run_artifacts_path, f'hammerdb_result_{vm_num}.json')
            check_cmd = f'powershell -Command "if (Test-Path \'{self.__remote_dir}/results/hammerdb_result.json\') {{ echo found }}"'
            for elapsed in range(0, self._timeout, OC.DELAY):
                check = self._virtctl.virtctl_ssh(vm_name=vm_name, command=check_cmd,
                                                  namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username,
                                                  timeout=60)
                if check and 'found' in check:
                    break
                logger.info(f'Waiting for hammerdb_result.json on VM {vm_name}... ({elapsed}s)')
                time.sleep(OC.DELAY)
            if not self._virtctl._scp_file(vm_name=vm_name, remote_path=f'{self.__remote_dir}/results/hammerdb_result.json',
                                           local_path=local_result_json,
                                           namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username):
                raise Windows_HammerDB_NOT_Succeeded(f'Failed to SCP hammerdb_result.json from VM {vm_name}')
            if not os.path.exists(local_result_json):
                raise Windows_HammerDB_NOT_Succeeded(f'hammerdb_result.json not found locally at {local_result_json}')
            logger.info(f'hammerdb_result.json copied to {local_result_json}')

            hammerdb_results_dict = self._parse_hammerdb_results_vm(local_result_json)
            if hammerdb_results_dict and self._es_host:
                for entry in hammerdb_results_dict:
                    thread_result = {
                        'vm_name': vm_name,
                        'vm_name_num': f'winmssql-vm-{vm_num}',
                        'db_type': 'mssql',
                        'db_version': self._product_versions.get('mssql', 2025) if isinstance(self._product_versions, dict) else 2025,
                        'storage_type': self._storage_type,
                        **entry,
                    }
                    self._upload_hammerdb_thread_result(
                        index=self._es_index,
                        kind=self._kind,
                        status='complete',
                        run_artifacts_url=self._data_dict.get('run_artifacts_url', ''),
                        database='mssql',
                        thread_result=thread_result,
                    )
                    self._verify_elasticsearch_data_uploaded(
                        index=self._es_index,
                        uuid=self._uuid,
                    )
            else:
                logger.warning(f'HammerDB results could not be parsed from {local_result_json}')

            local_log_file = os.path.join(self._run_artifacts_path, f'run_hammerdb_benchmark_{vm_num}.log')
            if self._virtctl._scp_file(vm_name=vm_name, remote_path=f'{self.__remote_dir}/run_hammerdb_benchmark.log',
                                       local_path=local_log_file,
                                       namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username):
                logger.info(f'run_hammerdb_benchmark.log copied to {local_log_file}')
            else:
                logger.warning(f'Failed to SCP run_hammerdb_benchmark.log from VM {vm_name}')

            local_prepare_log = os.path.join(self._run_artifacts_path, f'run_prepare_hammerdb_{vm_num}.log')
            if self._virtctl._scp_file(vm_name=vm_name, remote_path=f'{self.__remote_dir}/run_prepare_hammerdb.log',
                                       local_path=local_prepare_log,
                                       namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username):
                logger.info(f'run_prepare_hammerdb.log copied to {local_prepare_log}')
            else:
                logger.warning(f'Failed to SCP run_prepare_hammerdb.log from VM {vm_name}')
        except Exception as err:
            self.save_error_logs()
            raise err

    def _delete_vm(self, vm_num: str):
        """Phase 5: Delete VM."""
        try:
            vm_name = self._get_vm_name(vm_num)
            self._oc.delete_vm_sync(yaml=self._get_vm_yaml(vm_num), vm_name=vm_name)
        except Exception as err:
            self.save_error_logs()
            raise err

    def save_error_logs(self):
        """Upload error logs to Elasticsearch."""
        if self._es_host:
            self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status='failed', result=self._data_dict)
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    @logger_time_stamp
    def run(self):
        """
        Run the winmssql VM workload. Same flow for 1 VM and N VMs.
        """
        try:
            if self._run_type in ('test_ci', 'chaos_ci', 'func_ci'):
                self._es_index = f"hammerdb-{self._run_type.replace('_', '-')}-results"
            else:
                self._es_index = 'hammerdb-results'
            self._initialize_run()
            self._set_bootstorm_vm_first_run_time()

            # create windows dv
            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'windows_dv.yaml'))
            self._oc.wait_for_dv_status(status='Succeeded')

            self._data_dict = {}
            self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')

            # Determine VM count
            if self._scale:
                vm_count = self._scale * len(self._scale_node_list)
                threads_limit = self._threads_limit
                bulk_sleep = self._bulk_sleep_time
            else:
                vm_count = 1
                threads_limit = 1
                bulk_sleep = 0

            bulks = tuple(self.split_run_bulks(iterable=range(vm_count), limit=threads_limit))

            # Run all phases sequentially; each phase runs across all VMs in parallel
            steps = (self._create_vm, self._prepare_vm, self._run_hammerdb,
                     self._collect_results, self._delete_vm)
            for target in steps:
                proc = []
                for bulk in bulks:
                    for vm_num in bulk:
                        p = Process(target=target, args=(str(vm_num),))
                        p.start()
                        proc.append(p)
                    for p in proc:
                        p.join()
                    time.sleep(bulk_sleep)
                    proc = []

            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'windows_dv.yaml'))
                self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            raise err
        except Exception as err:
            self.save_error_logs()
            raise err
