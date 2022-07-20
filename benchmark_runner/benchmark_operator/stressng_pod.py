
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class StressngPod(BenchmarkOperatorWorkloadsOperations):
    """
    This class for stressng workload
    """
    def __init__(self):
        """
        All inherit from WorkloadsOperations
        """
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''

    @logger_time_stamp
    def run(self):
        """
        This method run stressng workload
        :return:
        """
        try:
            if 'kata' in self._workload:
                self.__kind = 'kata'
                self.__name = self._workload.replace('kata', 'pod')
            else:
                self.__kind = 'pod'
                self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=f'{self.__workload_name}-workload')
            self._oc.wait_for_initialized(label='app=stressng_workload', workload=self.__workload_name)
            self._oc.wait_for_ready(label='app=stressng_workload', workload=self.__workload_name)
            self.__status = self._oc.wait_for_pod_completed(label='app=stressng_workload', workload=self.__workload_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics']:
                self.system_metrics_collector(workload=self.__workload_name)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name)
            if self._es_host:
                # verify that data upload to elastic search according to unique uuid
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                pod_name=f'{self.__workload_name}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                                           pod_name=f'{self.__workload_name}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._oc._is_pod_exist(pod_name='benchmark-controller-manager'):
                self._create_pod_log(label='benchmark-controller-manager')
            if self._oc._is_pod_exist(pod_name=self.__workload_name):
                self._create_pod_log(label=self.__workload_name)
            run_artifacts_url = os.path.join(self._environment_variables_dict.get('run_artifacts_url', ''), f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name), timeout=3)
                if ids:
                    for id in ids:
                        self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
                else:
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, uuid=self._uuid)
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                                           pod_name=f'{self.__workload_name}-workload')
            raise err
