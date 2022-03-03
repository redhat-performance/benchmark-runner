
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
        self.__workload = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''

    @typechecked
    @logger_time_stamp
    def stressng_pod(self, name: str = ''):
        """
        This method run stressng workload
        :return:
        """
        try:
            if name == '':
                name = self.stressng_pod.__name__
            self.__workload = name.replace('_', '-')
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'), pod_name=f'{self.__workload}-workload')
            self._oc.wait_for_initialized(label='app=stressng_workload', workload=self.__workload)
            self._oc.wait_for_ready(label='app=stressng_workload', workload=self.__workload)
            self.__status = self._oc.wait_for_pod_completed(label='app=stressng_workload', workload=self.__workload)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload)
            if self._es_host:
                # verify that data upload to elastic search according to unique uuid
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'),
                pod_name=f'{self.__workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{self.__workload}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{self.__workload}-workload')
            raise err
