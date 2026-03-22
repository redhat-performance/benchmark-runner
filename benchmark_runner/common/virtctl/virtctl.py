
import os
import subprocess
import tempfile
import time
from typing import Optional
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc import OC, VMStatus
from benchmark_runner.main.environment_variables import environment_variables


class Virtctl(OC):
    """
    Interface to virtctl command
    """

    def __init__(self):
        super().__init__()

    @typechecked
    def generate_ssh_key(self, key_path: str = '') -> str:
        """
        Generate a temporary SSH keypair for virtctl ssh access to VMs.
        Returns the path to the private key.
        """
        if not key_path:
            key_path = os.path.join(tempfile.mkdtemp(), 'vm_key')
        if not os.path.exists(key_path):
            subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', key_path, '-N', ''],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Generated SSH keypair at {key_path}")
        return key_path

    @typechecked
    def get_ssh_public_key(self, key_path: str) -> str:
        """
        Read and return the SSH public key content.
        """
        pub_path = f"{key_path}.pub"
        with open(pub_path, 'r') as f:
            return f.read().strip()

    @typechecked
    def virtctl_ssh(self, vm_name: str, command: str, namespace: str = '', key_path: str = '', username: str = '') -> Optional[str]:
        """
        Execute a command inside a VM via virtctl ssh.
        Returns stdout string, or None on failure.
        """
        namespace = namespace or environment_variables.environment_variables_dict.get('namespace', '')
        username = username or environment_variables.environment_variables_dict.get('vm_user', 'root')
        try:
            if self.is_virtctl_ge(min_version="1.6.0"):
                target = f'vmi/{vm_name}'
            else:
                target = vm_name
            result = subprocess.run(
                ['virtctl', '-n', namespace, 'ssh', f'--username={username}', f'--identity-file={key_path}',
                 '-t', '-o StrictHostKeyChecking=no', '-t', '-o UserKnownHostsFile=/dev/null',
                 f'--command={command}', target],
                capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return result.stdout
            else:
                stderr = result.stderr.strip()
                if 'connection refused' in stderr or 'no route to host' in stderr:
                    pass  # VM booting, expected
                elif 'Permanently added' in stderr and not result.stdout.strip():
                    pass  # Command ran but returned non-zero (e.g., test -f on missing file)
                else:
                    if result.stdout.strip():
                        return result.stdout
                    logger.warning(f"virtctl ssh failed: {stderr[:200]}")
                return None
        except Exception as e:
            logger.warning(f"virtctl ssh error: {e}")
            return None

    @typechecked
    def ssh_ready(self, vm_name: str, namespace: str = '', key_path: str = '', username: str = '') -> bool:
        """
        Check if SSH is accessible on a VM.
        """
        result = self.virtctl_ssh(vm_name=vm_name, command='echo ready', namespace=namespace, key_path=key_path, username=username)
        return result is not None and 'ready' in result

    @typechecked
    def wait_for_virtctl_ssh(self, vm_name: str, namespace: str = '', key_path: str = '', username: str = '', timeout: int = 180) -> bool:
        """
        Wait for SSH to be accessible on a VM via virtctl.
        """
        for i in range(0, timeout, 5):
            if self.ssh_ready(vm_name=vm_name, namespace=namespace, key_path=key_path, username=username):
                logger.info(f"SSH ready on {vm_name} after {i}s")
                return True
            if i > 0 and i % 30 == 0:
                logger.info(f"Waiting for SSH on {vm_name}... ({i}s)")
            time.sleep(5)
        logger.warning(f"SSH on {vm_name} not ready within {timeout}s")
        return False

    @typechecked
    def wait_for_file_created(self, vm_name: str, file_path: str, namespace: str = '', key_path: str = '', username: str = '', timeout: int = int(environment_variables.environment_variables_dict.get('timeout', 3600))) -> bool:
        """
        Poll until a file exists inside the VM via SSH.
        Used to wait for workload completion (JSON output file = workload done).
        """
        poll_interval = 5
        for elapsed in range(0, timeout, poll_interval):
            check_result = self.virtctl_ssh(vm_name=vm_name, command=f'test -f {file_path} && echo done', namespace=namespace, key_path=key_path, username=username)
            if check_result is not None and 'done' in check_result:
                logger.info(f"File {file_path} found on {vm_name} after {elapsed}s")
                return True
            if elapsed > 0 and elapsed % 30 == 0:
                logger.info(f"Waiting for {file_path} on {vm_name}... ({elapsed}s)")
            time.sleep(poll_interval)
        logger.warning(f"File {file_path} not found on {vm_name} within {timeout}s")
        return False

    @typechecked
    def scp_file(self, vm_name: str, remote_path: str, local_path: str, namespace: str = '', key_path: str = '', username: str = '') -> bool:
        """
        Copy a file from VM to local using virtctl scp.
        """
        namespace = namespace or environment_variables.environment_variables_dict.get('namespace', '')
        username = username or environment_variables.environment_variables_dict.get('vm_user', 'root')
        try:
            if self.is_virtctl_ge(min_version="1.6.0"):
                source = f'{username}@vmi/{vm_name}:{remote_path}'
            else:
                source = f'{username}@{vm_name}:{remote_path}'
            result = subprocess.run(
                ['virtctl', '-n', namespace, 'scp', f'--identity-file={key_path}',
                 '-t', '-o StrictHostKeyChecking=no', '-t', '-o UserKnownHostsFile=/dev/null',
                 source, local_path],
                capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                logger.info(f"SCP {remote_path} from {vm_name} to {local_path}")
                return True
            else:
                logger.warning(f"virtctl scp failed: {result.stderr.strip()[:200]}")
                return False
        except Exception as e:
            logger.warning(f"virtctl scp error: {e}")
            return False

    @typechecked
    def wait_for_vm_workload_completed(self, vm_name: str, file_path: str, local_path: str, namespace: str = '', key_path: str = '', username: str = '', timeout: int = int(environment_variables.environment_variables_dict.get('timeout', 3600))) -> bool:
        """
        Wait for workload completion (file exists) then SCP result file to local.
        Combines: wait_for_virtctl_ssh + wait_for_file_created + scp_file
        """
        # Wait for SSH to be ready
        if not self.wait_for_virtctl_ssh(vm_name=vm_name, namespace=namespace, key_path=key_path, username=username, timeout=180):
            logger.warning(f"SSH never became ready on {vm_name}")
            return False
        # Wait for result file
        if not self.wait_for_file_created(vm_name=vm_name, file_path=file_path, namespace=namespace, key_path=key_path, username=username, timeout=timeout):
            return False
        # SCP result file to local
        return self.scp_file(vm_name=vm_name, remote_path=file_path, local_path=local_path, namespace=namespace, key_path=key_path, username=username)

    @typechecked
    @logger_time_stamp
    def save_vm_log(self, vm_name: str, output_filename: str = '', namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method save vm log in log_path
        :param vm_name: vm name with uuid
        :param output_filename:
        """
        if not output_filename:
            output_filename = os.path.join(self._run_artifacts, vm_name)
        namespace = f'-n {namespace}' if namespace else ''
        self.run(cmd=f"virtctl console {namespace} {vm_name} > {output_filename}", background=True)

    @typechecked
    @logger_time_stamp
    def stop_vm_async(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        The method stop vm
        @param vm_name:
        @param namespace:
        @return: command output
        """
        namespace = f'-n {namespace}' if namespace else ''
        return self.run(cmd=f'virtctl stop {vm_name} {namespace}')

    @typechecked
    @logger_time_stamp
    def stop_vm_sync(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        The method stop vm and wait till stopped
        @param vm_name:
        @return: True or Error
        """
        self.stop_vm_async(vm_name=vm_name, namespace=namespace)
        return self.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Stopped, namespace=namespace)

    @typechecked
    @logger_time_stamp
    def start_vm_async(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        The method start vm
        @param vm_name:
        @param namespace:
        @return: command output
        """
        namespace = f'-n {namespace}' if namespace else ''
        return self.run(cmd=f'virtctl start {vm_name} {namespace}')

    @typechecked
    @logger_time_stamp
    def start_vm_sync(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        The method start vm and wait till running
        @param vm_name:
        @return: True or Error
        """
        self.start_vm_async(vm_name=vm_name, namespace=namespace)
        return self.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Running, namespace=namespace)

    @typechecked
    @logger_time_stamp
    def expose_vm(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        The method expose vm
        @param vm_name:
        """
        namespace = f'-n {namespace}' if namespace else ''
        self.run(cmd=f'virtctl expose vm {vm_name} --name {vm_name} {namespace} --port 27022 --target-port 22 --type NodePort')
