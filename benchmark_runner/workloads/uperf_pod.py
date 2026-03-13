
import os
import time
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class UperfPod(WorkloadsOperations):
    """
    This class runs uperf workload using direct Job creation (no operator)
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__server_job_name = ''
        self.__client_job_name = ''

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
        This method runs the uperf workload
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
            self.__server_job_name = f'uperf-server-{self._trunc_uuid}'
            self.__client_job_name = f'uperf-client-{self._trunc_uuid}'

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create ConfigMap with uperf workload profiles
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))

            # Create and run Server Job
            logger.info("Creating uperf server job")
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))

            # Wait for server pod to be created and ready
            self._oc.wait_for_pod_create(pod_name='uperf-server')

            # Wait for server to be initialized
            server_name = self._environment_variables_dict.get('pin_node1', '')
            if server_name:
                label = f'app=uperf-bench-server-0-{self._trunc_uuid}'
                self._oc.wait_for_initialized(label=label, workload=self.__workload_name, label_uuid=False)
                self._oc.wait_for_ready(label=label, workload=self.__workload_name, label_uuid=False)
            else:
                label = f'role=server'
                self._oc.wait_for_initialized(label=label, workload=self.__workload_name, label_uuid=False)
                self._oc.wait_for_ready(label=label, workload=self.__workload_name, label_uuid=False)

            logger.info("Uperf server is ready, getting server IP")

            # Get server pod IP using oc command
            import subprocess
            server_ip_cmd = f"oc get pods -n {self._environment_variables_dict['namespace']} -l app=uperf-bench-server-0-{self._trunc_uuid} -o jsonpath='{{.items[0].status.podIP}}'"
            result = subprocess.run(server_ip_cmd, shell=True, capture_output=True, text=True)
            server_ip = result.stdout.strip().strip("'")
            logger.info(f"Server IP: {server_ip}")

            # Update environment variables with server IP for client template
            self._environment_variables_dict['server_ip'] = server_ip

            # Give server a moment to fully start listening
            time.sleep(5)

            # Re-generate client YAML with server IP (template needs it)
            from benchmark_runner.common.template_operations.template_operations import TemplateOperations
            template_ops = TemplateOperations(workload=self._workload)
            template_ops.set_environment_variables(self._environment_variables_dict)
            # This will regenerate all YAMLs including client with server_ip
            template_ops.generate_yamls()

            logger.info(f"Creating client job with server IP {server_ip}")

            # Create and run Client Job
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))

            # Wait for client pod to be created
            self._oc.wait_for_pod_create(pod_name='uperf-client')
            self._oc.wait_for_initialized(label='app=uperf-bench-client', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label='app=uperf-bench-client', workload=self.__workload_name, label_uuid=False)

            # Wait for client Job completion
            self.__status = self._oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=self.__workload_name, label_uuid=False, job=True)
            self.__status = 'complete' if self.__status else 'failed'

            if self._enable_prometheus_snapshot:
                # Prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, labels=['uperf-client', 'uperf-server'])

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

            # Cleanup: delete Jobs and ConfigMap
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.save_error_logs()
            # Cleanup on error
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))
            raise err

        except Exception as err:
            # Save run artifacts logs
            if self._oc.pod_exists(pod_name='uperf-server'):
                self._create_pod_log(pod='uperf-server')
            if self._oc.pod_exists(pod_name='uperf-client'):
                self._create_pod_log(pod='uperf-client')

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
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_configmap.yaml'))
            raise err
