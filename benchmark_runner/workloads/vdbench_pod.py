
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class VdbenchPod(WorkloadsOperations):
    """
    This class run vdbench pod
    """
    def __init__(self):
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
        This method run the workload
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
            result_list = self._create_pod_run_artifacts(pod_name=self.__pod_name)
            if self._es_host:
                # upload several run results
                for result in result_list:
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
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
            result_list = self._create_pod_run_artifacts(pod_name=self.__pod_name)
            # upload several run results
            for result in result_list:
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=result)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=self.__pod_name)
            raise err