
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
    def hammerdb_pod(self, database: str, name: str = ''):
        """
        This method run hammerdb workload
        :return:
        """
        try:
            if name == '':
                name = self.hammerdb_pod.__name__
            self.__workload = name.replace('_', '-')
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            # database
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'), pod_name=database, namespace=f'{database}-db')
            self._oc.wait_for_initialized(label=f'app={database}', workload=database, namespace=f'{database}-db', label_uuid=False)
            self._oc.wait_for_ready(label=f'app={database}', workload=database, namespace=f'{database}-db', label_uuid=False)
            # hammerdb
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'), pod_name=f'{self.__workload}-creator')
            # hammerdb creator
            self._oc.wait_for_pod_create(pod_name=f'{self.__workload}-creator')
            self._oc.wait_for_initialized(label='app=hammerdb_creator', workload=self.__workload)
            self._oc.wait_for_ready(label='app=hammerdb_creator', workload=self.__workload)
            self._oc.wait_for_pod_completed(label='app=hammerdb_creator', workload=self.__workload)
            # hammerdb workload
            self._oc.wait_for_pod_create(pod_name=f'{self.__workload}-workload')
            self._oc.wait_for_initialized(label='app=hammerdb_workload', workload=self.__workload)
            self._oc.wait_for_ready(label='app=hammerdb_workload', workload=self.__workload)
            self.__status = self._oc.wait_for_pod_completed(label='app=hammerdb_workload', workload=self.__workload)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[f'{self.__workload}-creator', f'{self.__workload}-workload'], database=database)
            if self._es_host:
                # verify that data upload to elastic search
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, database=database, status=self.__status, run_artifacts_url=run_artifacts_url)
            # delete hammerdb
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                pod_name=f'{self.__workload}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'),
                                     pod_name=database,
                                     namespace=f'{database}-db')
        except ElasticSearchDataNotUploaded as err:
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{self.__workload}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'), pod_name=database,
                                     namespace=f'{database}-db')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[f'{self.__workload}-creator', f'{self.__workload}-workload'], database=database)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, database=database)
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{self.__workload}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'), pod_name=database,
                                     namespace=f'{database}-db')
            raise err