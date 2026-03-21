
import os
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class StressngPod(WorkloadsOperations):
    """
    This class runs stressng workload using direct Job creation (no operator)
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__job_name = ''

    def save_error_logs(self):
        """
        This method uploads logs into elastic and s3 bucket in case of error
        """
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
        This method runs the stressng workload
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set workload type
            if 'kata' in self._workload:
                self.__kind = 'kata'
                self.__name = self._workload.replace('kata', 'pod')
            else:
                self.__kind = 'pod'
                self.__name = self._workload

            self.__workload_name = self._workload.replace('_', '-')
            self.__job_name = f'{self.__workload_name}-{self._trunc_uuid}'

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace (apply so it does not fail if namespace already exists)
            self._oc.apply_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create ConfigMap and Job; use is_check=True so creation failures surface immediately
            self._oc.create_async(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'),
                is_check=True,
            )
            self._oc.create_async(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                is_check=True,
            )

            # Wait for Job to create pod (by label; Job pods have name <job>-<suffix>)
            self._oc.wait_for_pod_create_by_label(label=f'app=stressng_workload-{self._trunc_uuid}')

            # Wait for pod to be initialized and ready
            self._oc.wait_for_initialized(label=f'app=stressng_workload-{self._trunc_uuid}', label_uuid=False)
            self._oc.wait_for_ready(label=f'app=stressng_workload-{self._trunc_uuid}', label_uuid=False)

            # Wait for Job completion
            self.__status = self._oc.wait_for_pod_completed(label=f'app=stressng_workload-{self._trunc_uuid}', label_uuid=False, job=True)
            self.__status = 'complete' if self.__status else 'failed'

            if self._enable_prometheus_snapshot:
                # Prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name)

            if self._es_host:
                if self.__status == 'failed':
                    # Job failed: try to update existing doc if pod uploaded, else upload failure doc
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=10)
                    if ids:
                        for id in ids:
                            self._update_elasticsearch_index(
                                index=self.__es_index,
                                id=id,
                                kind=self.__kind,
                                status='failed',
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
                else:
                    # Verify that data uploaded to ElasticSearch (workload pod uploads it during job run)
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)
                    if ids is False:
                        raise ElasticSearchDataNotUploaded

                    # Update metadata for each result
                    for id in ids:
                        self._update_elasticsearch_index(
                            index=self.__es_index,
                            id=id,
                            kind=self.__kind,
                            status=self.__status,
                            run_artifacts_url=run_artifacts_url,
                            prometheus_result=self._prometheus_result
                        )

            # Cleanup: delete Job and ConfigMap
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.save_error_logs()
            # Cleanup on error
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))
            raise err

        except Exception as err:
            # Save run artifacts logs (get pod by label; Job pods have name <job>-<suffix>)
            stressng_label = f'app=stressng_workload-{self._trunc_uuid}'
            if self._oc.pod_label_exists(label_name=stressng_label):
                pod_name = self._oc.get_first_pod_name_by_label(label=stressng_label)
                if pod_name:
                    self._oc.save_pod_log(pod_name=pod_name)

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=3)
                if ids:
                    for id in ids:
                        self._update_elasticsearch_index(
                            index=self.__es_index,
                            id=id,
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

            # Cleanup on error
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))
            raise err
