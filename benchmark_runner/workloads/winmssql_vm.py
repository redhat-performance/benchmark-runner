
import os
import time
from datetime import datetime, timezone, timedelta

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

    def wait_for_windows_hammerdb_finished(self, vm_nums: int = 1):
        """
        Wait until the Windows HammerDB workload finishes by checking the 'vm' key in Elasticsearch
        and verifying that data is not already updated by checking key data_updated.

        Args:
            vm_nums: Expected number of VMs to complete (for scale support)

        Returns:
            True if the workload succeeded.

        Raises:
            Windows_HammerDB_NOT_Succeeded: If the workload did not succeed within the timeout.
        """
        current_wait_time = 0

        while True:
            # Get ALL documents in time window
            current_datetime = datetime.now(timezone.utc)
            start_datetime = current_datetime - timedelta(hours=1)
            end_datetime = current_datetime + timedelta(hours=1)

            es_data = self._es_operations.get_index_data_between_dates(
                index=self._es_index,
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )

            # Count documents with 'vm': 'Succeeded' and data_updated != True
            succeeded_count = sum(
                1 for doc in es_data
                if doc.get('_source', {}).get('vm') == 'Succeeded'
                and doc.get('_source', {}).get('vm_os_version') == 'winmssql2022'
                and str(doc.get('_source', {}).get('data_updated', '')).lower() != 'true'
            )

            logger.info(f'Found {succeeded_count}/{vm_nums} successful VMs')

            if succeeded_count >= vm_nums:
                return True

            # Check timeout
            if self._timeout > 0 and current_wait_time >= self._timeout:
                break

            # Sleep before next check
            time.sleep(OC.DELAY)
            current_wait_time += OC.DELAY

        raise Windows_HammerDB_NOT_Succeeded(
            f"Only {succeeded_count}/{vm_nums} VMs completed HammerDB successfully within {self._timeout} seconds"
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
            if not self._verification_only:
                # create windows dv
                self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'windows_dv.yaml'))
                self._oc.wait_for_dv_status(status='Succeeded')
            if self._scale:
                # Just create the vms
                self._create_vms_only = True
                self.run_vm_workload()
                self._create_vms_only = False
            else:
                self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'))
                self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}',
                                            status=VMStatus.Stopped)
                self._set_bootstorm_vm_first_run_time()
                self._set_bootstorm_vm_start_time(vm_name=self._vm_name)
                self._virtctl.start_vm_sync(vm_name=self._vm_name)
                self._data_dict = self._get_bootstorm_vm_elapsed_time(vm_name=self._vm_name, vm_node='')
            vm_count = int(self._scale)*len(self._scale_node_list) if self._scale else 1
            self.wait_for_windows_hammerdb_finished(vm_nums=vm_count)
            if self._scale:
                ids = self._get_index_ids_between_dates(index=self._es_index, key='status')
                # Adding data_updated=True to stamp that this data is already updated and enrich with new product versions fields
                self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                for id in ids:
                    self._update_elasticsearch_index(index=self._es_index, id=id, kind='vm', status='Succeeded', run_artifacts_url=self._data_dict['run_artifacts_url'], database='mssql', vm_name=f'{self._workload_name}-{self._trunc_uuid}', data_updated=True, scale=int(self._scale)*len(self._scale_node_list))
                self._only_delete_all=True
                self.run_vm_workload()
            else:
                ids = self._get_index_ids_between_dates(index=self._es_index, key='status')
                # Adding data_updated=True to stamp that this data is already updated and enrich with new product versions fields
                self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                for id in ids:
                    self._update_elasticsearch_index(index=self._es_index, id=id, kind='vm', status='Succeeded', run_artifacts_url=self._data_dict['run_artifacts_url'], database='mssql', vm_name=f'{self._workload_name}-{self._trunc_uuid}', data_updated=True)
                self._finalize_vm()
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
                    vm_name=self._vm_name)
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
