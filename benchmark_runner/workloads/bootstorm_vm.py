
import os
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations
from benchmark_runner.common.oc.oc import VMStatus


class BootstormVM(WorkloadsOperations):
    """
    This class run bootstorm vm
    """
    START_STAMP = '@@~@@START-WORKLOAD@@~@@'
    END_STAMP = '@@~@@END-WORKLOAD@@~@@'

    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__vm_name = ''
        self.__data_dict = {}

    def __create_vm_scale(self, vm_num: str):
        """
        This method creates vms in parallel
        """
        self._oc._create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))
        self._oc.wait_for_vm_status(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}', status=VMStatus.Stopped)

    def __run_vm_scale(self, vm_num: str):
        """
        This method runs vms in parallel
        """
        vm_name = f'bootstorm-vm-{self._trunc_uuid}-{vm_num}'
        self.set_bootstorm_vm_start_time(vm_name=vm_name)
        self._virtctl.start_vm_sync(vm_name=vm_name)
        self.__data_dict = self.get_bootstorm_vm_elapse_time(vm_name=vm_name)
        self.__status = 'complete' if self.__data_dict else 'failed'
        if self._es_host:
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=self.__data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def __delete_vm_scale(self, vm_num: str):
        """
        This method deletes vms in parallel
        """
        vm_name = f'bootstorm-vm-{self._trunc_uuid}-{vm_num}'
        self._oc.delete_vm_sync(
            yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'),
            vm_name=vm_name)

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self.__name = self._workload
            if self._run_type == 'test_ci':
                self.__es_index = 'bootstorm-test-ci-results'
            else:
                self.__es_index = 'bootstorm-results'
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            if not self._scale:
                self._oc._create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
                self._oc.wait_for_vm_status(vm_name=f'bootstorm-vm-{self._trunc_uuid}', status=VMStatus.Stopped)
                self.set_bootstorm_vm_start_time(vm_name=self.__vm_name)
                self._virtctl.start_vm_sync(vm_name=self.__vm_name)
                self.__data_dict = self.get_bootstorm_vm_elapse_time(vm_name=self.__vm_name)
                self.__status = 'complete' if self.__data_dict else 'failed'
                if self._es_host:
                    # upload several run results
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=self.__data_dict)
                    # verify that data upload to elastic search according to unique uuid
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    vm_name=self.__vm_name)
            # scale
            else:
                # create namespace
                self._oc._create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
                # create redis and state signals
                proc = []
                scale = int(self._scale)
                self.__data_dict['scale'] = scale
                for target in [self.__create_vm_scale, self.__run_vm_scale, self.__delete_vm_scale]:
                    # create vms in parallel
                    count = 0
                    for scale_node in range(len(self._scale_node_list)):
                        for scale_num in range(scale):
                            count += 1
                            p = Process(target=target, args=(str(count),))
                            p.start()
                            proc.append(p)
                    for p in proc:
                        p.join()
                # delete namespace
                self._oc._delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._es_host:
                self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=self.__data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            raise err
