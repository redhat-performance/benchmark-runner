
import os

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class VdbenchVM(WorkloadsOperations):
    """
    This class run vdbench vm
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__vm_name = ''

    @logger_time_stamp
    def run(self):
        """
        This method run the workload
        :return:
        """
        try:
            self.__name = self._workload
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', run_type='vm', label_uuid=False)
            # Create vm log should be direct after vm is ready
            self.__vm_name = self._create_vm_log(labels=[self.__workload_name])
            self.__status = self._oc.wait_for_vm_log_completed(vm_name=self.__vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@')
            self.__status = 'complete' if self.__status else 'failed'
            # save run artifacts logs
            result_list = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.__vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@')
            if self._es_host:
                # upload several run results
                for result in result_list:
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            result_list = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.__vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@')
            # upload several run results
            for result in result_list:
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=result)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err