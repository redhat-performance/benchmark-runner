
import json
import os
import re
import time
from datetime import datetime, timezone

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class UperfPod(WorkloadsOperations):
    """
    This class runs uperf workload using direct Job creation (no operator)
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = self._workload.replace('_', '-')
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__server_job_name = f'uperf-server-{self._trunc_uuid}'
        self.__client_job_name = f'uperf-client-{self._trunc_uuid}'
        self.__template_ops = TemplateOperations(workload=self._workload)

    def _extract_json_from_pod_logs(self, pod_logs: str) -> list:
        """
        Extract parsed JSON results from pod logs.
        Parser prints one JSON doc per line at the end of logs.
        """
        results = []
        for line in pod_logs.strip().splitlines():
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if not results:
            logger.warning("No JSON results found in pod logs")
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
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            if 'kata' in self._workload:
                self.__kind = 'kata'
                self.__name = self._workload.replace('kata', 'pod')
            else:
                self.__kind = 'pod'
                self.__name = self._workload

            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'

            self._environment_variables_dict['kind'] = self.__kind

            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            logger.info("Creating uperf server job")
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))

            self._oc.wait_for_pod_create(pod_name='uperf-server')

            server_name = self._environment_variables_dict.get('pin_node1', '')
            if server_name:
                label = f'app=uperf-bench-server-0-{self._trunc_uuid}'
            else:
                label = f'role=server'
            self._oc.wait_for_initialized(label=label, workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=label, workload=self.__workload_name, label_uuid=False)

            logger.info("Uperf server is ready, getting server IP")

            namespace = self._environment_variables_dict['namespace']
            server_label = f'app=uperf-bench-server-0-{self._trunc_uuid}'
            server_ip = self._oc.get_pod_ip(label=server_label, namespace=namespace)
            logger.info(f"Server IP: {server_ip}")

            server_node = self._oc.get_pod_node(label=server_label, namespace=namespace)
            logger.info(f"Server Node: {server_node}")

            cluster_name = self._oc.get_cluster_name()

            self._environment_variables_dict['server_ip'] = server_ip
            self._environment_variables_dict['server_node'] = server_node
            self._environment_variables_dict['clustername'] = cluster_name

            time.sleep(5)

            self.__template_ops.set_environment_variables(self._environment_variables_dict)
            self.__template_ops.generate_yamls()

            logger.info(f"Creating client job with server IP {server_ip}")

            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))

            self._oc.wait_for_pod_create(pod_name='uperf-client')
            self._oc.wait_for_initialized(label='app=uperf-bench-client', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label='app=uperf-bench-client', workload=self.__workload_name, label_uuid=False)

            self.__status = self._oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=self.__workload_name, label_uuid=False, job=True)
            self.__status = 'complete' if self.__status else 'failed'

            # Get client pod info and logs
            logger.info("Extracting uperf results from client pod logs")
            client_pod = self._oc.get_pod(label='uperf-client')
            client_node = self._oc.get_pod_node(pod_name=client_pod, namespace=namespace)
            client_ip = self._oc.get_pod_ip(pod_name=client_pod, namespace=namespace)
            logger.info(f"Client Node: {client_node}, Client IP: {client_ip}")

            pod_logs = self._oc.get_pod_logs(pod_name=client_pod, namespace=namespace)

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, labels=['uperf-client', 'uperf-server'])

            if self._es_host:
                logger.info("Extracting uperf JSON results from pod logs")
                parsed_results = self._extract_json_from_pod_logs(pod_logs)

                if parsed_results:
                    logger.info(f"Uploading {len(parsed_results)} uperf results to ElasticSearch")
                    for parsed in parsed_results:
                        # Add metadata from benchmark-runner
                        parsed['uuid'] = self._uuid
                        parsed['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                        parsed['uperf_ts'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
                        throughput_gbps = round((parsed.get('norm_byte', 0) * 8) / (1024**3), 4) if parsed.get('norm_byte', 0) > 0 else 0
                        logger.info(f"  {parsed.get('test_type')}-{parsed.get('protocol')}-{parsed.get('message_size')}-{parsed.get('num_threads')}: "
                                    f"throughput={throughput_gbps}Gbps, latency={parsed.get('norm_ltcy')}ms")
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
                    logger.warning("No uperf JSON found in pod logs, uploading minimal metadata")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status,
                                                  result={'uuid': self._uuid, 'workload': 'uperf', 'kind': self.__kind, 'run_artifacts_url': run_artifacts_url})

            # Cleanup
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))

            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.save_error_logs()
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))
            raise err

        except Exception as err:
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

            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_client.yaml'))
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_server.yaml'))
            raise err
