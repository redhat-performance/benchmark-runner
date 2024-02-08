
import time
from datetime import datetime
from typeguard import typechecked
import ast  # change string list to list
from enum import Enum

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger, datetime_format
from benchmark_runner.common.clouds.IBM.ibm_exceptions import IBMMachineNotLoad
from benchmark_runner.common.clouds.BareMetal.bare_metal_operations import BareMetalOperations


class Actions(Enum):
    """
    IBM Actions
    """
    POWER_OFF = 'power-off'
    POWER_ON = 'power-on'
    REBOOT = 'reboot'


class IBMOperations(BareMetalOperations):
    """
    This class is responsible for all IBM cloud operations, all commands run on remote provision IBM host
    """
    SHORT_TIMEOUT = 600

    @typechecked
    def __init__(self, user: str):
        super().__init__(user)
        self._ibm_api_key = self._environment_variables_dict.get('ibm_api_key', '')
        self._ibm_worker_ids = self._environment_variables_dict.get('worker_ids', '')
        self._ibm_worker_ids_list = ast.literal_eval(self._ibm_worker_ids)

    def __ibm_login_cmd(self):
        """
        This method returns ibm login command
        :return:
        """
        return f'ibmcloud login --apikey {self._ibm_api_key} 1>/dev/null 2>&1'

    # private method: machine id
    def __get_ibm_machine_status(self, machine_id: str):
        """
        This method returns IBM machine status
        :return:
        """
        details = self._remote_ssh.run_command(command=f'ibmcloud sl hardware detail {machine_id}')
        item_results = details.split()
        for ind, item in enumerate(item_results):
            if item == 'Status':
                return item_results[ind+1]

    def __async_set_action_ibm_machine(self, action: str, machine_id: str):
        """
        This method reboots IBM machine id
        :param action:
        :param machine_id:
        :return:
        """
        self._remote_ssh.run_command(command=f'ibmcloud sl hardware {action} {machine_id} -f')

    def __wait_for_active_machine(self, machine_id: str, sleep_time=10, timeout=SHORT_TIMEOUT):
        """
        This method waits till IBM machine will be active
        :param machine_id:
        :return:
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self.__get_ibm_machine_status(machine_id=machine_id) == 'ACTIVE':
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise IBMMachineNotLoad()

    @staticmethod
    def __ibm_logout_cmd():
        """
        This method returns ibm logout command
        :return:
        """
        return 'ibmcloud logout'

    def run_ocp_installer(self):
        """
        This method run ocp assisted installer
        :return: True if installation success and raise exception if installation failed
        """
        self.update_provision_config()
        logger.info(f'Starting OCP assisted installer, Start time: {datetime.now().strftime(datetime_format)}')
        # Must add -t otherwise remote ssh of ansible will not end
        self._ssh.run(cmd=f"ssh -t provision \"{self.__ibm_login_cmd()};{self._install_ocp_cmd()}\" ")
        logger.info(f'OpenShift cluster {self._get_installation_version()} version is installed successfully, End time: {datetime.now().strftime(datetime_format)}')
