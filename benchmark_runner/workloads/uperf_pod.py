
import os
import re
import subprocess
import time
from datetime import datetime, timezone
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

    def _parse_uperf_pod_logs(self, pod_logs, server_ip, server_node, client_node, pod_id):
        """
        Parse uperf pod logs and extract metrics

        Args:
            pod_logs: Raw pod log output containing uperf results
            server_ip: Server IP address
            server_node: Server node name
            client_node: Client node name
            pod_id: Client pod name

        Returns:
            List of dictionaries with parsed metrics (one per test combination)
        """
        metrics_list = []

        # Default environment metadata
        env_metadata = {
            'uuid': self._uuid,
            'workload': 'uperf',
            'kind': 'pod',
            'user': self._environment_variables_dict.get('test_user', 'ripsaw'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'iteration': 0,
            'client_ips': self._environment_variables_dict.get('client_ips', ''),
            'remote_ip': server_ip,
            'service_ip': self._environment_variables_dict.get('service_ip', 'False'),
            'service_type': self._environment_variables_dict.get('service_type', ''),
            'port': self._environment_variables_dict.get('port', '30000'),
            'server_node': server_node,
            'num_pairs': self._environment_variables_dict.get('num_pairs', ''),
            'multus_client': self._environment_variables_dict.get('multus_client', ''),
            'networkpolicy': self._environment_variables_dict.get('networkpolicy', ''),
            'density': self._environment_variables_dict.get('density', ''),
            'nodes_in_iter': self._environment_variables_dict.get('nodes_in_iter', ''),
            'step_size': self._environment_variables_dict.get('step_size', ''),
            'colocate': self._environment_variables_dict.get('colocate', ''),
            'density_range': self._environment_variables_dict.get('density_range', ''),
            'node_range': self._environment_variables_dict.get('node_range', ''),
            'hostnetwork': self._environment_variables_dict.get('hostnetwork', 'False')
        }

        # Split logs by test runs (each test starts with "<?xml")
        test_sections = pod_logs.split('<?xml version=1.0?>')

        for section in test_sections[1:]:  # Skip first empty split
            # Parse test parameters from XML profile
            profile_match = re.search(r'<profile name="([^"]+)">', section)
            if not profile_match:
                continue

            profile_name = profile_match.group(1)
            parts = profile_name.split('-')

            if len(parts) >= 5:
                test_type = parts[0]
                protocol = parts[1]
                message_size = int(parts[2]) if parts[2].isdigit() else 64
                read_message_size = int(parts[3]) if parts[3].isdigit() else 64
                num_threads = int(parts[4]) if parts[4].isdigit() else 1
            else:
                # Fallback defaults
                test_type = 'stream'
                protocol = 'tcp'
                message_size = 64
                read_message_size = 64
                num_threads = 1

            # Parse uperf output - look for Txn2 lines
            pattern = r'timestamp_ms:([\d.]+).*name:Txn2.*nr_bytes:(\d+).*nr_ops:(\d+)'
            result_lines = []

            for line in section.splitlines():
                match = re.search(pattern, line)
                if match:
                    ts, bytes_val, ops_val = match.groups()
                    result_lines.append({
                        'timestamp_ms': float(ts),
                        'bytes': int(bytes_val),
                        'ops': int(ops_val)
                    })

            if not result_lines:
                logger.warning(f"No Txn2 data found for profile {profile_name}")
                continue

            # Get last line (final cumulative values)
            last = result_lines[-1]
            bytes_total = last['bytes']
            ops_total = last['ops']

            # Calculate normalized values
            norm_byte = bytes_total
            norm_ops = ops_total
            norm_ltcy = 0.0

            if len(result_lines) >= 2:
                prev = result_lines[-2]
                norm_byte = last['bytes'] - prev['bytes']
                norm_ops = last['ops'] - prev['ops']

                if norm_ops > 0:
                    time_diff_ms = last['timestamp_ms'] - prev['timestamp_ms']
                    norm_ltcy = round(time_diff_ms / norm_ops * 1000, 4)

            # Calculate duration and throughput
            duration = len(result_lines)
            throughput_mbps = 0.0

            if len(result_lines) > 0:
                first = result_lines[0]
                duration_sec = (last['timestamp_ms'] - first['timestamp_ms']) / 1000
                if duration_sec > 0 and bytes_total > 0:
                    throughput_mbps = round(bytes_total * 8 / duration_sec / 1000000, 4)

            # Create metrics document
            metrics = {
                **env_metadata,
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                'uperf_ts': datetime.fromtimestamp(last['timestamp_ms'] / 1000, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
                'test_type': test_type,
                'protocol': protocol,
                'message_size': message_size,
                'read_message_size': read_message_size,
                'num_threads': num_threads,
                'bytes': bytes_total,
                'ops': ops_total,
                'norm_byte': norm_byte,
                'norm_ops': norm_ops,
                'norm_ltcy': norm_ltcy,
                'duration': duration,
                'throughput_mbps': throughput_mbps,
                'client_node': client_node,
                'pod_id': pod_id
            }

            metrics_list.append(metrics)

        return metrics_list

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

            # Get server pod IP and node using oc command
            server_ip_cmd = f"oc get pods -n {self._environment_variables_dict['namespace']} -l app=uperf-bench-server-0-{self._trunc_uuid} -o jsonpath='{{.items[0].status.podIP}}'"
            result = subprocess.run(server_ip_cmd, shell=True, capture_output=True, text=True)
            server_ip = result.stdout.strip().strip("'")
            logger.info(f"Server IP: {server_ip}")

            # Get server node
            server_node_cmd = f"oc get pods -n {self._environment_variables_dict['namespace']} -l app=uperf-bench-server-0-{self._trunc_uuid} -o jsonpath='{{.items[0].spec.nodeName}}'"
            result = subprocess.run(server_node_cmd, shell=True, capture_output=True, text=True)
            server_node = result.stdout.strip().strip("'")
            logger.info(f"Server Node: {server_node}")

            # Get cluster name from cluster version
            cluster_name_cmd = "oc get clusterversion -o jsonpath='{.items[0].spec.clusterID}'"
            result = subprocess.run(cluster_name_cmd, shell=True, capture_output=True, text=True)
            cluster_name = result.stdout.strip().strip("'")
            if not cluster_name:
                # Fallback: get from infrastructure
                cluster_name_cmd = "oc get infrastructure cluster -o jsonpath='{.status.infrastructureName}'"
                result = subprocess.run(cluster_name_cmd, shell=True, capture_output=True, text=True)
                cluster_name = result.stdout.strip().strip("'")

            # Update environment variables with server info for client template
            self._environment_variables_dict['server_ip'] = server_ip
            self._environment_variables_dict['server_node'] = server_node
            self._environment_variables_dict['clustername'] = cluster_name
            self._environment_variables_dict['test_user'] = os.environ.get('TEST_USER', 'ripsaw')
            self._environment_variables_dict['port'] = os.environ.get('PORT', '30000')
            self._environment_variables_dict['run_id'] = os.environ.get('RUN_ID', 'NA')

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

            # Extract uperf results from client pod logs
            logger.info("Extracting uperf results from client pod logs")
            client_pod = self._oc.get_pod(label='uperf-client')

            # Get client node name
            client_node_cmd = f"oc get pods -n {self._environment_variables_dict['namespace']} {client_pod} -o jsonpath='{{.spec.nodeName}}'"
            result = subprocess.run(client_node_cmd, shell=True, capture_output=True, text=True)
            client_node = result.stdout.strip().strip("'")
            logger.info(f"Client Node: {client_node}")

            # Get pod logs using oc command
            logs_cmd = f"oc logs -n {self._environment_variables_dict['namespace']} {client_pod}"
            result = subprocess.run(logs_cmd, shell=True, capture_output=True, text=True)
            pod_logs = result.stdout

            if self._enable_prometheus_snapshot:
                # Prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload_name, labels=['uperf-client', 'uperf-server'])

            if self._es_host:
                # Parse uperf logs and upload results
                logger.info("Parsing uperf pod logs")
                metrics_list = self._parse_uperf_pod_logs(pod_logs, server_ip, server_node, client_node, client_pod)

                if metrics_list:
                    logger.info(f"Uploading {len(metrics_list)} uperf results to ElasticSearch")
                    for metrics in metrics_list:
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    # Verify data was uploaded
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)

                    # Update metadata for each result
                    if ids:
                        for id in ids:
                            self._update_elasticsearch_index(
                                index=self.__es_index,
                                id=id,
                                kind=self.__kind,
                                status=self.__status,
                                run_artifacts_url=run_artifacts_url,
                                prometheus_result=self._prometheus_result
                            )
                else:
                    logger.warning("No uperf metrics found in pod logs, uploading minimal metadata")
                    minimal_data = {
                        'uuid': self._uuid,
                        'workload': 'uperf',
                        'kind': self.__kind,
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=minimal_data)

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
