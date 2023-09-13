
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.bootstorm_vm import BootstormVM


class WindowsVM(BootstormVM):
    """
    This class runs Windows vm
    """
    def __init__(self):
        super().__init__()

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self._initialize_run()
            if self._run_type == 'test_ci':
                self._es_index = 'windows-test-ci-results'
            else:
                self._es_index = 'windows-results'
            # create windows dv
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'windows_dv.yaml'))
            self._oc.wait_for_dv_status(status='Succeeded')
            if not self._scale:
                self._run_vm()
            # scale
            else:
                # create run bulks
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)), limit=self._threads_limit))
                # create, run and delete vms
                for target in (self._create_vm_scale, self._run_vm_scale, self._stop_vm_scale, self._wait_for_stop_vm_scale, self._delete_vm_scale, self._wait_for_delete_vm_scale):
                    proc = []
                    for bulk in bulks:
                        for vm_num in bulk:
                            p = Process(target=target, args=(str(vm_num),))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
                        # sleep between bulks
                        time.sleep(self._bulk_sleep_time)
                        proc = []
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
