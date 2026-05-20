
import json
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class FioPod(WorkloadsOperations):
    """
    This class runs fio pod
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

    FIO_RESULTS_START = '@@~@@FIO-RESULTS-START@@~@@'
    FIO_RESULTS_END = '@@~@@FIO-RESULTS-END@@~@@'

    def _create_pod_run_artifacts_json(self, pod_name: str):
        """
        This method creates pod run artifacts from FIO JSON output.
        Extracts JSON between FIO-RESULTS-START/END delimiters in pod log.
        """
        result_list = []
        pod_log_file = self._create_pod_log(pod=pod_name, log_type='.log')
        workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
        try:
            with open(pod_log_file, 'r') as f:
                content = f.read()
            start_idx = content.find(self.FIO_RESULTS_START)
            end_idx = content.find(self.FIO_RESULTS_END)
            if start_idx == -1 or end_idx == -1:
                logger.warning(f'FIO result delimiters not found in {pod_log_file}')
                return result_list
            json_str = content[start_idx + len(self.FIO_RESULTS_START):end_idx].strip()
            summary = json.loads(json_str)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f'Failed to parse FIO JSON from {pod_log_file}: {e}')
            return result_list
        workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
        run_artifacts_url = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')
        for block_size, ops in summary.items():
            for io_operation, metrics in ops.items():
                result = {
                    'block_size': block_size,
                    'io_operation': io_operation,
                    'total_iops': metrics.get('TotalIOPS', 0),
                    'total_bw_kbs': metrics.get('TotalBW_KBs', 0),
                    'lat_avg_usec': metrics.get('LatAvg_usec', 0),
                    'lat_p99_usec': metrics.get('LatP99_usec', 0),
                    'pod_name': pod_name,
                    'run_artifacts_url': run_artifacts_url,
                }
                result_list.append(result)
        result_json_path = os.path.join(self._run_artifacts_path, f'{pod_name}.json')
        with open(result_json_path, 'w') as f:
            json.dump(result_list, f, indent=2)
        logger.info(f'FIO results saved to {result_json_path}')
        return result_list

    def save_error_logs(self):
        if self._es_host:
            self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._get_workload_file_name(self.__workload_name), is_file=True)}.tar.gz')
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed',
                                          result=self.__data_dict)
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def __create_pod_scale(self, pod_num: str):
        try:
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{pod_num}.yaml'))
            self._oc.wait_for_pod_create(pod_name=f'{self.__pod_name}-{pod_num}')
        except Exception as err:
            raise err

    def __run_pod_scale(self, pod_num: str):
        try:
            self._oc.wait_for_initialized(label=f'app=fio-{self._trunc_uuid}-{pod_num}', label_uuid=False)
            self._oc.wait_for_ready(label=f'app=fio-{self._trunc_uuid}-{pod_num}', label_uuid=False)
            self._oc.wait_for_pod_completed(label=f'app=fio-{self._trunc_uuid}-{pod_num}', label_uuid=False, job=False)
            self._create_pod_run_artifacts_json(pod_name=f'{self.__pod_name}-{pod_num}')
        except Exception as err:
            raise err

    def __delete_pod_scale(self, pod_num: str):
        try:
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{pod_num}.yaml'))
        except Exception as err:
            raise err

    @logger_time_stamp
    def run(self):
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()
            workload = self._workload.removesuffix('_ephemeral')
            self.__kind = 'pod'
            self.__name = workload
            self.__workload_name = workload.replace('_', '-')
            self.__pod_name = f'{self.__workload_name}-{self._trunc_uuid}'
            if self._run_type == 'test_ci':
                self.__es_index = 'fio-test-ci-results'
            else:
                self.__es_index = 'fio-results'
            self._environment_variables_dict['kind'] = self.__kind
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'fio_configmap.yaml'))
            if not self._scale:
                self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=self.__pod_name)
                self._oc.wait_for_initialized(label=f'app=fio-{self._trunc_uuid}', label_uuid=False)
                self._oc.wait_for_ready(label=f'app=fio-{self._trunc_uuid}', label_uuid=False)
                self.__status = self._oc.wait_for_pod_completed(label=f'app=fio-{self._trunc_uuid}', label_uuid=False, job=False)
                self.__status = 'complete' if self.__status else 'failed'
                if self._enable_prometheus_snapshot:
                    self._prometheus_metrics_operation.finalize_prometheus()
                    metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                    self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
                result_list = self._create_pod_run_artifacts_json(pod_name=self.__pod_name)
                if self._es_host:
                    for result in result_list:
                        if self._enable_prometheus_snapshot:
                            result.update(self._prometheus_result)
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
                self._oc.delete_pod_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    pod_name=self.__pod_name)
            else:
                self.__scale = int(self._scale)
                pod_count = self._scale * len(self._scale_node_list)
                bulks = tuple(self.split_run_bulks(iterable=range(pod_count), limit=self._threads_limit))
                for target in (self.__create_pod_scale, self.__run_pod_scale, self.__delete_pod_scale):
                    proc = []
                    for bulk in bulks:
                        for pod_num in bulk:
                            p = Process(target=target, args=(str(pod_num),))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
                        time.sleep(self._bulk_sleep_time)
                        proc = []
                if self._enable_prometheus_snapshot:
                    self._prometheus_metrics_operation.finalize_prometheus()
                    metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                    self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
                if self._es_host:
                    for pod_num in range(pod_count):
                        result_json = os.path.join(self._run_artifacts_path, f'{self.__pod_name}-{pod_num}.json')
                        if not os.path.exists(result_json):
                            continue
                        with open(result_json) as f:
                            result_list = json.load(f)
                        for result in result_list:
                            if self._enable_prometheus_snapshot:
                                result.update(self._prometheus_result)
                            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='complete', result=result)
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                pod_name=self.__pod_name)
            raise err
        except Exception as err:
            if self._oc.pod_exists(pod_name=self.__pod_name):
                self._create_pod_log(pod=self.__pod_name)
            self.save_error_logs()
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), pod_name=self.__pod_name)
            raise err
