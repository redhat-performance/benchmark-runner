
import os
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


