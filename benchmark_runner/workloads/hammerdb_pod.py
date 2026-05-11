
import os
import time

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class HammerdbPod(WorkloadsOperations):
    """
    This class runs HammerDB pod workload with scale support.
    Same code path for 1 pod and N pods.
    Each pod includes its own DB Deployment + HammerDB runner.
    """

    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__database = ''
        self.__es_index = ''
        self.__kind = ''

    def _get_pod_name(self, pod_num: str) -> str:
        if self._scale:
            return f'{self.__workload_name}-{self._trunc_uuid}-{pod_num}'
        return f'{self.__workload_name}-{self._trunc_uuid}'

    def _get_pod_yaml(self, pod_num: str) -> str:
        if self._scale:
            return os.path.join(self._run_artifacts_path, f'{self.__name}_{pod_num}.yaml')
        return os.path.join(self._run_artifacts_path, f'{self.__name}.yaml')

    def _create_pod(self, pod_num: str):
        """Phase 1: Create pod (includes DB Deployment) and wait for completion."""
        try:
            pod_name = self._get_pod_name(pod_num)
            self._oc.create_pod_sync(yaml=self._get_pod_yaml(pod_num), pod_name=pod_name)
            status = self._oc.wait_for_pod_completed(label=f'app={pod_name}',
                                                      workload=self.__workload_name,
                                                      label_uuid=False,
                                                      job=False)
            if not status:
                logger.warning(f'Pod {pod_name} did not complete successfully')
        except Exception as err:
            self.__save_error_logs()
            raise err

    def _collect_logs(self, pod_num: str):
        """Phase 2: Save pod logs to file for later parsing."""
        try:
            pod_name = self._get_pod_name(pod_num)
            output_filename = self._oc.save_pod_log(pod_name=pod_name, log_type='.log')
            logger.info(f'Pod log saved to {output_filename}')
        except Exception as err:
            self.__save_error_logs()
            raise err

    def _delete_pod(self, pod_num: str):
        """Phase 3: Delete pod."""
        try:
            self._oc.delete_async(yaml=self._get_pod_yaml(pod_num))
        except Exception as err:
            self.__save_error_logs()
            raise err

    def _upload_results(self, pod_count: int):
        """Upload all pod results to ES from the main process (no SSL issues)."""
        if self._enable_prometheus_snapshot:
            self._prometheus_metrics_operation.finalize_prometheus()
            metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
            self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

        run_artifacts_url = os.path.join(
            self._run_artifacts_url,
            f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
        )

        for pod_num in range(pod_count):
            pod_name = self._get_pod_name(str(pod_num))
            log_file = os.path.join(self._run_artifacts_path, f'{pod_name}.log')
            try:
                with open(log_file, encoding='utf-8', errors='replace') as f:
                    log_output = f.read()
            except OSError as err:
                logger.warning(f'Could not read HammerDB pod log at {log_file}: {err}')
                log_output = ''

            hammerdb_results_dict = self._parse_hammerdb_results_pod(
                log_output, source_label=log_file)

            if hammerdb_results_dict and self._es_host:
                thread_results = self._hammerdb_thread_results(hammerdb_results_dict)
                for thread_result in thread_results:
                    thread_result.update({
                        'pod_name': pod_name,
                        'pod_name_num': f'hammerdb-pod-{pod_num}',
                    })
                    self._upload_hammerdb_thread_result(
                        index=self.__es_index,
                        kind=self.__kind,
                        status='complete',
                        run_artifacts_url=run_artifacts_url,
                        database=self.__database,
                        thread_result=thread_result,
                    )
                    self._verify_elasticsearch_data_uploaded(
                        index=self.__es_index,
                        uuid=self._uuid,
                    )
            else:
                logger.warning(f'HammerDB results could not be parsed from {log_file}')

    def __save_error_logs(self):
        """Save logs and upload failure status to Elasticsearch on error."""
        if self._es_host:
            run_artifacts_url = os.path.join(
                self._run_artifacts_url,
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )
            tmpl = self._hammerdb_elasticsearch_template_fields()
            self._upload_to_elasticsearch(
                index=self.__es_index,
                kind=self.__kind,
                status='failed',
                result={**{'run_artifacts_url': run_artifacts_url}, **tmpl},
                database=self.__database,
            )
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    @logger_time_stamp
    def run(self):
        """
        Run HammerDB pod workload. Same flow for 1 pod and N pods.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            parts = self._workload.split('_')
            self.__database = parts[2]
            self.__kind = 'kata' if 'kata' in self._workload else 'pod'
            self.__name = f'hammerdb_{self.__kind}_{self.__database}'
            self.__workload_name = f'hammerdb-{self.__database}-pod'

            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'

            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))

            if self.__database == 'mssql':
                namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
                self._oc.run(f'oc adm policy add-scc-to-user anyuid -z default -n {namespace}')

            configmap_yaml = os.path.join(
                self._run_artifacts_path,
                f'hammerdb_{self.__kind}_{self.__database}_configmap.yaml'
            )
            self._oc.create_async(yaml=configmap_yaml)

            if self._scale:
                pod_count = self._scale * len(self._scale_node_list)
                threads_limit = self._threads_limit
                bulk_sleep = self._bulk_sleep_time
            else:
                pod_count = 1
                threads_limit = 1
                bulk_sleep = 0

            bulks = tuple(self.split_run_bulks(iterable=range(pod_count), limit=threads_limit))

            steps = [self._create_pod, self._collect_logs]
            if self._delete_all:
                steps.append(self._delete_pod)
            self._run_parallel_phases(steps, bulks, bulk_sleep)

            self._upload_results(pod_count)

            if self._delete_all:
                self._oc.delete_async(yaml=configmap_yaml)
                self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.__save_error_logs()
            raise err
        except Exception as err:
            self.__save_error_logs()
            raise err
