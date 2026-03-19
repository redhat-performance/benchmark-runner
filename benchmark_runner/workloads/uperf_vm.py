
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class UperfVM(WorkloadsOperations):
    """
    This class runs uperf VM workload using direct VirtualMachine creation (no operator)
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__server_vm_name = ''
        self.__client_vm_name = ''

    def _extract_file_from_vm(self, vm_name, file_path):
        """
        Extract a file from a VM using kubectl exec into virt-launcher pod

        Args:
            vm_name: Name of the VM
            file_path: Path to file inside the VM

        Returns:
            File contents as string, or None if extraction fails
        """
        try:
            # Get virt-launcher pod name
            pod_cmd = f"oc get pods -n {self._environment_variables_dict['namespace']} -l kubevirt.io=virt-launcher -o name | grep {vm_name}"
            result = subprocess.run(pod_cmd, shell=True, capture_output=True, text=True)
            pod_name = result.stdout.strip().replace('pod/', '')

            if not pod_name:
                logger.error(f"Could not find virt-launcher pod for VM {vm_name}")
                return None

            # Extract file from compute container
            extract_cmd = f"oc exec -n {self._environment_variables_dict['namespace']} {pod_name} -c compute -- cat {file_path}"
            result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Failed to extract {file_path} from VM {vm_name}: {result.stderr}")
                return None

            return result.stdout

        except Exception as e:
            logger.error(f"Exception extracting file from VM: {e}")
            return None

    def _parse_uperf_output(self, uperf_output, server_ip, server_node):
        """
        Parse uperf output and return metrics

        Args:
            uperf_output: Raw uperf output text
            server_ip: Server IP address
            server_node: Server node name

        Returns:
            Dictionary with parsed metrics
        """
        # Default values
        metrics = {
            'uuid': self._uuid,
            'workload': 'uperf',
            'kind': 'vm',
            'test_type': 'stream',
            'protocol': 'tcp',
            'message_size': 64,
            'read_message_size': 64,
            'num_threads': 1,
            'bytes': 0,
            'ops': 0,
            'norm_byte': 0,
            'norm_ops': 0,
            'norm_ltcy': 0.0,
            'duration': 0,
            'throughput_mbps': 0.0,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            'uperf_ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            'user': self._environment_variables_dict.get('test_user', 'ripsaw'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'iteration': 0,
            'client_ips': self._environment_variables_dict.get('client_ips', ''),
            'remote_ip': server_ip,
            'service_ip': self._environment_variables_dict.get('service_ip', 'False'),
            'service_type': self._environment_variables_dict.get('service_type', ''),
            'port': self._environment_variables_dict.get('port', '30000'),
            'client_node': '',
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
            'pod_id': '',
            'hostnetwork': self._environment_variables_dict.get('hostnetwork', 'False')
        }

        if not uperf_output:
            logger.warning("No uperf output to parse")
            return metrics

        # Parse uperf output - look for Txn2 lines with timestamp_ms, nr_bytes, nr_ops
        # Example line: timestamp_ms:1234567890.123 name:Txn2 nr_bytes:1024 nr_ops:16
        pattern = r'timestamp_ms:\s*([\d.]+).*name:Txn2.*nr_bytes:\s*(\d+).*nr_ops:\s*(\d+)'

        result_lines = []
        for line in uperf_output.splitlines():
            match = re.search(pattern, line)
            if match:
                ts, bytes_val, ops_val = match.groups()
                result_lines.append({
                    'timestamp_ms': float(ts),
                    'bytes': int(bytes_val),
                    'ops': int(ops_val)
                })

        if not result_lines:
            logger.warning("No Txn2 data found in uperf output")
            return metrics

        # Get last line (final cumulative values)
        last = result_lines[-1]
        metrics['bytes'] = last['bytes']
        metrics['ops'] = last['ops']

        # Calculate normalized values if we have previous line
        if len(result_lines) >= 2:
            prev = result_lines[-2]
            metrics['norm_byte'] = last['bytes'] - prev['bytes']
            metrics['norm_ops'] = last['ops'] - prev['ops']

            # Calculate normalized latency (ms)
            if metrics['norm_ops'] > 0:
                time_diff_ms = last['timestamp_ms'] - prev['timestamp_ms']
                metrics['norm_ltcy'] = round(time_diff_ms / metrics['norm_ops'] * 1000, 4)
        else:
            metrics['norm_byte'] = metrics['bytes']
            metrics['norm_ops'] = metrics['ops']

        # Duration is number of result lines
        metrics['duration'] = len(result_lines)

        # Calculate throughput
        first = result_lines[0]
        if last['timestamp_ms'] > first['timestamp_ms']:
            duration_sec = (last['timestamp_ms'] - first['timestamp_ms']) / 1000
            if duration_sec > 0 and metrics['bytes'] > 0:
                metrics['throughput_mbps'] = round(metrics['bytes'] * 8 / duration_sec / 1000000, 4)

        # Set uperf timestamp from last result
        metrics['uperf_ts'] = datetime.fromtimestamp(last['timestamp_ms'] / 1000, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

        # Try to get client node from uperf output (hostname line)
        hostname_match = re.search(r'hostname:\s*(\S+)', uperf_output)
        if hostname_match:
            metrics['client_node'] = hostname_match.group(1)

        return metrics

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
        This method runs the uperf VM workload
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set workload type
            self.__kind = 'vm'
            self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            self.__server_vm_name = f'uperf-server-{self._trunc_uuid}'
            self.__client_vm_name = f'uperf-client-{self._trunc_uuid}'

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create VirtualMachines (server + client in one YAML)
            logger.info("Creating uperf server and client VirtualMachines")
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)

            # Wait for server VM to be ready
            logger.info("Waiting for uperf server VM")
            self._oc.wait_for_vm_create(vm_name=self.__server_vm_name)
            self._oc.wait_for_initialized(label=f'app=uperf-server-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=uperf-server-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            logger.info("Server VM is ready, getting server IP")

            # Get server VMI IP - retry until IP is assigned
            server_ip = ""
            max_retries = 30
            for attempt in range(max_retries):
                server_ip_cmd = f"oc get vmi -n {self._environment_variables_dict['namespace']} {self.__server_vm_name} -o jsonpath='{{.status.interfaces[0].ipAddress}}'"
                result = subprocess.run(server_ip_cmd, shell=True, capture_output=True, text=True)
                server_ip = result.stdout.strip().strip("'")
                if server_ip:
                    logger.info(f"Server VMI IP: {server_ip}")
                    break
                logger.info(f"Waiting for server VMI IP (attempt {attempt + 1}/{max_retries})...")
                time.sleep(2)

            if not server_ip:
                raise RuntimeError(f"Failed to get server VMI IP after {max_retries} attempts")

            # Get server VMI node
            server_node_cmd = f"oc get vmi -n {self._environment_variables_dict['namespace']} {self.__server_vm_name} -o jsonpath='{{.status.nodeName}}'"
            result = subprocess.run(server_node_cmd, shell=True, capture_output=True, text=True)
            server_node = result.stdout.strip().strip("'")
            logger.info(f"Server VMI Node: {server_node}")

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

            # Give server a moment to fully start uperf listener
            time.sleep(5)

            # Re-generate YAML with server IP
            from benchmark_runner.common.template_operations.template_operations import TemplateOperations
            template_ops = TemplateOperations(workload=self._workload)
            template_ops.set_environment_variables(self._environment_variables_dict)
            template_ops.generate_yamls()
            logger.info(f"Regenerated client VM YAML with server IP: {server_ip}")

            # Apply the regenerated YAML directly using oc apply to create client VM
            logger.info("Applying regenerated YAML to create client VM with server IP")
            yaml_path = os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml')
            apply_cmd = f"oc apply -f {yaml_path}"
            result = subprocess.run(apply_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to apply YAML: {result.stderr}")
                raise RuntimeError(f"Failed to apply regenerated YAML: {result.stderr}")
            logger.info(f"Applied YAML successfully: {result.stdout}")

            # Wait for client VM to be ready
            logger.info("Waiting for uperf client VM")
            self._oc.wait_for_vm_create(vm_name=self.__client_vm_name)
            self._oc.wait_for_initialized(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            # Wait for client workload to complete by polling for signal file
            logger.info("Waiting for uperf client workload to complete...")
            max_wait = 600  # 10 minutes timeout
            wait_interval = 5
            elapsed = 0
            workload_complete = False

            while elapsed < max_wait:
                # Check if signal file exists on client VM
                signal_check = self._extract_file_from_vm(self.__client_vm_name, '/tmp/workload_complete.signal')
                if signal_check is not None:
                    logger.info("Workload completed (signal file found)")
                    workload_complete = True
                    break
                time.sleep(wait_interval)
                elapsed += wait_interval
                if elapsed % 30 == 0:
                    logger.info(f"Still waiting for workload completion... ({elapsed}s elapsed)")

            if not workload_complete:
                logger.warning(f"Workload did not complete within {max_wait}s timeout")
                self.__status = 'failed'
            else:
                self.__status = 'complete'

            # Extract uperf results from client VM while it's still running
            logger.info(f"Extracting uperf results from client VM: {self.__client_vm_name}")
            uperf_output = self._extract_file_from_vm(self.__client_vm_name, '/tmp/uperf.out')

            # Create vm logs after extraction (VMs still running)
            logger.info("Creating VM logs")
            vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            if self._enable_prometheus_snapshot:
                # Prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__server_vm_name, self.__client_vm_name])

            # Upload results to ElasticSearch
            if self._es_host:

                if uperf_output:
                    # Parse uperf output
                    logger.info("Parsing uperf output")
                    metrics = self._parse_uperf_output(uperf_output, server_ip, server_node)

                    # Upload to ElasticSearch
                    logger.info("Uploading uperf results to ElasticSearch")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    # Verify data was uploaded
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)

                    # Update metadata for each result (if data was found)
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
                    logger.warning("Failed to extract uperf output from client VM, uploading minimal metadata")
                    # Upload minimal metadata even if we couldn't extract results
                    minimal_data = {
                        'uuid': self._uuid,
                        'workload': 'uperf',
                        'kind': self.__kind,
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=minimal_data)

            # Cleanup: delete VirtualMachines
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except Exception as err:
            # Save run artifacts logs
            if self._oc.vm_exists(vm_name=self.__server_vm_name) or self._oc.vm_exists(vm_name=self.__client_vm_name):
                vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
                # Upload error metadata
                data_dict = {
                    'uuid': self._uuid,
                    'workload': 'uperf',
                    'kind': self.__kind,
                    'run_artifacts_url': run_artifacts_url
                }
                self._upload_to_elasticsearch(
                    index=self.__es_index,
                    kind=self.__kind,
                    status='failed',
                    result=data_dict
                )

            # Cleanup on error
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)
            raise err
