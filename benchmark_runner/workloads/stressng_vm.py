
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


class StressngVM(WorkloadsOperations):
    """
    This class runs stressng VM workload using direct VirtualMachine creation (no operator).
    Cloud-init installs and runs stress-ng inside the VM guest OS.
    Results are extracted via qemu-guest-agent.
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__vm_name = ''

    def _get_virt_launcher_pod(self):
        """Get the virt-launcher pod name for this VM"""
        namespace = self._environment_variables_dict['namespace']
        cmd = f"oc get pods -n {namespace} -l kubevirt.io=virt-launcher -o name | grep {self.__vm_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        pod_name = result.stdout.strip().replace('pod/', '')
        if not pod_name:
            logger.warning(f"Could not find virt-launcher pod for VM {self.__vm_name}")
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

    def _wait_for_guest_agent(self, timeout=180):
        """Wait for qemu-guest-agent to connect inside the VM"""
        namespace = self._environment_variables_dict['namespace']
        for i in range(timeout):
            cmd = f"oc get vmi -n {namespace} {self.__vm_name} -o jsonpath='{{.status.conditions[?(@.type==\"AgentConnected\")].status}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            status = result.stdout.strip().strip("'")
            if status == 'True':
                logger.info(f"Guest agent connected after {i}s")
                return True
            if i > 0 and i % 30 == 0:
                logger.info(f"Waiting for guest agent... ({i}s)")
            time.sleep(1)
        logger.warning(f"Guest agent did not connect within {timeout}s")
        return False

    def _guest_exec(self, pod_name, domain, command, args=None):
        """
        Execute a command inside the VM via qemu-guest-agent and return stdout.

        Args:
            pod_name: virt-launcher pod name
            domain: libvirt domain name
            command: command path (e.g. /bin/cat)
            args: list of arguments

        Returns:
            stdout as string, or None on failure
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
            logger.warning(f"guest-exec failed (rc={result.returncode}): stderr={result.stderr.strip()}, stdout={result.stdout.strip()}")
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

        # Wait a moment then get the result
        time.sleep(2)
        status_cmd_json = json.dumps({"execute": "guest-exec-status", "arguments": {"pid": pid}})
        cmd = f"oc exec -n {namespace} {pod_name} -c compute -- virsh -c qemu+unix:///session qemu-agent-command {domain} '{status_cmd_json}'"

        # Retry for command completion
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
                logger.warning(f"Failed to parse guest-exec-status response: {e}, raw={result.stdout[:500]}")
                return None
            time.sleep(2)

        logger.warning(f"guest-exec PID {pid} did not complete after 10 retries")
        return None

    def _guest_file_read(self, pod_name, domain, file_path):
        """
        Read a file from inside the VM via guest-file-open/guest-file-read/guest-file-close.
        More reliable than guest-exec + cat for file reading.
        """
        namespace = self._environment_variables_dict['namespace']
        base_cmd = f"oc exec -n {namespace} {pod_name} -c compute -- virsh -c qemu+unix:///session qemu-agent-command {domain}"

        # Open the file
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

        logger.info(f"Opened {file_path} with handle {handle}")

        # Read the file contents (read up to 4MB in chunks)
        content = ''
        for _ in range(100):  # max 100 chunks of 48KB = ~4.8MB
            read_cmd = json.dumps({"execute": "guest-file-read", "arguments": {"handle": handle, "count": 49152}})
            result = subprocess.run(f"{base_cmd} '{read_cmd}'", shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"guest-file-read failed: {result.stderr.strip()}")
                break

            try:
                resp = json.loads(result.stdout)
                ret = resp.get('return', {})
                buf_b64 = ret.get('buf-b64', '')
                eof = ret.get('eof', False)
                if buf_b64:
                    content += base64.b64decode(buf_b64).decode('utf-8', errors='ignore')
                if eof:
                    break
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to parse guest-file-read response: {e}")
                break

        # Close the file
        close_cmd = json.dumps({"execute": "guest-file-close", "arguments": {"handle": handle}})
        subprocess.run(f"{base_cmd} '{close_cmd}'", shell=True, capture_output=True, text=True)

        logger.info(f"Read {len(content)} bytes from {file_path}")
        return content if content else None

    def _parse_stressng_output(self, output):
        """
        Parse stress-ng output and extract metrics

        Args:
            output: Raw stress-ng output text (may include boot messages and other console noise)

        Returns:
            Dictionary with parsed metrics
        """
        metrics = {
            'uuid': self._uuid,
            'workload': 'stressng',
            'kind': 'vm',
            'user': self._environment_variables_dict.get('test_user', 'ripsaw'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'runtype': self._environment_variables_dict.get('runtype', 'all'),
            'timeout': self._environment_variables_dict.get('timeout', 5),
            'cpu_stressors': self._environment_variables_dict.get('cpu_stressors', 1),
            'cpu_percentage': self._environment_variables_dict.get('cpu_percentage', 100),
            'vm_stressors': self._environment_variables_dict.get('vm_stressors', 1),
            'vm_bytes': self._environment_variables_dict.get('vm_bytes', '256M'),
            'mem_stressors': self._environment_variables_dict.get('mem_stressors', 1),
            'cpu_bogomips': 0.0,
            'vm_bogomips': 0.0,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        if not output:
            logger.warning("No stress-ng output to parse")
            return metrics

        # Parse bogo ops from stress-ng metrics-brief output
        # Example: "stress-ng: metrc: [987] cpu               11725     10.01 ..."
        cpu_match = re.search(r'\scpu\s+([\d.]+)', output)
        if cpu_match:
            metrics['cpu_bogomips'] = float(cpu_match.group(1))

        vm_match = re.search(r'\svm\s+([\d.]+)', output)
        if vm_match:
            metrics['vm_bogomips'] = float(vm_match.group(1))

        logger.info(f"Parsed metrics: cpu_bogomips={metrics['cpu_bogomips']}, vm_bogomips={metrics['vm_bogomips']}")
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
        This method runs the stressng VM workload.
        Cloud-init handles installing and running stress-ng inside the VM.
        Results are extracted via qemu-guest-agent.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set workload type
            self.__kind = 'vm'
            self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci'
            else:
                self.__es_index = 'stressng'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create VirtualMachine (cloud-init will install and run stress-ng)
            logger.info("Creating stressng VirtualMachine")
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)

            # Wait for VM to be ready
            self._oc.wait_for_vm_create(vm_name=self.__vm_name)
            self._oc.wait_for_initialized(label=f'app=stressng-vm-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=stressng-vm-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            logger.info("VirtualMachine is ready, cloud-init will install and run stress-ng inside the VM...")

            # Get cluster name
            cluster_name_cmd = "oc get clusterversion -o jsonpath='{.items[0].spec.clusterID}'"
            result = subprocess.run(cluster_name_cmd, shell=True, capture_output=True, text=True)
            cluster_name = result.stdout.strip().strip("'")
            if not cluster_name:
                cluster_name_cmd = "oc get infrastructure cluster -o jsonpath='{.status.infrastructureName}'"
                result = subprocess.run(cluster_name_cmd, shell=True, capture_output=True, text=True)
                cluster_name = result.stdout.strip().strip("'")

            self._environment_variables_dict['clustername'] = cluster_name
            self._environment_variables_dict['test_user'] = os.environ.get('TEST_USER', 'ripsaw')
            self._environment_variables_dict['run_id'] = os.environ.get('RUN_ID', 'NA')

            # Wait for guest agent to connect (cloud-init installs qemu-guest-agent)
            logger.info("Waiting for qemu-guest-agent to connect...")
            agent_ready = self._wait_for_guest_agent(timeout=180)

            # Find virt-launcher pod and domain
            pod_name = self._get_virt_launcher_pod()
            domain = self._get_vm_domain(pod_name) if pod_name else ''

            if not agent_ready or not pod_name or not domain:
                logger.warning(f"Guest agent setup incomplete: agent={agent_ready}, pod={pod_name}, domain={domain}")

            # Wait for stress-ng to complete by polling for signal file via guest agent
            # Use stressng_timeout (dedicated var) to avoid collision with general workload timeout
            stressng_timeout = int(self._environment_variables_dict.get('stressng_timeout', 30))
            max_wait = stressng_timeout + 180  # stress-ng timeout + boot/install/agent buffer
            logger.info(f"Waiting up to {max_wait}s for stress-ng completion (stress-ng timeout={stressng_timeout}s)...")

            workload_complete = False
            poll_interval = 5
            for elapsed in range(0, max_wait, poll_interval):
                if pod_name and domain:
                    # Check for signal file via guest agent
                    check_result = self._guest_exec(pod_name, domain, '/bin/test', ['-f', '/opt/stressng/workload_complete.signal'])
                    if check_result is not None:
                        logger.info(f"stress-ng completed (signal file found after {elapsed}s)")
                        workload_complete = True
                        break
                if elapsed > 0 and elapsed % 30 == 0:
                    logger.info(f"Still waiting for stress-ng completion... ({elapsed}s)")
                time.sleep(poll_interval)

            self.__status = 'complete' if workload_complete else 'failed'

            if not workload_complete:
                logger.warning(f"Timed out after {max_wait}s waiting for stress-ng completion")
                # Run diagnostics to understand what happened inside the VM
                if pod_name and domain:
                    logger.info("=== DIAGNOSTICS: checking VM state ===")
                    ls_result = self._guest_exec(pod_name, domain, '/bin/ls', ['-la', '/opt/stressng/'])
                    if ls_result is not None:
                        logger.info(f"ls /root/:\n{ls_result}")
                    ps_result = self._guest_exec(pod_name, domain, '/bin/bash', ['-c', 'ps aux | grep -E "stress|cloud-init" | grep -v grep'])
                    if ps_result is not None:
                        logger.info(f"Running processes:\n{ps_result}")
                    cloud_log = self._guest_exec(pod_name, domain, '/bin/bash', ['-c', 'tail -30 /var/log/cloud-init-output.log 2>/dev/null || echo "no cloud-init log"'])
                    if cloud_log is not None:
                        logger.info(f"Cloud-init output (last 30 lines):\n{cloud_log}")
                    # Check if output file exists even without signal
                    logger.info("Checking if stressng_output.txt exists despite missing signal...")

            # Extract stress-ng results via guest agent
            stressng_output = None
            if pod_name and domain:
                # Try guest-exec (cat) first
                logger.info("Extracting stress-ng results via guest-exec...")
                stressng_output = self._guest_exec(pod_name, domain, '/bin/cat', ['/opt/stressng/output.txt'])

                # Fallback to guest-file-read if guest-exec failed
                if not stressng_output:
                    logger.info("guest-exec failed, trying guest-file-read fallback...")
                    stressng_output = self._guest_file_read(pod_name, domain, '/opt/stressng/output.txt')

                if stressng_output:
                    logger.info(f"Extracted stress-ng output ({len(stressng_output)} bytes)")
                    # Save to run artifacts for debugging
                    output_log = os.path.join(self._run_artifacts_path, f'{self.__vm_name}_stressng_output.log')
                    with open(output_log, 'w') as f:
                        f.write(stressng_output)
                else:
                    logger.warning("Failed to extract stress-ng output via both guest-exec and guest-file-read")

            # Create vm logs
            logger.info("Creating VM logs")
            vm_name = self._create_vm_log(labels=[self.__vm_name])

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__vm_name])

            if self._es_host:
                if stressng_output:
                    # Parse stress-ng output
                    logger.info("Parsing stress-ng output")
                    metrics = self._parse_stressng_output(stressng_output)

                    # Upload to ElasticSearch
                    logger.info("Uploading stress-ng results to ElasticSearch")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    # Verify data was uploaded
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)

                    # Update metadata
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
                    logger.warning("No stress-ng output captured, uploading minimal metadata")
                    minimal_data = {
                        'uuid': self._uuid,
                        'workload': 'stressng',
                        'kind': self.__kind,
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=minimal_data)

            # Cleanup: delete VirtualMachine
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.save_error_logs()
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            raise err

        except Exception as err:
            # Save run artifacts logs
            if self._oc.vm_exists(vm_name=self.__vm_name):
                vm_name = self._create_vm_log(labels=[self.__vm_name])

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
                    data_dict = {
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(
                        index=self.__es_index,
                        kind=self.__kind,
                        status='failed',
                        result=data_dict
                    )
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

            # Cleanup on error
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            raise err
