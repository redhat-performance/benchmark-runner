
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class HammerdbPod(BenchmarkOperatorWorkloadsOperations):
    """
    This class for uperf workload
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
        This method run hammerdb workload
        :return:
        """
        try:
            self.__name = f"{self._workload.split('_')[0]}_{self._workload.split('_')[1]}"
            self.__database = self._workload.split('_')[2]
            if 'kata' in self._workload:
                self.__kind = 'kata'
                self.__name = self.__name.replace('kata', 'pod')
            else:
                self.__kind = 'pod'
            self.__workload_name = f"{self._workload.split('_')[0]}-{self._workload.split('_')[1]}"
            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            # database
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__database}.yaml'), pod_name=self.__database, namespace=f'{self.__database}-db')
            self._oc.wait_for_initialized(label=f'app={self.__database}', workload=self.__database, namespace=f'{self.__database}-db', label_uuid=False)
            self._oc.wait_for_ready(label=f'app={self.__database}', workload=self.__database, namespace=f'{self.__database}-db', label_uuid=False)
            # hammerdb
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{self.__database}.yaml'), pod_name=f'{self.__workload_name}-creator')
            # hammerdb creator
            self._oc.wait_for_pod_create(pod_name=f'{self.__workload_name}-creator')
            self._oc.wait_for_initialized(label='app=hammerdb_creator', workload=self.__workload_name)
            self._oc.wait_for_ready(label='app=hammerdb_creator', workload=self.__workload_name)
            self._oc.wait_for_pod_completed(label='app=hammerdb_creator', workload=self.__workload_name)
            # hammerdb workload
            self._oc.wait_for_pod_create(pod_name=f'{self.__workload_name}-workload')
            self._oc.wait_for_initialized(label='app=hammerdb_workload', workload=self.__workload_name)
            self._oc.wait_for_ready(label='app=hammerdb_workload', workload=self.__workload_name)
            self.__status = self._oc.wait_for_pod_completed(label='app=hammerdb_workload', workload=self.__workload_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics']:
                self.system_metrics_collector(workload=self.__workload_name, es_fetch_min_time=self.__es_fetch_min_time)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[f'{self.__workload_name}-creator', f'{self.__workload_name}-workload'], database=self.__database)
            if self._es_host:
                # verify that data upload to elastic search
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name), es_fetch_min_time=self.__es_fetch_min_time)
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, database=self.__database, status=self.__status, run_artifacts_url=run_artifacts_url)
            # delete hammerdb
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}',  f'{self.__name}_{self.__database}.yaml'),
                pod_name=f'{self.__workload_name}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__database}.yaml'),
                                     pod_name=self.__database,
                                     namespace=f'{self.__database}-db')
        except ElasticSearchDataNotUploaded as err:
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}',  f'{self.__name}_{self.__database}.yaml'),
                                           pod_name=f'{self.__workload_name}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__database}.yaml'), pod_name=self.__database,
                                     namespace=f'{self.__database}-db')
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._oc.pod_exists(pod_name='benchmark-controller-manager'):
                self._create_pod_log(label='benchmark-controller-manager')
            if self._oc.pod_exists(pod_name=self.__database, namespace=f'{self.__database}-db'):
                self._create_pod_log(database=self.__database)
            if self._oc.pod_exists(pod_name=f'{self.__workload_name}-creator'):
                self._create_pod_log(label=f'{self.__workload_name}-creator')
            if self._oc.pod_exists(pod_name=f'{self.__workload_name}-workload'):
                self._create_pod_log(label=f'{self.__workload_name}-workload')
            full_name = f'{self.__workload_name}-{self.__database}'
            run_artifacts_url = os.path.join(self._environment_variables_dict.get('run_artifacts_url', ''), f'{self._get_run_artifacts_hierarchy(workload_name=full_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name), timeout=3)
                if ids:
                    for id in ids:
                        self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
                else:
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, database=self.__database, uuid=self._uuid)
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}',  f'{self.__name}_{self.__database}.yaml'),
                                           pod_name=f'{self.__workload_name}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__database}.yaml'), pod_name=self.__database,
                                     namespace=f'{self.__database}-db')
            raise err
