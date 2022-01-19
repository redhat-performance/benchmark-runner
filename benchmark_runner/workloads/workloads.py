
import os

from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class Workloads(WorkloadsOperations):
    """
    This class create workload
    """
    def __init__(self):
        """
        All inherit from WorkloadsOperations
        """
        super().__init__()
        self.__workload = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__vm_name = ''

    @typechecked
    @logger_time_stamp
    def vdbench_pod(self, name: str = ''):
        """
    This method run vdbench pog workload
    :return:
    """
        try:
            if name == '':
                name = self.vdbench_pod.__name__
            self.__workload = name.replace('_', '-')
            self.__pod_name = f'{self.__workload}-{self._trunc_uuid}'
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'
            self._environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'), pod_name=self.__pod_name)
            self._oc.wait_for_initialized(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False)
            self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False)
            self.__status = self._oc.wait_for_pod_completed(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False, job=False)
            self.__status = 'complete' if self.__status else 'failed'
            # save run artifacts logs
            result = self._create_pod_run_artifacts(pod_name=self.__pod_name)
            if self._es_host:
                self._upload_to_es(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                # verify that data upload to elastic search according to unique uuid
                self._verify_es_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=self.__pod_name)
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=self.__pod_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            result = self._create_pod_run_artifacts(pod_name=self.__pod_name)
            self._upload_to_es(kind=self.__kind, status='failed', result=result)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=self.__pod_name)
            raise err

    @logger_time_stamp
    def vdbench_kata(self):
        """
        This method run vdbench kata workload
        :return:
        """
        self.vdbench_pod(self.vdbench_kata.__name__)

    @logger_time_stamp
    def vdbench_vm(self):
        """
        This method run vdbench vm workload
        :return:
        """
        try:
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'

            self.__workload = self.vdbench_vm.__name__.replace('_', '-')
            self.__vm_name = f'{self.__workload}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_vm.__name__}.yaml'), vm_name=self.__vm_name)
            self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', run_type='vm', label_uuid=False)
            # Create vm log should be direct after vm is ready
            self.__vm_name = self._create_vm_log(labels=[self.__workload])
            self.__status = self._oc.wait_for_vm_log_completed(vm_name=self.__vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@')
            self.__status = 'complete' if self.__status else 'failed'
            # save run artifacts logs
            result = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.__vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@')
            if self._es_host:
                self._upload_to_es(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                # verify that data upload to elastic search according to unique uuid
                self._verify_es_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_vm.__name__}.yaml'),
                vm_name=self.__vm_name)
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_vm.__name__}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            result = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.__vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@')
            self._upload_to_es(kind=self.__kind, status='failed', result=result)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_vm.__name__}.yaml'),
                vm_name=self.__vm_name)
            raise err

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """
        self.initialize_workload()
        workloads = Workloads()
        class_method = getattr(workloads, self._workload)
        class_method()
        self.finalize_workload()



