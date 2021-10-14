
from datetime import time, datetime
from typeguard import typechecked
from tenacity import retry, stop_after_attempt
import ast  # change string list to list
from enum import Enum

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger, datetime_format
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.remote_ssh.remote_ssh import ConnectionData, RemoteSsh
from benchmark_runner.common.ocp_resources.create_ocp_resource import CreateOcpResource
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.github.github_operations import GitHubOperations
from benchmark_runner.common.clouds.IBM.ibm_exceptions import IBMMachineNotLoad, MissingMasterNodes, MissingWorkerNodes


class Actions(Enum):
    """
    IBM Actions
    """
    POWER_OFF = 'power-off'
    POWER_ON = 'power-on'
    REBOOT = 'reboot'


class IBMOperations:
    """
    This class is responsible for all IBM cloud operations, all commands run on remote provision IBM host
    """

    @typechecked
    def __init__(self, user: str):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__ibm_api_key = self.__environment_variables_dict.get('ibm_api_key', '')
        self.__ibm_oc_user = self.__environment_variables_dict.get('provision_oc_user', '')
        self.__ibm_worker_ids = self.__environment_variables_dict.get('worker_ids', '')
        self.__ocp_env_flavor = self.__environment_variables_dict.get('ocp_env_flavor', '')
        self.__ibm_worker_ids_list = ast.literal_eval(self.__ibm_worker_ids)
        # FUNC or PERF
        self.__ocp_env_flavor = self.__environment_variables_dict.get('ocp_env_flavor', '')
        self.__provision_kubeadmin_password_path = self.__environment_variables_dict.get('provision_kubeadmin_password_path', '')
        self.__provision_kubeconfig_path = self.__environment_variables_dict.get('provision_kubeconfig_path', '')
        self.__provision_installer_path = self.__environment_variables_dict.get('provision_installer_path', '')
        self.__provision_installer_cmd = self.__environment_variables_dict.get('provision_installer_cmd', '')
        self.__install_ocp_version = self.__environment_variables_dict.get('install_ocp_version', '')
        self.__ocp_version_build = self.__environment_variables_dict.get('ocp_version_build', '')
        self.__num_ocs_disks = int(self.__environment_variables_dict.get('num_ocs_disk', ''))
        self.__connection_data = ConnectionData(host_name=self.__environment_variables_dict.get('provision_ip', ''),
                                                user_name=user,
                                                port=int(self.__environment_variables_dict.get('provision_port', '')),
                                                timeout=int(
                                                    self.__environment_variables_dict.get('provision_timeout', '')),
                                                ssh_key=self.__environment_variables_dict.get('provision_ssh_key', ''))
        self.__remote_ssh = RemoteSsh(self.__connection_data)
        self.__github_operations = GitHubOperations()

    def __get_kubeadmin_password(self):
        """
        This method return kubeadmin password if exist
        :return:
        """
        if self.__remote_ssh.exist(remote_path=self.__provision_kubeadmin_password_path):
            return self.__remote_ssh.run_command(f'cat {self.__provision_kubeadmin_password_path}')

    def __get_kubeconfig(self):
        """
        This method return kubeconfig if exist
        :return:
        """
        if self.__remote_ssh.exist(remote_path=self.__provision_kubeconfig_path):
            return self.__remote_ssh.run_command(f'cat {self.__provision_kubeconfig_path}')

    def __ibm_login_cmd(self):
        """
        This method return ibm login command
        :return:
        """
        return f'ibmcloud login --apikey {self.__ibm_api_key}'

    # private method: machine id
    def __get_ibm_machine_status(self, machine_id: str):
        """
        This method return IBM machine status
        :return:
        """
        details = self.__remote_ssh.run_command(command=f'ibmcloud sl hardware detail {machine_id}')
        item_results = details.split()
        for ind, item in enumerate(item_results):
            if item == 'Status':
                return item_results[ind+1]

    def __async_set_action_ibm_machine(self, action: str, machine_id: str):
        """
        This method reboot machine id
        :param action:
        :param machine_id:
        :return:
        """
        self.__remote_ssh.run_command(command=f'ibmcloud sl hardware {action} {machine_id} -f')

    def __wait_for_active_machine(self, machine_id: str, sleep_time=10, timeout=600):
        """
        This method wait till machine will be active
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
        This method return ibm logout command
        :return:
        """
        return 'ibmcloud logout'

    def __ibm_ipi_install_ocp_cmd(self):
        """
        This method return ibm ipi installer cmd if exist
        :return:
        """
        if self.__remote_ssh.exist(remote_path=self.__provision_installer_path):
            return self.__provision_installer_cmd

    @logger_time_stamp
    def get_ibm_disks_blk_name(self):
        """
        This method connect to remote provision machine
        :return:
        """
        ibm_blk = ['sdb', 'sdc', 'sdd', 'sde']
        return ibm_blk[:self.__num_ocs_disks]

    @logger_time_stamp
    def ibm_connect(self):
        """
        This method connect to remote provision machine
        :return:
        """
        self.__remote_ssh.connect()

    @logger_time_stamp
    def ibm_disconnect(self):
        """
        This method
        :return:
        """
        self.__remote_ssh.disconnect()

    @logger_time_stamp
    def update_ocp_version(self):
        """
        This method update the ocp version on provision machine
        :return:
        """
        self.__remote_ssh.replace_parameter(remote_path='/ipi-installer/baremetal-deploy/ansible-ipi-install/inventory',
                                            file_name='hosts',
                                            parameter='version=',
                                            value=f'"{self.__install_ocp_version}"')
        self.__remote_ssh.replace_parameter(remote_path='/ipi-installer/baremetal-deploy/ansible-ipi-install/inventory',
                                            file_name='hosts',
                                            parameter='build=',
                                            value=f'"{self.__ocp_version_build}"')

    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def run_ibm_ocp_ipi_installer(self):
        """
        This method run ocp ipi installer with retry mechanism
        :return: True if installation success and raise exception if installation failed
        """
        logger.info(f'Starting OCP IPI installer, Start time: {datetime.now().strftime(datetime_format)}')
        result = self.__remote_ssh.run_command(
           f'{self.__ibm_login_cmd()};{self.__ibm_ipi_install_ocp_cmd()};{self.__ibm_logout_cmd()}')
        if 'failed=1' in result:
            # Workers issue: workaround for solving IBM workers stuck on BIOS page after reboot
            logger.info('Installation failed, checking worker nodes status')
            # Check if first worker is down
            if self.__get_ibm_machine_status(machine_id=self.__ibm_worker_ids_list()[0]) != 'ACTIVE':
                logger.info('One Worker is down, reboot all workers')
                # reboot all not active workers
                for worker_id in self.__ibm_worker_ids_list():
                    if self.__get_ibm_machine_status(machine_id=worker_id) != 'ACTIVE':
                        self.__async_set_action_ibm_machine(action=Actions.REBOOT.value, machine_id=worker_id)
                # Wait till all worker will be active
                for worker_id in self.__ibm_worker_ids_list():
                    self.__wait_for_active_machine(machine_id=worker_id)
                logger.info('All workers are up and running now')
                return True
            # Another issue that is not related to workers
            else:
                logger.info('Installation failed, retry again')
                raise Exception(f'Installation failed after 3 retries')

        else:
            return True

    @logger_time_stamp
    def oc_login(self):
        """
        This method login to the cluster with new credentials
        :return:
        """
        oc = OC(kubeadmin_password=self.__get_kubeadmin_password())
        oc.login()
        return oc

    @logger_time_stamp
    def verify_cluster_is_up(self, oc: OC):
        """
        This method verify that master/worker nodes are up and running
        :return:
        """
        master_nodes = oc.get_master_nodes()
        # master always are 3
        if len(master_nodes.split()) == 3:
            logger.info('master nodes are up and running')
            if self.__ocp_env_flavor == 'PERF':
                worker_nodes = oc.get_worker_nodes()
                # In perf we have more than 1 worker
                if len(worker_nodes.split()) >= 1:
                    logger.info('worker nodes are up and running')
                else:
                    raise MissingWorkerNodes()
        else:
            raise MissingMasterNodes()

    @staticmethod
    @logger_time_stamp
    @typechecked
    def install_ocp_resources(resources: list, ibm_blk_disk_name: list = []):
        """
        This method install OCP resources 'cnv', 'local_storage', 'ocs'
        :param ibm_blk_disk_name: ibm blk disk name
        :param resources:
        :return:
        """
        create_ocp_resource = CreateOcpResource()
        for resource in resources:
            create_ocp_resource.create_resource(resource=resource, ibm_blk_disk_name=ibm_blk_disk_name)

    @logger_time_stamp
    def update_ocp_github_credentials(self):
        """
        This method update github secrets kubeconfig and kubeadmin_password
        :return:
        """
        self.__github_operations.create_secret(secret_name=f'{self.__ocp_env_flavor}_KUBECONFIG', unencrypted_value=self.__get_kubeconfig())
        self.__github_operations.create_secret(secret_name=f'{self.__ocp_env_flavor}_KUBEADMIN_PASSWORD',
                                                unencrypted_value=self.__get_kubeadmin_password())
