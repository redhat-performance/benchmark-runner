
import os

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class StressngVM(BenchmarkOperatorWorkloadsOperations):
    """
    This class for stressng vm workload
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
        This method run stressng vm workload
        :return:
        """
        try:
            self.__name = self._workload
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'
            self.__workload_name = self._workload.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=f'{self.__workload_name}-workload')
            self._oc.wait_for_initialized(label='app=stressng_workload', workload=self.__workload_name)
            self._oc.wait_for_ready(label='app=stressng_workload', workload=self.__workload_name)
            # Create vm log should be direct after vm is ready
            vm_name = self._create_vm_log(labels=[self.__workload_name])
            self.__status = self._oc.wait_for_vm_completed(workload=self.__workload_name, vm_name=vm_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload_name)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, pod=False)
            # verify that data upload to elastic search
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self._environment_variables_dict.get('kind', ''), status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=f'{self.__workload_name}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                                          vm_name=f'{self.__workload_name}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, pod=False)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self._environment_variables_dict.get('kind', ''), status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                                          vm_name=f'{self.__workload_name}-workload')
            raise err