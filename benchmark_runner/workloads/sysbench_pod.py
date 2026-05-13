
import os
from datetime import datetime, timezone

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

            self._oc.apply_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

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

            self.__status = self._oc.wait_for_pod_completed(label=sysbench_label, label_uuid=False, job=False)
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
                    logger.info("Extracting sysbench JSON results from pod logs")
                    parsed = self._extract_json_from_pod_logs(pod_logs)

                    if parsed:
                        parsed['uuid'] = self._uuid
                        parsed['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                        logger.info(f"Uploading sysbench results: cpu_events_avg={parsed.get('cpu_events_avg')}, memory_throughput_mib={parsed.get('memory_throughput_mib')}")
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=parsed)

                        ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)
                        if ids:
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
                        logger.warning("No sysbench JSON found in pod logs, uploading minimal metadata")
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status,
                                                      result={'uuid': self._uuid, 'workload': 'sysbench', 'kind': self.__kind, 'run_artifacts_url': run_artifacts_url})
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
