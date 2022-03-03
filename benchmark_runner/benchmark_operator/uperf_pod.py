
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class UperfPod(BenchmarkOperatorWorkloadsOperations):
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
    def uperf_pod(self, name: str = ''):
        """
        This method run uperf workload
        :return:
        """
        try:
            if name == '':
                name = self.uperf_pod.__name__
            self.__workload = name.replace('_', '-')
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-server')
            # uperf server
            server_name = self._environment_variables_dict.get('pin_node1', '')
            if server_name:
                # uperf server name is limited up to 27 chars
                if len(server_name) > 27:
                    server_name = server_name[:28]
                label = f'app=uperf-bench-server-{server_name}-0'
                self._oc.wait_for_initialized(label=label, workload=self.__workload)
                self._oc.wait_for_ready(label=label, workload=self.__workload)
            # in case that no pin node
            else:
                label = f'benchmark-operator-workload=uperf'
                self._oc.wait_for_initialized(label=label, workload=self.__workload, label_uuid=False)
                self._oc.wait_for_ready(label=label, workload=self.__workload, label_uuid=False)
            # uperf client
            self._oc.wait_for_pod_create(pod_name='uperf-client')
            self._oc.wait_for_initialized(label='app=uperf-bench-client', workload=self.__workload)
            self._oc.wait_for_ready(label='app=uperf-bench-client', workload=self.__workload)
            self.__status = self._oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=self.__workload)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, labels=['uperf-client', 'uperf-server'])
            if self._es_host:
                # verify that data upload to elastic search
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'),
                pod_name=f'uperf-client')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, labels=['uperf-client', 'uperf-server'])
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err