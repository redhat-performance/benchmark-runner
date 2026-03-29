
import os
import re
import time
from datetime import datetime, timezone
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class UperfVM(WorkloadsOperations):
    """
    This class runs uperf VM workload using direct VirtualMachine creation (no operator).
    Cloud-init installs and runs uperf inside the VM guest OS.
    Results are extracted via qemu-guest-agent.
    """
    def __init__(self):
        super().__init__()
        self.__name = self._workload
        self.__workload_name = self._workload.replace('_', '-')
        self.__es_index = ''
        self.__kind = 'vm'
        self.__status = ''
        self.__server_vm_name = f'uperf-server-{self._trunc_uuid}'
        self.__client_vm_name = f'uperf-client-{self._trunc_uuid}'
        self.__template_ops = TemplateOperations(workload=self._workload)

    @typechecked
    def _parse_single_uperf_result(self, output_section: str, server_ip: str, server_node: str, test_type: str = 'stream', protocol: str = 'tcp', message_size: int = 64, num_threads: int = 1) -> dict:
        """
        Parse a single uperf test result section and return metrics dict.
        """
        metrics = {
            'uuid': self._uuid,
            'workload': 'uperf',
            'kind': 'vm',
            'test_type': test_type,
            'protocol': protocol,
            'message_size': message_size,
            'read_message_size': message_size,
            'num_threads': num_threads,
            'bytes': 0,
            'ops': 0,
            'norm_byte': 0,
            'norm_ops': 0,
            'norm_ltcy': 0.0,
            'duration': 0,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            'uperf_ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            'user': self._environment_variables_dict.get('test_user', 'user'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'iteration': 0,
            'client_ips': self._environment_variables_dict.get('client_ips', ''),
            'remote_ip': server_ip,
            'service_ip': self._environment_variables_dict.get('service_ip', 'False'),
            'service_type': self._environment_variables_dict.get('service_type', ''),
            'port': self._environment_variables_dict.get('port', '30000'),
            'client_node': self._environment_variables_dict.get('client_node', ''),
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

        # Primary: parse timestamp_ms lines (from -v -a -R flags, same as snafu)
        # Format: "timestamp_ms:1234.5 name:Txn2 nr_bytes:123 nr_ops:456"
        ts_results = re.findall(r'timestamp_ms:([\d.]+)\s+name:Txn2\s+nr_bytes:(\d+)\s+nr_ops:(\d+)', output_section)

        if len(ts_results) > 1:
            # Compute totals from timestamp_ms data (last entry has cumulative totals)
            first_ts = float(ts_results[0][0])
            last_ts = float(ts_results[-1][0])
            total_bytes = int(ts_results[-1][1])
            total_ops = int(ts_results[-1][2])
            duration_sec = (last_ts - first_ts) / 1000.0

            if duration_sec > 0:
                avg_byte = total_bytes / duration_sec
                avg_ops = total_ops / duration_sec
                throughput_gbps = round((avg_byte * 8) / (1024**3), 4)

                metrics['bytes'] = total_bytes
                metrics['norm_byte'] = avg_byte
                metrics['ops'] = total_ops
                metrics['norm_ops'] = avg_ops
                metrics['duration'] = int(duration_sec)

                # 95th percentile latency from per-second samples
                lat_samples = []
                prev_ts, prev_ops = float(ts_results[0][0]), int(ts_results[0][2])
                for ts_str, _, ops_str in ts_results[1:]:
                    ts, ops = float(ts_str), int(ops_str)
                    norm_ops = ops - prev_ops
                    if norm_ops > 0 and prev_ts > 0:
                        norm_ltcy = ((ts - prev_ts) / norm_ops) * 1000
                        lat_samples.append(norm_ltcy)
                    prev_ts, prev_ops = ts, ops
                if lat_samples:
                    lat_samples.sort()
                    rank = 0.95 * (len(lat_samples) - 1)
                    lower = int(rank)
                    frac = rank - lower
                    metrics['norm_ltcy'] = round(lat_samples[lower] + frac * (lat_samples[min(lower + 1, len(lat_samples) - 1)] - lat_samples[lower]), 4)

                logger.info(f"  {test_type}-{protocol}-{message_size}-{num_threads}: "
                            f"Average byte={avg_byte:.1f}, Average ops={avg_ops:.1f}, "
                            f"throughput={throughput_gbps}Gbps"
                            + (f", 95%ile latency={metrics['norm_ltcy']}ms" if metrics['norm_ltcy'] > 0 else ''))
            else:
                logger.warning(f"  {test_type}-{protocol}-{message_size}-{num_threads}: duration=0")
        else:
            # Fallback: parse Txn2 summary line (non-verbose output)
            txn2_summary = re.search(r'Txn2\s+([\d.]+)(K|KB|M|MB|G|GB)\s*/\s*([\d.]+)\(s\)\s*=\s*([\d.]+)(Kb|Mb|Gb)/s\s+([\d.]+)op/s', output_section)
            if txn2_summary:
                data_val, data_unit, duration_s, tp_val, tp_unit, ops_s = txn2_summary.groups()
                multipliers = {'K': 1024, 'KB': 1024, 'M': 1024**2, 'MB': 1024**2, 'G': 1024**3, 'GB': 1024**3}
                total_bytes = int(float(data_val) * multipliers.get(data_unit, 1))
                duration_sec = float(duration_s)
                total_ops = int(float(ops_s) * duration_sec)
                avg_byte = total_bytes / duration_sec if duration_sec > 0 else 0
                avg_ops = total_ops / duration_sec if duration_sec > 0 else 0
                throughput_gbps = round((avg_byte * 8) / (1024**3), 4) if avg_byte > 0 else 0
                metrics['bytes'] = total_bytes
                metrics['norm_byte'] = avg_byte
                metrics['ops'] = total_ops
                metrics['norm_ops'] = avg_ops
                metrics['duration'] = int(duration_sec)
                logger.info(f"  {test_type}-{protocol}-{message_size}-{num_threads}: "
                            f"Average byte={avg_byte:.1f}, throughput={throughput_gbps}Gbps (summary fallback)")
            else:
                logger.warning(f"  {test_type}-{protocol}-{message_size}-{num_threads}: No Txn2 data found")

        return metrics

    @typechecked
    def _parse_uperf_output(self, uperf_output: str, server_ip: str, server_node: str) -> list:
        """
        Parse uperf output containing one or more test results.
        Returns a list of metrics dicts (one per test).
        """
        if not uperf_output:
            logger.warning("No uperf output to parse")
            return []

        # Split output by test markers: "=== TEST stream-tcp-64-64-1 ==="
        test_sections = re.split(r'=== TEST (\S+) ===', uperf_output)

        results = []
        # test_sections: ['preamble', 'stream-tcp-64-64-1', 'output1', 'rr-tcp-64-64-1', 'output2', ...]
        i = 1
        while i < len(test_sections) - 1:
            test_name = test_sections[i]
            test_output = test_sections[i + 1]
            i += 2

            # Parse test name: test_type-proto-size-readsize-nthreads
            parts = test_name.split('-')
            if len(parts) >= 5:
                test_type = parts[0]
                protocol = parts[1]
                message_size = int(parts[2])
                num_threads = int(parts[4])
            else:
                test_type, protocol, message_size, num_threads = 'stream', 'tcp', 64, 1

            logger.info(f"Parsing test: {test_name}")
            metrics = self._parse_single_uperf_result(
                test_output, server_ip, server_node,
                test_type=test_type, protocol=protocol,
                message_size=message_size, num_threads=num_threads
            )
            results.append(metrics)

        # Fallback: no markers found, parse as single test
        if not results:
            logger.info("No test markers found, parsing as single test")
            metrics = self._parse_single_uperf_result(uperf_output, server_ip, server_node)
            results.append(metrics)

        return results

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
        This method runs the uperf VM workload.
        Cloud-init handles installing and running uperf inside the VMs.
        Results are extracted via qemu-guest-agent.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

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
            namespace = self._environment_variables_dict['namespace']
            server_ip = self._oc.get_vmi_ip(namespace=namespace, vm_name=self.__server_vm_name)
            if not server_ip:
                raise RuntimeError(f"Failed to get server VMI IP")
            logger.info(f"Server VMI IP: {server_ip}")

            # Get server VMI node
            server_node = self._oc.get_vmi_node(namespace=namespace, vm_name=self.__server_vm_name)
            logger.info(f"Server VMI Node: {server_node}")

            # Get cluster name
            cluster_name = self._oc.get_cluster_name()

            # Update environment variables with server info for client template
            self._environment_variables_dict['server_ip'] = server_ip
            self._environment_variables_dict['server_node'] = server_node
            self._environment_variables_dict['clustername'] = cluster_name

            # Give server a moment to fully start uperf listener
            time.sleep(5)

            # Re-generate YAML with server IP
            self.__template_ops.set_environment_variables(self._environment_variables_dict)
            self.__template_ops.generate_yamls()
            logger.info(f"Regenerated client VM YAML with server IP: {server_ip}")

            # Delete the client VM by name (not by YAML, which would delete server too)
            logger.info("Deleting client VM (created with empty server_ip) before recreating...")
            namespace = self._environment_variables_dict['namespace']
            self._oc.delete_vm_by_name(vm_name=self.__client_vm_name, namespace=namespace)
            self._oc.wait_for_vm_delete(vm_name=self.__client_vm_name, namespace=namespace)

            # Apply the regenerated YAML to create client VM with correct server IP
            logger.info(f"Creating client VM with server IP: {server_ip}")
            yaml_path = os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml')
            self._oc.apply_async(yaml=yaml_path)

            # Wait for client VM to be ready
            logger.info("Waiting for uperf client VM")
            self._oc.wait_for_vm_create(vm_name=self.__client_vm_name)
            self._oc.wait_for_initialized(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            # Get client VMI IP and node
            client_ip = self._oc.get_vmi_ip(namespace=namespace, vm_name=self.__client_vm_name)
            client_node = self._oc.get_vmi_node(namespace=namespace, vm_name=self.__client_vm_name)
            logger.info(f"Client VMI IP: {client_ip}, Client VMI Node: {client_node}")
            self._environment_variables_dict['client_ips'] = client_ip + ' ' if client_ip else ''
            self._environment_variables_dict['client_node'] = client_node

            # Wait for guest agent on client VM
            logger.info("Waiting for guest agent on client VM...")
            self._oc.wait_for_guest_agent(vm_name=self.__client_vm_name, namespace=namespace, timeout=180)

            # Wait for client workload to complete by polling for signal file via guest agent
            logger.info("Waiting for uperf client workload to complete...")
            max_wait = self._timeout  # from environment variable (default 3600)
            poll_interval = 5
            workload_complete = False

            # Get client VM's virt-launcher pod and domain for guest-exec
            client_pod = self._oc.get_virt_launcher_pod(vm_name=self.__client_vm_name, namespace=namespace)
            client_domain = self._oc.get_vm_domain(pod_name=client_pod, namespace=namespace) if client_pod else ''

            for elapsed in range(0, max_wait, poll_interval):
                if client_pod and client_domain:
                    check_result = self._oc.guest_exec(pod_name=client_pod, domain=client_domain, command='/bin/test', args=['-f', '/opt/uperf/workload_complete.signal'], namespace=namespace)
                    if check_result is not None:
                        logger.info(f"Workload completed (signal file found after {elapsed}s)")
                        workload_complete = True
                        break
                if elapsed > 0 and elapsed % 30 == 0:
                    logger.info(f"Still waiting for workload completion... ({elapsed}s)")
                time.sleep(poll_interval)

            if not workload_complete:
                logger.warning(f"Workload did not complete within {max_wait}s timeout")
                self.__status = 'failed'
            else:
                self.__status = 'complete'

            # Extract uperf results from client VM via guest agent
            uperf_output = None
            if client_pod and client_domain:
                logger.info(f"Extracting uperf results from client VM: {self.__client_vm_name}")
                uperf_output = self._oc.guest_exec(pod_name=client_pod, domain=client_domain, command='/bin/cat', args=['/opt/uperf/output.txt'], namespace=namespace)
                if not uperf_output:
                    logger.info("guest-exec failed, trying guest-file-read fallback...")
                    uperf_output = self._oc.guest_file_read(pod_name=client_pod, domain=client_domain, file_path='/opt/uperf/output.txt', namespace=namespace)

                if uperf_output:
                    logger.info(f"Extracted uperf output ({len(uperf_output)} bytes)")
                    output_log = os.path.join(self._run_artifacts_path, f'{self.__client_vm_name}_uperf_output.log')
                    with open(output_log, 'w') as f:
                        f.write(uperf_output)
                else:
                    logger.warning("Failed to extract uperf output via guest agent")

            # Create vm logs
            logger.info("Creating VM logs")
            vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__server_vm_name, self.__client_vm_name])

            # Upload results to ElasticSearch
            if self._es_host:
                if uperf_output:
                    logger.info("Parsing uperf output")
                    results_list = self._parse_uperf_output(uperf_output, server_ip, server_node)

                    logger.info(f"Uploading {len(results_list)} uperf results to ElasticSearch")
                    for metrics in results_list:
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

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
                    logger.warning("Failed to extract uperf output from client VM, uploading minimal metadata")
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

        except ElasticSearchDataNotUploaded as err:
            # Cleanup on ES upload failure
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)
            raise err
        except Exception as err:
            # Save run artifacts logs
            if self._oc.vm_exists(vm_name=self.__server_vm_name) or self._oc.vm_exists(vm_name=self.__client_vm_name):
                vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
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
