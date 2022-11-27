
import os

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class HammerdbVM(BenchmarkOperatorWorkloadsOperations):
    """
    This class for hammerdb vm workload
    """
    ES_FETCH_TIME = 30

    def __init__(self):
        """
        All inherit from WorkloadsOperations
        """
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__database = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__es_fetch_min_time = self.ES_FETCH_TIME if self._run_type == 'perf_ci' else None

    @logger_time_stamp
    def run(self):
        """
        This method run hammerdb vm workload
        :return:
        """
        try:
            self.__name = f"{self._workload.split('_')[0]}_{self._workload.split('_')[1]}"
            self.__database = self._workload.split('_')[2]
            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'
            self.__workload_name = self.__name.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{self.__database}.yaml'), vm_name=f'{self.__workload_name}-workload')
            # hammerdb workload and database
            self._oc.wait_for_vm_creation(vm_name=f'{self.__workload_name}-workload')
            self._oc.wait_for_initialized(label='app=hammerdb_workload', workload=self.__workload_name)
            self._oc.wait_for_ready(label='app=hammerdb_workload', workload=self.__workload_name)
            # Create vm log should be direct after vm is ready
            vm_name = self._create_vm_log(labels=[self.__workload_name])
            self.__status = self._oc.wait_for_vm_completed(workload=self.__workload_name, vm_name=vm_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics']:
                self.system_metrics_collector(workload=self.__workload_name, es_fetch_min_time=self.__es_fetch_min_time)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, pod=False)
            # verify that data upload to elastic search
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name), es_fetch_min_time=self.__es_fetch_min_time)
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self._environment_variables_dict.get('kind', ''), status=self.__status, run_artifacts_url=run_artifacts_url, database=self.__database)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{self.__database}.yaml'),
                vm_name=f'{self.__workload_name}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{self.__database}.yaml'),
                                          vm_name=f'{self.__workload_name}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._oc.pod_exists(pod_name='benchmark-controller-manager'):
                self._create_pod_log(label='benchmark-controller-manager')
            full_name = f'{self.__workload_name}-{self.__database}'
            run_artifacts_url = os.path.join(self._environment_variables_dict.get('run_artifacts_url', ''), f'{self._get_run_artifacts_hierarchy(workload_name=full_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name), timeout=3)
                if ids:
                    for id in ids:
                        self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, database=self.__database)
                else:
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, database=self.__database, uuid=self._uuid)
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            # delete hammerdb
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{self.__database}.yaml'),
                                          vm_name=f'{self.__workload_name}-workload')
            raise err
