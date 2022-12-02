
import time
from datetime import datetime
from typeguard import typechecked
import ast  # change string list to list
from enum import Enum

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger, datetime_format
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.remote_ssh.remote_ssh import ConnectionData, RemoteSsh
from benchmark_runner.common.ocp_resources.create_ocp_resource import CreateOCPResource
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.github.github_operations import GitHubOperations
from benchmark_runner.common.clouds.IBM.ibm_exceptions import IBMMachineNotLoad, MissingMasterNodes, MissingWorkerNodes, IBMOCPInstallationFailed
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.common.clouds.IBM.assisted_installer_latest_version import OCPVersions


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
    LATEST = 'latest'
    SHORT_TIMEOUT = 600

    @typechecked
    def __init__(self, user: str):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__ibm_api_key = self.__environment_variables_dict.get('ibm_api_key', '')
        self.__user = user
        self.__ibm_worker_ids = self.__environment_variables_dict.get('worker_ids', '')
        self.__ocp_env_flavor = self.__environment_variables_dict.get('ocp_env_flavor', '')
        self.__ibm_worker_ids_list = ast.literal_eval(self.__ibm_worker_ids)
        # FUNC or PERF
        self.__create_pod_ci_cmd = self.__environment_variables_dict.get('create_pod_ci_cmd', '')
        self.__provision_kubeadmin_password_path = self.__environment_variables_dict.get('provision_kubeadmin_password_path', '')
        self.__provision_kubeconfig_path = self.__environment_variables_dict.get('provision_kubeconfig_path', '')
        self.__provision_installer_path = self.__environment_variables_dict.get('provision_installer_path', '')
        self.__provision_installer_cmd = self.__environment_variables_dict.get('provision_installer_cmd', '')
        self.__provision_installer_log = self.__environment_variables_dict.get('provision_installer_log', '')
        self.__install_ocp_version = self.__environment_variables_dict.get('install_ocp_version', '')
        self.__ocp_version_build = self.__environment_variables_dict.get('ocp_version_build', '')
        self.__num_odf_disks = int(self.__environment_variables_dict.get('num_odf_disk', 1))
        self.__provision_ip = self.__environment_variables_dict.get('provision_ip', '')
        self.__provision_port = int(self.__environment_variables_dict.get('provision_port', ''))
        self.__provision_timeout = int(self.__environment_variables_dict.get('provision_timeout', ''))
        self.__container_private_key_path = self.__environment_variables_dict.get('container_private_key_path', '')
        self.__connection_data = ConnectionData(host_name=self.__provision_ip,
                                                user_name=self.__user,
                                                port=self.__provision_port,
                                                timeout=self.__provision_timeout,
                                                ssh_key=self.__container_private_key_path)
        self.__remote_ssh = RemoteSsh(self.__connection_data)
        self.__github_operations = GitHubOperations()
        self.__ssh = SSH()
        self.__cli = self.__environment_variables_dict.get('cli', '')

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
        return f'ibmcloud login --apikey {self.__ibm_api_key} 1>/dev/null 2>&1'

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

    def __wait_for_active_machine(self, machine_id: str, sleep_time=10, timeout=SHORT_TIMEOUT):
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

    def __wait_for_install_complete(self, sleep_time: int = SHORT_TIMEOUT):
        """
        This method wait till ocp install complete
        :param sleep_time:
        :return:
        """
        current_wait_time = 0
        while self.__provision_timeout <= 0 or current_wait_time <= self.__provision_timeout:
            install_log = self.__remote_ssh.run_command(self.__provision_installer_log)
            if 'failed=0' in install_log:
                return True
            elif 'failed=1' in install_log:
                return False
            logger.info(f'Waiting till OCP install complete, waiting {int(current_wait_time/60)} minutes')
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise IBMOCPInstallationFailed()

    @staticmethod
    def __ibm_logout_cmd():
        """
        This method return ibm logout command
        :return:
        """
        return 'ibmcloud logout'

    def __ibm_install_ocp_cmd(self):
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
        return ibm_blk[:self.__num_odf_disks]

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

    def __get_installation_version(self):
        """
        This method return installation version
        :return:
        """
        ocp_versions = OCPVersions()
        if self.LATEST in self.__install_ocp_version:
            openshift_version_data = self.__install_ocp_version.split('-')
            return ocp_versions.get_latest_version(latest_version=openshift_version_data[1])
        else:
            return self.__install_ocp_version

    def get_ocp_server_version(self):
        """
        This method return ocp server version
        :return:
        """
        return self.__remote_ssh.run_command(command=f"{self.__cli} version -ojson | jq -r '.openshiftVersion'").strip()

    def version_already_installed(self):
        """
        This method validate if version is already install
        :return: True if it already installed, False if it NOT already installed
        """
        if self.get_ocp_server_version() == 'null':
            return False
        elif self.LATEST in self.__install_ocp_version and self.get_ocp_server_version() == self.__get_installation_version():
            return self.get_ocp_server_version().strip()
        elif self.__install_ocp_version == self.get_ocp_server_version():
            return self.__install_ocp_version
        else:
            return False

    @logger_time_stamp
    def restart_pod_ci(self):
        """
        This method restart pod ci: elastic, kibana, grafana, nginx and flask - solved connectivity issue after installation
        :return:
        """
        self.__remote_ssh.run_command('podman pod restart pod_ci')

    @logger_time_stamp
    def update_ocp_version(self):
        """
        This method update the ocp version on provision machine
        :return:
        """
        # Get the latest assisted installer version
        if self.LATEST in self.__install_ocp_version:
            self.__install_ocp_version = self.__get_installation_version()
        openshift_version_data = self.__install_ocp_version.split('.')
        self.__remote_ssh.replace_parameter(remote_path='/root/jetlag/ansible/vars',
                                            file_name='ibmcloud.yml',
                                            parameter='ocp_release_image:',
                                            value=f'quay.io\/openshift-release-dev\/ocp-release:{self.__install_ocp_version}-x86_64')
        self.__remote_ssh.replace_parameter(remote_path='/root/jetlag/ansible/vars',
                                            file_name='ibmcloud.yml',
                                            parameter='openshift_version:',
                                            value=f'"{openshift_version_data[0]}.{openshift_version_data[1]}"')

    @logger_time_stamp
    def run_ibm_ocp_installer(self):
        """
        This method run ocp assisted installer
        :return: True if installation success and raise exception if installation failed
        """
        logger.info(f'Starting OCP assisted installer, Start time: {datetime.now().strftime(datetime_format)}')
        # update ssh config - must add it and also mount it
        self.__ssh.run(f"echo Host provision >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"echo -e '\t'HostName {self.__provision_ip} >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"echo -e '\t'User {self.__user} >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"echo -e '\t'IdentityFile {self.__container_private_key_path} >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"echo -e '\t'StrictHostKeyChecking no >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"echo -e '\t'ServerAliveInterval 30 >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"echo -e '\t'ServerAliveCountMax 5 >> /{self.__user}/.ssh/config")
        self.__ssh.run(f"chmod 600 /{self.__user}/.ssh/config")
        # Must add -t otherwise remote ssh of ansible will not end
        self.__ssh.run(cmd=f"ssh -t provision \"{self.__ibm_login_cmd()};{self.__ibm_install_ocp_cmd()}\" ")
        logger.info(f'OpenShift cluster {self.__get_installation_version()} version is installed successfully, End time: {datetime.now().strftime(datetime_format)}')

    @logger_time_stamp
    def verify_install_complete(self):
        """
        This method verify that installation complete
        :return: True if installation success and raise exception if installation failed
        """
        complete = self.__wait_for_install_complete()
        if not complete:
            raise Exception(f'Installation failed')
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
                # if there are worker nodes, they must be 3
                if len(worker_nodes.split()) > 1:
                    if len(worker_nodes.split()) == 3:
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
        This method install OCP resources 'cnv', 'local_storage', 'odf'
        :param ibm_blk_disk_name: ibm blk disk name
        :param resources:
        :return:
        """
        create_ocp_resource = CreateOCPResource()
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

    def get_ocp_install_time(self):
        """
        This method return install time
        :param self:
        :return:
        """
        install_log = self.__remote_ssh.run_command(self.__provision_installer_log)
        return install_log.split()[-1].strip('"')
