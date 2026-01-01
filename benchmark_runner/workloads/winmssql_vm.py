
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

    def wait_for_windows_hammerdb_finished(self):
        """
        Wait until the Windows HammerDB workload finishes by checking the 'status' key in Elasticsearch
        and verifying that data is not already updated by checking key data_updated.
        Returns:
            True if the workload succeeded.
        Raises:
            Windows_HammerDB_NOT_Succeeded: If the workload did not succeed within the timeout.
        """
        current_wait_time = 0

        while True:
            response = self._get_latest_resource_with_key(index=self._es_index, key='status')
            # Verify that winmssl elasticsearch data is uploaded by checking 'status', 'vm_os_version'
            # Checking that this is the latest data by verify that 'data_updated' is not True
            if response.get('status') == 'Succeeded' and response.get('vm_os_version') == 'winmssql2022' and str(response.get('data_updated', '')).lower() != 'true':
                return True
            else:
                logger.info('Waiting for the Windows HammerDB run to finish successfully...')

            # check timeout
            if self._timeout > 0 and current_wait_time >= self._timeout:
                break

            # sleep before next check
            time.sleep(OC.DELAY)
            current_wait_time += OC.DELAY

        raise Windows_HammerDB_NOT_Succeeded(
            f"HammerDB did not succeed within {self._timeout} seconds"
        )

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
            # create windows dv
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'windows_dv.yaml'))
            self._oc.wait_for_dv_status(status='Succeeded')
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'))
            self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}', status=VMStatus.Stopped)
            self._set_bootstorm_vm_first_run_time()
            self._set_bootstorm_vm_start_time(vm_name=self._vm_name)
            self._virtctl.start_vm_sync(vm_name=self._vm_name)
            self._data_dict = self._get_bootstorm_vm_elapsed_time(vm_name=self._vm_name, vm_node='')
            self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            self.wait_for_windows_hammerdb_finished()
            ids = self._get_index_ids_between_dates(index=self._es_index)
            # Adding data_updated=True to stamp that this data is already updated and enrich with new product versions fields
            for id in ids:
                self._update_elasticsearch_index(index=self._es_index, id=id, kind='vm', status='Succeeded', run_artifacts_url=self._data_dict['run_artifacts_url'], database='mssql', vm_name=f'{self._workload_name}-{self._trunc_uuid}', data_updated=True)
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
