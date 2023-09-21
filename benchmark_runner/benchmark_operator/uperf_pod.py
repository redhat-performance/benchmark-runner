
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class UperfPod(BenchmarkOperatorWorkloadsOperations):
    """
    This class runs uperf workload
    """
    def __init__(self):
        """
        All inherit from BenchmarkOperatorWorkloadsOperations
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
        This method runs uperf workload
        :return:
        """
        try:
            self._prometheus_metrics_operation.init_prometheus()
            if 'kata' in self._workload:
                self.__kind = 'kata'
                self.__name = self._workload.replace('kata', 'pod')
            else:
                self.__kind = 'pod'
                self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=f'uperf-server')
            # uperf server
            server_name = self._environment_variables_dict.get('pin_node1', '')
            if server_name:
                label = f'app=uperf-bench-server-0'
                self._oc.wait_for_initialized(label=label, workload=self.__workload_name)
                self._oc.wait_for_ready(label=label, workload=self.__workload_name)
            # in case that no pin node
            else:
                label = f'benchmark-operator-workload=uperf'
                self._oc.wait_for_initialized(label=label, workload=self.__workload_name, label_uuid=False)
                self._oc.wait_for_ready(label=label, workload=self.__workload_name, label_uuid=False)
            # uperf client
            self._oc.wait_for_pod_create(pod_name='uperf-client')
            self._oc.wait_for_initialized(label='app=uperf-bench-client', workload=self.__workload_name)
            self._oc.wait_for_ready(label='app=uperf-bench-client', workload=self.__workload_name)
            self.__status = self._oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=self.__workload_name)
            self.__status = 'complete' if self.__status else 'failed'
            # prometheus queries
            self._prometheus_metrics_operation.finalize_prometheus()
            metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
            prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics']:
                self.system_metrics_collector(workload=self.__workload_name)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, labels=['uperf-client', 'uperf-server'])
            if self._es_host:
                # verify that data upload to elastic search
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status=self.__status, run_artifacts_url=run_artifacts_url, prometheus_result=prometheus_result)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                pod_name=f'uperf-client')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=f'uperf-client')
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._oc.pod_exists(pod_name='benchmark-controller-manager'):
                self._create_pod_log(label='benchmark-controller-manager')
            if self._oc.pod_exists(pod_name='uperf-server'):
                self._create_pod_log(label='uperf-server')
            if self._oc.pod_exists(pod_name='uperf-client'):
                self._create_pod_log(label='uperf-client')
            run_artifacts_url = os.path.join(self._environment_variables_dict.get('run_artifacts_url', ''), f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload_name), timeout=3)
                if ids:
                    for id in ids:
                        self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
                else:
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, uuid=self._uuid)
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=f'uperf-client')
            raise err
