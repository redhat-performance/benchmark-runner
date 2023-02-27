
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations
from benchmark_runner.common.prometheus.prometheus_metrics_operations import PrometheusMetricsOperation


class VdbenchPod(WorkloadsOperations):
    """
    This class run vdbench pod
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__scale = ''
        self.__data_dict = {}
        self.__prometheus_metrics_operation = PrometheusMetricsOperation()

    def __create_pod_scale(self, pod_num: str):
        """
        This method create pod in parallel
        """
        self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{pod_num}.yaml'))
        self._oc.wait_for_pod_create(pod_name=f'{self.__pod_name}-{pod_num}')

    def __run_pod_scale(self, pod_num: str):
        """
        This method runs pod in parallel
        """
        self._oc.wait_for_initialized(label=f'app=vdbench-{self._trunc_uuid}-{pod_num}', label_uuid=False)
        self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}-{pod_num}', label_uuid=False)
        self.__status = self._oc.wait_for_pod_completed(label=f'app=vdbench-{self._trunc_uuid}-{pod_num}', label_uuid=False, job=False)
        self.__status = 'complete' if self.__status else 'failed'
        self.__prometheus_metrics_operation.finalize_prometheus()
        metric_results = self.__prometheus_metrics_operation.run_prometheus_queries()
        prometheus_result = self.parse_prometheus_metrics(data=metric_results)
        # save run artifacts logs
        result_list = self._create_pod_run_artifacts(pod_name=f'{self.__pod_name}-{pod_num}')
        if self._es_host:
            # upload several run results
            for result in result_list:
                result.update(prometheus_result)
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def __delete_pod_scale(self, pod_num: str):
        """
        This method create pod in parallel
        """
        self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{pod_num}.yaml'))

    @logger_time_stamp
    def run(self):
        """
        This method run the workload
        :return:
        """
        try:
            self.__prometheus_metrics_operation.init_prometheus()
            if 'kata' in self._workload:
                self.__kind = 'kata'
                self.__name = self._workload.replace('kata', 'pod')
            else:
                self.__kind = 'pod'
                self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            self.__pod_name = f'{self.__workload_name}-{self._trunc_uuid}'
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'
            self._environment_variables_dict['kind'] = self.__kind
            if not self._scale:
                self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=self.__pod_name)
                self._oc.wait_for_initialized(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False)
                self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False)
                self.__status = self._oc.wait_for_pod_completed(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False, job=False)
                self.__status = 'complete' if self.__status else 'failed'
                self.__prometheus_metrics_operation.finalize_prometheus()
                metric_results = self.__prometheus_metrics_operation.run_prometheus_queries()
                prometheus_result = self.parse_prometheus_metrics(data=metric_results)
                # save run artifacts logs
                result_list = self._create_pod_run_artifacts(pod_name=self.__pod_name)
                if self._es_host:
                    # upload several run results
                    for result in result_list:
                        result.update(prometheus_result)
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                    # verify that data upload to elastic search according to unique uuid
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
                self._oc.delete_pod_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    pod_name=self.__pod_name)
            # scale
            else:
                self.__scale = int(self._scale)
                # create namespace
                self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
                # create redis and state signals
                sync_pods = {'redis': 'redis', 'state_signals_exporter_pod': 'state-signals-exporter'}
                for pod, name in sync_pods.items():
                    if pod == 'redis':
                        pod_name = f'redis-master'
                    else:
                        pod_name = name
                    self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{pod}.yaml'), pod_name=pod_name)
                    self._oc.wait_for_initialized(label=f'app={name}', label_uuid=False)
                    self._oc.wait_for_ready(label=f'app={name}', label_uuid=False)
                # prepare scale run
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)), limit=self._threads_limit))
                # create, run and delete vms
                for target in (self.__create_pod_scale, self.__run_pod_scale, self.__delete_pod_scale):
                    proc = []
                    for bulk in bulks:
                        for pod_num in bulk:
                            p = Process(target=target, args=(str(pod_num),))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
                        # sleep between bulks
                        time.sleep(self._bulk_sleep_time)
                        proc = []
                self._create_scale_logs()
                # delete redis and state signals
                for pod, name in sync_pods.items():
                    if pod == 'redis':
                        pod_name = f'redis-master'
                    else:
                        pod_name = name
                    self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{pod}.yaml'), pod_name=pod_name)
                # delete namespace
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                pod_name=self.__pod_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._oc.pod_exists(pod_name=self.__pod_name):
                self._create_pod_log(pod=self.__pod_name)
            self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            if self._es_host:
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=self.__data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=self.__pod_name)
            raise err
