
import os

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class HammerdbPod(WorkloadsOperations):
    """
    This class runs HammerDB pod workload (benchmark-runner path).
    Applies resources in order: namespace -> configmap -> combined DB+HammerDB pod YAML.
    """

    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__database = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''

    def __save_error_logs(self):
        """Save logs and upload failure status to Elasticsearch on error"""
        if self._oc.pod_exists(pod_name=self.__pod_name):
            self._create_pod_log(pod=self.__pod_name)
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
        Run HammerDB pod workload: namespace -> configmap -> pod, then wait for completion.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # e.g. workload = 'hammerdb_pod_mariadb' -> database = 'mariadb', kind = 'pod'
            parts = self._workload.split('_')
            self.__database = parts[2]
            self.__kind = 'kata' if 'kata' in self._workload else 'pod'
            self.__name = f'hammerdb_{self.__kind}_{self.__database}'
            self.__workload_name = f'hammerdb-{self.__database}-pod'
            self.__pod_name = f'{self.__workload_name}-{self._trunc_uuid}'

            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'

            # 1. Create namespace
            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))

            # 2. Create configmaps
            configmap_yaml = os.path.join(
                self._run_artifacts_path,
                f'hammerdb_{self.__kind}_{self.__database}_configmap.yaml'
            )
            self._oc.create_async(yaml=configmap_yaml)

            # 3. Create combined DB server + HammerDB pod YAML
            pod_yaml = os.path.join(self._run_artifacts_path, f'{self.__name}.yaml')
            self._oc.create_pod_sync(yaml=pod_yaml, pod_name=self.__pod_name)

            # Wait for HammerDB pod to complete (initContainer waits for DB readiness)
            self.__status = self._oc.wait_for_pod_completed(label=f'app={self.__pod_name}',
                                                            workload=self.__workload_name,
                                                            label_uuid=False,
                                                            job=False)
            self.__status = 'complete' if self.__status else 'failed'

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            output_filename = self._oc.save_pod_log(pod_name=self.__pod_name, log_type='.log')
            try:
                with open(output_filename, encoding='utf-8', errors='replace') as f:
                    log_output = f.read()
            except OSError as err:
                logger.warning('Could not read HammerDB pod log at %s: %s', output_filename, err)
                log_output = ''
            hammerdb_results_dict = self._parse_hammerdb_results_pod(
                log_output, source_label=output_filename)
            if not hammerdb_results_dict:
                logger.warning('HammerDB results could not be parsed from pod log (path=%s)', output_filename)

            if self._es_host:
                run_artifacts_url = os.path.join(
                    self._run_artifacts_url,
                    f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
                )
                thread_results = self._hammerdb_thread_results(hammerdb_results_dict)
                if thread_results:
                    for thread_result in thread_results:
                        self._upload_hammerdb_thread_result(
                            index=self.__es_index,
                            kind=self.__kind,
                            status=self.__status,
                            run_artifacts_url=run_artifacts_url,
                            database=self.__database,
                            thread_result=thread_result,
                        )
                        extra_match = {
                            k: thread_result[k]
                            for k in ('threads', 'current_worker')
                            if k in thread_result
                        }
                        self._verify_elasticsearch_data_uploaded(
                            index=self.__es_index,
                            uuid=self._uuid,
                            extra_match=extra_match if extra_match else None,
                        )

            # Cleanup: delete the combined YAML (removes DB deployment, service, PVC, and pod)
            self._oc.delete_async(yaml=pod_yaml)
            self._oc.delete_async(yaml=configmap_yaml)

        except ElasticSearchDataNotUploaded as err:
            self.__save_error_logs()
            raise err
        except Exception as err:
            self.__save_error_logs()
            raise err
