
import base64
import json
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
    This class runs uperf VM workload using direct VirtualMachine creation (no operator).
    Cloud-init installs and runs uperf inside the VM guest OS.
    Results are extracted via qemu-guest-agent.
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

    def _get_virt_launcher_pod(self, vm_name):
        """Get the virt-launcher pod name for a VM"""
        namespace = self._environment_variables_dict['namespace']
        cmd = f"oc get pods -n {namespace} -l kubevirt.io=virt-launcher -o name | grep {vm_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        pod_name = result.stdout.strip().replace('pod/', '')
        if not pod_name:
            logger.warning(f"Could not find virt-launcher pod for VM {vm_name}")
        return pod_name

    def _get_vm_domain(self, pod_name):
        """Get the libvirt domain name from the virt-launcher pod"""
        namespace = self._environment_variables_dict['namespace']
        cmd = f"oc exec -n {namespace} {pod_name} -c compute -- virsh -c qemu+unix:///session list --name"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        domain = result.stdout.strip()
        if not domain:
            logger.warning(f"Could not get libvirt domain name from pod {pod_name}")
        return domain

    def _wait_for_guest_agent(self, vm_name, timeout=180):
        """Wait for qemu-guest-agent to connect inside the VM"""
        namespace = self._environment_variables_dict['namespace']
        for i in range(timeout):
            cmd = f"oc get vmi -n {namespace} {vm_name} -o jsonpath='{{.status.conditions[?(@.type==\"AgentConnected\")].status}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            status = result.stdout.strip().strip("'")
            if status == 'True':
                logger.info(f"Guest agent connected on {vm_name} after {i}s")
                return True
            if i > 0 and i % 30 == 0:
                logger.info(f"Waiting for guest agent on {vm_name}... ({i}s)")
            time.sleep(1)
        logger.warning(f"Guest agent on {vm_name} did not connect within {timeout}s")
        return False

    def _guest_exec(self, pod_name, domain, command, args=None):
        """
        Execute a command inside the VM via qemu-guest-agent and return stdout.
        """
        namespace = self._environment_variables_dict['namespace']

        exec_args = {"path": command, "capture-output": True}
        if args:
            exec_args["arg"] = args

        ga_cmd = json.dumps({"execute": "guest-exec", "arguments": exec_args})
        cmd = f"oc exec -n {namespace} {pod_name} -c compute -- virsh -c qemu+unix:///session qemu-agent-command {domain} '{ga_cmd}'"
        logger.info(f"guest-exec: {command} {args or ''}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logger.warning(f"guest-exec failed (rc={result.returncode}): stderr={result.stderr.strip()}")
            return None

        try:
            resp = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse guest-exec response: {result.stdout[:500]}")
            return None

        pid = resp.get('return', {}).get('pid')
        if pid is None:
            logger.warning(f"No PID in guest-exec response: {resp}")
            return None

        logger.info(f"guest-exec started with PID {pid}, waiting for completion...")
        time.sleep(2)

        status_cmd_json = json.dumps({"execute": "guest-exec-status", "arguments": {"pid": pid}})
        cmd = f"oc exec -n {namespace} {pod_name} -c compute -- virsh -c qemu+unix:///session qemu-agent-command {domain} '{status_cmd_json}'"

        for attempt in range(10):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"guest-exec-status failed (rc={result.returncode}): {result.stderr.strip()}")
                return None
            try:
                status_resp = json.loads(result.stdout)
                ret = status_resp.get('return', {})
                if ret.get('exited', False):
                    exitcode = ret.get('exitcode', -1)
                    out_data = ret.get('out-data', '')
                    err_data = ret.get('err-data', '')
                    logger.info(f"guest-exec completed: exitcode={exitcode}, out-data-len={len(out_data)}, err-data-len={len(err_data)}")
                    if err_data:
                        logger.info(f"guest-exec stderr: {base64.b64decode(err_data).decode('utf-8', errors='ignore')[:200]}")
                    if out_data:
                        return base64.b64decode(out_data).decode('utf-8', errors='ignore')
                    return '' if exitcode == 0 else None
                else:
                    logger.info(f"guest-exec PID {pid} still running (attempt {attempt + 1}/10)...")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse guest-exec-status response: {e}")
                return None
            time.sleep(2)

        logger.warning(f"guest-exec PID {pid} did not complete after 10 retries")
        return None

    def _guest_file_read(self, pod_name, domain, file_path):
        """
        Read a file from inside the VM via guest-file-open/guest-file-read/guest-file-close.
        """
        namespace = self._environment_variables_dict['namespace']
        base_cmd = f"oc exec -n {namespace} {pod_name} -c compute -- virsh -c qemu+unix:///session qemu-agent-command {domain}"

        open_cmd = json.dumps({"execute": "guest-file-open", "arguments": {"path": file_path, "mode": "r"}})
        result = subprocess.run(f"{base_cmd} '{open_cmd}'", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"guest-file-open failed: {result.stderr.strip()}")
            return None

        try:
            resp = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse guest-file-open response: {result.stdout[:200]}")
            return None

        handle = resp.get('return')
        if handle is None:
            logger.warning(f"No file handle in guest-file-open response: {resp}")
            return None

        content = ''
        for _ in range(100):
            read_cmd = json.dumps({"execute": "guest-file-read", "arguments": {"handle": handle, "count": 49152}})
            result = subprocess.run(f"{base_cmd} '{read_cmd}'", shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                break
            try:
                resp = json.loads(result.stdout)
                ret = resp.get('return', {})
                buf_b64 = ret.get('buf-b64', '')
                if buf_b64:
                    content += base64.b64decode(buf_b64).decode('utf-8', errors='ignore')
                if ret.get('eof', False):
                    break
            except Exception as e:
                logger.warning(f"Failed to parse guest-file-read response: {e}")
                break

        close_cmd = json.dumps({"execute": "guest-file-close", "arguments": {"handle": handle}})
        subprocess.run(f"{base_cmd} '{close_cmd}'", shell=True, capture_output=True, text=True)

        logger.info(f"Read {len(content)} bytes from {file_path}")
        return content if content else None

    def _extract_from_vm(self, vm_name, file_path):
        """
        Extract a file from a VM using guest-agent (guest-exec + guest-file-read fallback).
        """
        pod_name = self._get_virt_launcher_pod(vm_name)
        if not pod_name:
            return None
        domain = self._get_vm_domain(pod_name)
        if not domain:
            return None

        # Try guest-exec first
        result = self._guest_exec(pod_name, domain, '/bin/cat', [file_path])
        if result:
            return result

        # Fallback to guest-file-read
        logger.info("guest-exec failed, trying guest-file-read fallback...")
        return self._guest_file_read(pod_name, domain, file_path)

    def _parse_single_uperf_result(self, output_section, server_ip, server_node, test_type='stream', protocol='tcp', message_size=64, num_threads=1):
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

                # 95th percentile latency from per-second samples (snafu formula)
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
                    idx = min(int(len(lat_samples) * 0.95), len(lat_samples) - 1)
                    metrics['norm_ltcy'] = round(lat_samples[idx], 4)

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

    def _parse_uperf_output(self, uperf_output, server_ip, server_node):
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

            # Get cluster name
            cluster_name_cmd = "oc get clusterversion -o jsonpath='{.items[0].spec.clusterID}'"
            result = subprocess.run(cluster_name_cmd, shell=True, capture_output=True, text=True)
            cluster_name = result.stdout.strip().strip("'")
            if not cluster_name:
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

            # Delete the client VM that was created with empty server_ip, then recreate with correct IP
            logger.info("Deleting client VM (created with empty server_ip) before recreating...")
            namespace = self._environment_variables_dict['namespace']
            delete_cmd = f"oc delete vm {self.__client_vm_name} -n {namespace} --ignore-not-found"
            subprocess.run(delete_cmd, shell=True, capture_output=True, text=True)
            # Wait for client VM to be fully deleted
            for _ in range(30):
                if not self._oc.vm_exists(vm_name=self.__client_vm_name):
                    break
                time.sleep(1)

            # Apply the regenerated YAML to create client VM with correct server IP
            logger.info(f"Creating client VM with server IP: {server_ip}")
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

            # Wait for guest agent on client VM
            logger.info("Waiting for guest agent on client VM...")
            self._wait_for_guest_agent(self.__client_vm_name, timeout=180)

            # Wait for client workload to complete by polling for signal file via guest agent
            logger.info("Waiting for uperf client workload to complete...")
            max_wait = 600  # 10 minutes timeout
            poll_interval = 5
            workload_complete = False

            # Get client VM's virt-launcher pod and domain for guest-exec
            client_pod = self._get_virt_launcher_pod(self.__client_vm_name)
            client_domain = self._get_vm_domain(client_pod) if client_pod else ''

            for elapsed in range(0, max_wait, poll_interval):
                if client_pod and client_domain:
                    check_result = self._guest_exec(client_pod, client_domain, '/bin/test', ['-f', '/opt/uperf/workload_complete.signal'])
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

            # Diagnostic: read the actual test.xml to debug parsing issues
            if client_pod and client_domain:
                test_xml = self._guest_exec(client_pod, client_domain, '/bin/cat', ['/opt/uperf/test.xml'])
                if test_xml:
                    logger.info(f"test.xml content:\n{test_xml}")
                else:
                    logger.warning("Could not read test.xml from client VM")

            # Extract uperf results from client VM via guest agent
            uperf_output = None
            if client_pod and client_domain:
                logger.info(f"Extracting uperf results from client VM: {self.__client_vm_name}")
                uperf_output = self._guest_exec(client_pod, client_domain, '/bin/cat', ['/opt/uperf/output.txt'])
                if not uperf_output:
                    logger.info("guest-exec failed, trying guest-file-read fallback...")
                    uperf_output = self._guest_file_read(client_pod, client_domain, '/opt/uperf/output.txt')

                if uperf_output:
                    logger.info(f"Extracted uperf output ({len(uperf_output)} bytes):\n{uperf_output}")
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
