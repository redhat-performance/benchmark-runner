
import os
import re
from datetime import datetime, timezone
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class SysbenchPod(WorkloadsOperations):
    """
    This class runs sysbench pod workload.
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''

    @typechecked
    def _parse_single_section(self, section: str, test_type: str) -> dict:
        """
        Parse a single sysbench test section and extract metrics.
        """
        metrics = {
            'uuid': self._uuid,
            'workload': 'sysbench',
            'kind': self.__kind,
            'test_type': test_type,
            'user': self._environment_variables_dict.get('test_user', 'user'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'sysbench_threads': 0,
            'sysbench_time': 0,
            'events_avg': 0.0,
            'latency_95th': 0.0,
            'events_per_second': 0.0,
            'total_events': 0,
            'total_time': 0.0,
            'latency_avg': 0.0,
            'memory_throughput': 0.0,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        events_match = re.search(r'events\s+\(avg/stddev\):\s+([\d.]+)', section)
        if events_match:
            metrics['events_avg'] = float(events_match.group(1))

        latency_match = re.search(r'95th percentile:\s+([\d.]+)', section)
        if latency_match:
            metrics['latency_95th'] = float(latency_match.group(1))

        eps_match = re.search(r'events per second:\s+([\d.]+)', section)
        if eps_match:
            metrics['events_per_second'] = float(eps_match.group(1))

        total_events_match = re.search(r'total number of events:\s+(\d+)', section)
        if total_events_match:
            metrics['total_events'] = int(total_events_match.group(1))

        total_time_match = re.search(r'total time:\s+([\d.]+)s', section)
        if total_time_match:
            metrics['total_time'] = float(total_time_match.group(1))

        latency_avg_match = re.search(r'Latency.*?avg:\s+([\d.]+)', section, re.DOTALL)
        if latency_avg_match:
            metrics['latency_avg'] = float(latency_avg_match.group(1))

        threads_match = re.search(r'Number of threads:\s+(\d+)', section)
        if threads_match:
            metrics['sysbench_threads'] = int(threads_match.group(1))

        if metrics['total_time'] > 0:
            metrics['sysbench_time'] = round(metrics['total_time'])

        if test_type == 'memory':
            throughput_match = re.search(r'MiB transferred \(([\d.]+) MiB/sec\)', section)
            if throughput_match:
                metrics['memory_throughput'] = float(throughput_match.group(1))

        logger.info(f"Parsed sysbench {test_type}: events_avg={metrics['events_avg']}, latency_95th={metrics['latency_95th']}ms, threads={metrics['sysbench_threads']}, time={metrics['sysbench_time']}, memory_throughput={metrics['memory_throughput']}")
        return metrics

    @typechecked
    def _parse_sysbench_output(self, output: str) -> list:
        """
        Parse sysbench output containing CPU and memory test results.
        Returns a list of metrics dicts (one per test type).
        """
        if not output:
            logger.warning("No sysbench output to parse")
            return []

        results = []

        cpu_match = re.search(r'=== SYSBENCH CPU TEST ===(.*?)=== SYSBENCH CPU TEST DONE ===', output, re.DOTALL)
        if cpu_match:
            results.append(self._parse_single_section(cpu_match.group(1), 'cpu'))

        memory_match = re.search(r'=== SYSBENCH MEMORY TEST ===(.*?)=== SYSBENCH MEMORY TEST DONE ===', output, re.DOTALL)
        if memory_match:
            results.append(self._parse_single_section(memory_match.group(1), 'memory'))

        # Fallback: if no markers found, parse entire output as cpu
        if not results:
            results.append(self._parse_single_section(output, 'cpu'))

        logger.info(f"Uploading {len(results)} sysbench results to ElasticSearch")
        return results

    def save_error_logs(self):
        if self._es_host:
            data_dict = {
                'run_artifacts_url': os.path.join(
                    self._run_artifacts_url,
                    f'{self._get_run_artifacts_hierarchy(workload_name=self._get_workload_file_name(self.__workload_name), is_file=True)}.tar.gz'
                )
            }
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=data_dict)
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    @logger_time_stamp
    def run(self):
        """
        This method runs the sysbench pod workload
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            self.__kind = 'pod'
            self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'sysbench-test-ci-results'
            else:
                self.__es_index = 'sysbench-results'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace and apply security privileged SCC
            self._oc.apply_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
            self._oc.apply_security_privileged()

            # Create Job
            self._oc.create_async(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                is_check=True,
            )

            # Wait for pod creation, initialization, readiness, and Job completion
            sysbench_label = f'app=sysbench-workload-{self._trunc_uuid}'
            self._oc.wait_for_pod_create(label=sysbench_label)
            self._oc.wait_for_initialized(label=sysbench_label, label_uuid=False)
            self._oc.wait_for_ready(label=sysbench_label, label_uuid=False)

            self.__status = self._oc.wait_for_pod_completed(label=sysbench_label, label_uuid=False, job=True)
            self.__status = 'complete' if self.__status else 'failed'

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts (also saves pod logs to file)
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name)

            # Read pod logs from saved file (already saved by _create_run_artifacts)
            sysbench_pod = self._oc.get_pod(label='sysbench-pod')
            log_file = os.path.join(self._run_artifacts_path, sysbench_pod)
            with open(log_file, 'r') as f:
                pod_logs = f.read()

            if self._es_host:
                if self.__status == 'complete' and pod_logs:
                    logger.info("Parsing sysbench pod logs")
                    metrics_list = self._parse_sysbench_output(pod_logs)
                    for metrics in metrics_list:
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)
                    if ids is False:
                        raise ElasticSearchDataNotUploaded

                    for doc_id in ids:
                        self._update_elasticsearch_index(
                            index=self.__es_index,
                            id=doc_id,
                            kind=self.__kind,
                            status=self.__status,
                            run_artifacts_url=run_artifacts_url,
                            prometheus_result=self._prometheus_result
                        )
                else:
                    self._upload_to_elasticsearch(
                        index=self.__es_index,
                        kind=self.__kind,
                        status='failed',
                        result={'run_artifacts_url': run_artifacts_url}
                    )
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

            # Cleanup
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))

            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.save_error_logs()
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
            raise err

        except Exception as err:
            sysbench_label = f'app=sysbench-workload-{self._trunc_uuid}'
            if self._oc.pod_label_exists(label_name=sysbench_label):
                pod_name = self._oc.get_pod(label_selector=sysbench_label)
                if pod_name:
                    self._oc.save_pod_log(pod_name=pod_name)

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=3)
                if ids:
                    for doc_id in ids:
                        self._update_elasticsearch_index(
                            index=self.__es_index,
                            id=doc_id,
                            kind=self.__kind,
                            status='failed',
                            run_artifacts_url=run_artifacts_url
                        )
                else:
                    self._upload_to_elasticsearch(
                        index=self.__es_index,
                        kind=self.__kind,
                        status='failed',
                        result={'run_artifacts_url': run_artifacts_url}
                    )
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
            raise err
