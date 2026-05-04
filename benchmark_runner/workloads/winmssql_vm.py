
import os
import time

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.bootstorm_vm import BootstormVM
from benchmark_runner.common.oc.oc import VMStatus, OC
from benchmark_runner.workloads.workloads_exceptions import Windows_HammerDB_NOT_Succeeded


class WinMSSQLVM(BootstormVM):
    """
    This class runs Windows vm
    """
    def __init__(self):
        super().__init__()
        if not self._windows_url:
            raise ValueError('Missing Windows DV URL')
        self.__namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self.__username = self._environment_variables_dict.get('vm_user') or 'Administrator'
        self.__ssh_key_path = self._ssh_key_path
        self.__remote_dir = 'C:/tools/hammerdb-4.12'


    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            if self._run_type in ('test_ci', 'chaos_ci', 'func_ci'):
                self._es_index = f"hammerdb-{self._run_type.replace('_', '-')}-results"
            else:
                self._es_index = 'hammerdb-results'
            self._initialize_run()
            self._set_bootstorm_vm_first_run_time()
            # create windows dv
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'windows_dv.yaml'))
            self._oc.wait_for_dv_status(status='Succeeded')
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'))
            self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}', status=VMStatus.Stopped)
            self._virtctl.start_vm_sync(vm_name=self._vm_name)
            self._data_dict = {}
            self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')

            # SSH key is injected via cloudInitNoCloud at boot
            if not self._virtctl._wait_for_virtctl_ssh(vm_name=self._vm_name, namespace=self.__namespace,
                                                       key_path=self.__ssh_key_path, username=self.__username,
                                                       timeout=self._timeout):
                raise Windows_HammerDB_NOT_Succeeded('SSH never became ready on VM')

            # SCP all scripts to the VM
            scripts = ['run_main_hammerdb.ps1', '01_provision-data-disk.ps1',
                       '02_create_db.sql', '04_traceflags.sql',
                       '05_hammerdb-auto-runs.ps1', '06_parse_results.ps1']
            for script in scripts:
                script_path = os.path.join(self._run_artifacts_path, script)
                if not self._virtctl._scp_to_vm(vm_name=self._vm_name, local_path=script_path,
                                                remote_path=f'{self.__remote_dir}/{script}',
                                                namespace=self.__namespace, key_path=self.__ssh_key_path,
                                                username=self.__username):
                    raise Windows_HammerDB_NOT_Succeeded(f'Failed to SCP required script {script} to VM')
                logger.info(f'Copied {script} to VM')

            # SCP buildschema tcl to HammerDB scripts path
            buildschema_script = '03_buildschema_mssql.tcl'
            script_path = os.path.join(self._run_artifacts_path, buildschema_script)
            if not self._virtctl._scp_to_vm(vm_name=self._vm_name, local_path=script_path,
                                            remote_path=f'{self.__remote_dir}/scripts/tcl/mssqls/tprocc/{buildschema_script}',
                                            namespace=self.__namespace, key_path=self.__ssh_key_path,
                                            username=self.__username):
                logger.warning(f'Failed to SCP {buildschema_script} to VM')
            else:
                logger.info(f'Copied {buildschema_script} to VM at scripts/tcl/mssqls/tprocc/')

            # Run main script (rebuild DB + run HammerDB workload)
            logger.info('Running run_main_hammerdb.ps1 inside Windows VM ...')
            self._virtctl.virtctl_ssh(vm_name=self._vm_name,
                                     command=f'powershell -NoProfile -ExecutionPolicy Bypass -File {self.__remote_dir}/run_main_hammerdb.ps1',
                                     namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username,
                                     timeout=self._timeout)

            # SCP results back
            local_result_json = os.path.join(self._run_artifacts_path, 'hammerdb_result.json')
            check_cmd = f'powershell -Command "if (Test-Path \'{self.__remote_dir}/results/hammerdb_result.json\') {{ echo found }}"'
            for elapsed in range(0, self._timeout, OC.DELAY):
                check = self._virtctl.virtctl_ssh(vm_name=self._vm_name, command=check_cmd,
                                                  namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username)
                if check and 'found' in check:
                    break
                logger.info(f'Waiting for hammerdb_result.json on VM... ({elapsed}s)')
                time.sleep(OC.DELAY)
            if self._virtctl._scp_file(vm_name=self._vm_name, remote_path=f'{self.__remote_dir}/results/hammerdb_result.json',
                                       local_path=local_result_json,
                                       namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username):
                logger.info(f'hammerdb_result.json copied to {local_result_json}')
            else:
                logger.warning(f'Failed to SCP hammerdb_result.json from VM')

            # Upload per-thread results to Elasticsearch
            hammerdb_results_dict = self._parse_hammerdb_results_vm(local_result_json)
            if hammerdb_results_dict and self._es_host:
                for entry in hammerdb_results_dict:
                    thread_result = {
                        'vm_name': f'{self._workload_name}-{self._trunc_uuid}',
                        'db_type': 'mssql',
                        'db_version': self._product_versions.get('mssql', 2025) if isinstance(self._product_versions, dict) else 2025,
                        'storage_type': self._storage_type,
                        **entry,
                    }
                    self._upload_hammerdb_thread_result(
                        index=self._es_index,
                        kind=self._kind,
                        status='complete',
                        run_artifacts_url=self._data_dict['run_artifacts_url'],
                        database='mssql',
                        thread_result=thread_result,
                    )
                    self._verify_elasticsearch_data_uploaded(
                        index=self._es_index,
                        uuid=self._uuid,
                    )
            else:
                logger.warning('HammerDB results could not be parsed from %s', local_result_json)

            # SCP run log back
            local_log_file = os.path.join(self._run_artifacts_path, 'run_main_hammerdb.log')
            if self._virtctl._scp_file(vm_name=self._vm_name, remote_path=f'{self.__remote_dir}/run_main_hammerdb.log',
                                       local_path=local_log_file,
                                       namespace=self.__namespace, key_path=self.__ssh_key_path, username=self.__username):
                logger.info(f'run_main_hammerdb.log copied to {local_log_file}')
            else:
                logger.warning(f'Failed to SCP run_main_hammerdb.log from VM')

            self._finalize_vm()
            if self._delete_all:
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
                    vm_name=self._vm_name)
            if self._delete_all:
                # delete windows dv
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'windows_dv.yaml'))
                # delete namespace
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
                vm_name=self._vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._es_host:
                self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status='failed', result=self._data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)
            raise err
