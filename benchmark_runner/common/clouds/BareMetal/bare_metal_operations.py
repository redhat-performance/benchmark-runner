import os
import time
from datetime import datetime
from typeguard import typechecked
import ast  # change string list to list

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger, datetime_format
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.remote_ssh.remote_ssh import ConnectionData, RemoteSsh
from benchmark_runner.common.ocp_resources.create_ocp_resource import CreateOCPResource
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.github.github_operations import GitHubOperations
from benchmark_runner.common.clouds.BareMetal.bare_metal_exceptions import MissingMasterNodes, MissingWorkerNodes, OCPInstallationFailed, OCPUpgradeFailed
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.common.assisted_installer.assisted_installer_latest_version import AssistedInstallerVersions


class BareMetalOperations:
    """
    This class is responsible for Bare metal OpenShift installation operations, all commands run on remote provision server
    """
    LATEST = 'latest'
    SHORT_TIMEOUT = 600

    @typechecked
    def __init__(self, user: str):
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self._user = user
        self._ocp_env_flavor = self._environment_variables_dict.get('ocp_env_flavor', '')
        self._create_pod_ci_cmd = self._environment_variables_dict.get('create_pod_ci_cmd', '')
        self._provision_kubeadmin_password_path = self._environment_variables_dict.get('provision_kubeadmin_password_path', '')
        self._provision_kubeconfig_path = self._environment_variables_dict.get('provision_kubeconfig_path', '')
        self._provision_installer_path = self._environment_variables_dict.get('provision_installer_path', '')
        self._provision_installer_cmd = self._environment_variables_dict.get('provision_installer_cmd', '')
        self._provision_installer_log = self._environment_variables_dict.get('provision_installer_log', '')
        self._install_ocp_version = self._environment_variables_dict.get('install_ocp_version', '')
        self._cluster_type = self._environment_variables_dict.get('cluster_type', '')
        self._expected_nodes = self._environment_variables_dict.get('expected_nodes', '')
        if self._expected_nodes:
            # string to dict
            self._expected_nodes = ast.literal_eval(self._expected_nodes)
        self._ocp_version_build = self._environment_variables_dict.get('ocp_version_build', '')
        self._num_odf_disks = int(self._environment_variables_dict.get('num_odf_disk', 1))
        self._provision_ip = self._environment_variables_dict.get('provision_ip', '')
        self._provision_port = int(self._environment_variables_dict.get('provision_port', ''))
        self._provision_timeout = int(self._environment_variables_dict.get('provision_timeout', ''))
        self._container_private_key_path = self._environment_variables_dict.get('container_private_key_path', '')
        self._connection_data = ConnectionData(host_name=self._provision_ip,
                                                user_name=self._user,
                                                port=self._provision_port,
                                                timeout=self._provision_timeout,
                                                ssh_key=self._container_private_key_path)
        self._remote_ssh = RemoteSsh(self._connection_data)
        if self._environment_variables_dict.get('github_repository_short', ''):
            self._github_operations = GitHubOperations()
        self._ssh = SSH()
        self._cli = self._environment_variables_dict.get('cli', '')
        self._upgrade_ocp_version = self._environment_variables_dict.get('upgrade_ocp_version', '')

    def _get_kubeadmin_password(self):
        """
        This method returns kubeadmin password if exist
        :return:
        """
        if self._remote_ssh.exist(remote_path=self._provision_kubeadmin_password_path):
            return self._remote_ssh.run_command(f'cat {self._provision_kubeadmin_password_path}')

    def _get_kubeconfig(self):
        """
        This method returns kubeconfig if exist
        :return:
        """
        if self._remote_ssh.exist(remote_path=self._provision_kubeconfig_path):
            return self._remote_ssh.run_command(f'cat {self._provision_kubeconfig_path}')

    def _wait_for_install_complete(self, sleep_time: int = SHORT_TIMEOUT):
        """
        This method waits till ocp install complete
        :param sleep_time:
        :return:
        """
        current_wait_time = 0
        install_log = ''
        while self._provision_timeout <= 0 or current_wait_time <= self._provision_timeout:
            install_log = self._remote_ssh.run_command(self._provision_installer_log)
            if 'failed=0' in install_log:
                return True
            elif 'failed=1' in install_log:
                return False
            logger.info(f'Waiting till OCP install complete, waiting {int(current_wait_time/60)} minutes')
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise OCPInstallationFailed(install_log)

    def _wait_for_upgrade_complete(self, oc: OC, sleep_time: int = SHORT_TIMEOUT):
        """
        This method waits till ocp upgrade complete
        :param sleep_time:
        :return:
        """
        current_wait_time = 0
        logger.info(f'Waiting until the upgrade to version {self._upgrade_ocp_version} starts...')
        oc.wait_for_ocp_upgrade_start(upgrade_version=self._upgrade_ocp_version)
        while self._provision_timeout <= 0 or current_wait_time <= self._provision_timeout and oc.upgrade_in_progress():
            logger.info(f'Waiting till OCP upgrade complete, waiting {int(current_wait_time / 60)} minutes')
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        if f'Cluster version is {self._upgrade_ocp_version}' == oc.get_cluster_status():
            return True
        else:
            raise OCPUpgradeFailed(status=oc.get_cluster_status())

    def _install_ocp_cmd(self):
        """
        This method returns local ocp installer cmd if exist
        :return:
        """
        if self._remote_ssh.exist(remote_path=self._provision_installer_path):
            return self._provision_installer_cmd

    @logger_time_stamp
    def connect_to_provisioner(self):
        """
        This method connect to remote provision machine
        :return:
        """
        self._remote_ssh.connect()

    @logger_time_stamp
    def disconnect_from_provisioner(self):
        """
        This method
        :return:
        """
        self._remote_ssh.disconnect()

    def _get_installation_version(self):
        """
        This method return installation version
        :return:
        """
        assisted_installer_versions = AssistedInstallerVersions()
        if self.LATEST in self._install_ocp_version:
            openshift_version_data = self._install_ocp_version.split('-')
            # release candidate or engineering candidate or feature candidate version
            if '-rc' in self._install_ocp_version or '-ec' in self._install_ocp_version or '-fc' in self._install_ocp_version:
                return assisted_installer_versions.get_latest_version(latest_version=f'{openshift_version_data[1]}-{openshift_version_data[2]}')
            # release version
            else:
                return assisted_installer_versions.get_latest_version(latest_version=openshift_version_data[1])
        else:
            return self._install_ocp_version

    def get_ocp_server_version(self):
        """
        This method return ocp server version
        :return:
        """
        return self._remote_ssh.run_command(command=f"{self._cli} version -ojson | jq -r '.openshiftVersion'").strip()

    def version_already_installed(self):
        """
        This method validate if version is already install
        :return: True if it already installed, False if it NOT already installed
        """
        if self.get_ocp_server_version() == 'null':
            return False
        elif self.LATEST in self._install_ocp_version and self.get_ocp_server_version() == self._get_installation_version():
            return self.get_ocp_server_version().strip()
        elif self._install_ocp_version == self.get_ocp_server_version():
            return self._install_ocp_version
        else:
            return False

    @logger_time_stamp
    def restart_pod_ci(self):
        """
        This method restart pod ci: elastic, kibana, grafana, nginx and flask - solved connectivity issue after installation
        :return:
        """
        self._remote_ssh.run_command('podman pod restart pod_ci')

    @typechecked()
    @logger_time_stamp
    def update_ocp_version(self, file_name: str):
        """
        This method update the ocp version on provision machine
        :param file_name:
        :return:
        """
        # Get the latest assisted installer version
        if self.LATEST in self._install_ocp_version:
            self._install_ocp_version = self._get_installation_version()
        openshift_version_data = self._install_ocp_version.split('.')
        self._remote_ssh.replace_parameter(remote_path='/root/jetlag/ansible/vars',
                                            file_name=file_name,
                                            parameter='ocp_release_image:',
                                            value=fr'quay.io\/openshift-release-dev\/ocp-release:{self._install_ocp_version}-x86_64')
        self._remote_ssh.replace_parameter(remote_path='/root/jetlag/ansible/vars',
                                            file_name=file_name,
                                            parameter='openshift_version:',
                                            value=f'"{openshift_version_data[0]}.{openshift_version_data[1]}"')

    def update_provision_config(self):
        """
        This method update provision config file
        :return:
        """
        # update ssh config - must add it and also mount it
        self._ssh.run(f"echo Host provision > /{self._user}/.ssh/config")
        self._ssh.run(f"echo -e '\t'HostName {self._provision_ip} >> /{self._user}/.ssh/config")
        self._ssh.run(f"echo -e '\t'User {self._user} >> /{self._user}/.ssh/config")
        self._ssh.run(f"echo -e '\t'IdentityFile {self._container_private_key_path} >> /{self._user}/.ssh/config")
        self._ssh.run(f"echo -e '\t'StrictHostKeyChecking no >> /{self._user}/.ssh/config")
        self._ssh.run(f"echo -e '\t'ServerAliveInterval 30 >> /{self._user}/.ssh/config")
        self._ssh.run(f"echo -e '\t'ServerAliveCountMax 5 >> /{self._user}/.ssh/config")
        self._ssh.run(f"chmod 600 /{self._user}/.ssh/config")

    @logger_time_stamp
    def run_ocp_installer(self):
        """
        This method runs ocp assisted installer
        :return: True if installation success and raise exception if installation failed
        """
        self.update_provision_config()
        logger.info(f'Starting OCP assisted installer, Start time: {datetime.now().strftime(datetime_format)}')
        # Must add -t otherwise remote ssh of ansible will not end
        self._ssh.run(f"ssh -t provision \"{self._install_ocp_cmd()}\" ")
        logger.info(f'OpenShift cluster {self._get_installation_version()} version is installed successfully, End time: {datetime.now().strftime(datetime_format)}')

    def is_ocp_already_upgraded(self, oc: OC):
        """
        This method checks if Openshift cluster is already upgraded
        @return:
        """
        if f'Cluster version is {self._upgrade_ocp_version}' == oc.get_cluster_status():
            logger.info(f'Cluster is already upgraded to: {self._upgrade_ocp_version}')
            return True
        else:
            return False

    @logger_time_stamp
    def run_ocp_upgrade(self, oc: OC):
        """
        This method runs OpenShift upgrade
        @param oc:
        :return:
        """
        logger.info(f'Starting OCP upgrade, Start time: {datetime.now().strftime(datetime_format)}')
        logger.info(f'Stop OCP healthcheck')
        oc.healthcheck(action='stop')
        oc.upgrade_ocp(upgrade_ocp_version=self._upgrade_ocp_version)
        self.verify_upgrade_complete(oc=oc)
        logger.info(f'Resume OCP healthcheck')
        oc.healthcheck(action='resume')
        logger.info(f'Ending OCP upgrade, End time: {datetime.now().strftime(datetime_format)}')

    @logger_time_stamp
    def verify_install_complete(self):
        """
        This method verifies that the installation has completed
        :return: Returns True if the installation is successful; raises an exception if the installation fails
        """
        complete = self._wait_for_install_complete()
        if not complete:
            install_log = self._remote_ssh.run_command(self._provision_installer_log)
            raise OCPInstallationFailed(install_log)
        else:
            return True

    def is_cluster_upgraded(self, oc: OC, cnv_version: str, odf_version: str, lso_version: str):
        """
        This method checks if cluster/operators upgraded successfully
        @param oc:
        @param cnv_version:
        @param odf_version:
        @param lso_version:
        @return:
        """
        # check cluster version upgrade
        if oc.get_upgrade_version() == self._upgrade_ocp_version:
            lso_upgraded = oc.wait_for_operator_installation(operator='lso', version=lso_version, namespace='openshift-local-storage')
            odf_upgraded = oc.wait_for_operator_installation(operator='odf', version=odf_version, namespace='openshift-storage')
            cnv_upgraded = oc.wait_for_operator_installation(operator='cnv', version=cnv_version, namespace='openshift-cnv')
            # check operators versions upgrade
            if cnv_upgraded and lso_upgraded and odf_upgraded:
                return True
        return False

    @logger_time_stamp
    def verify_upgrade_complete(self, oc: OC):
        """
        This method verifies that the upgrade has completed
        :return: True if the upgrade is successful; raises an exception if the upgrade fails
        """
        complete = self._wait_for_upgrade_complete(oc)
        if complete:
            return True
        raise OCPUpgradeFailed(status=oc.get_cluster_status())

    @logger_time_stamp
    def oc_login(self):
        """
        This method login to the cluster with new credentials
        :return:
        """
        oc = OC(kubeadmin_password=self._get_kubeadmin_password())
        oc.login()
        return oc

    @staticmethod
    def get_missing_node(expected_nodes: list, actual_nodes: list):
        """
        This method returns missing nodes
        :return:
        """
        return set(expected_nodes) - set(actual_nodes)

    @logger_time_stamp
    def verify_cluster_is_up(self, oc: OC):
        """
        This method verify that master/worker nodes are up and running
        :return:
        """
        master_nodes = oc.get_master_nodes()
        if len(master_nodes.split()) == len(self._expected_nodes['master']):
            logger.info('master nodes are up and running')
            if self._ocp_env_flavor == 'PERF' and not self._cluster_type == 'SNO':
                worker_nodes = oc.get_worker_nodes()
                # if there are worker nodes, they must be 3
                if len(worker_nodes.split()) > 1:
                    if len(worker_nodes.split()) == len(self._expected_nodes['worker']):
                        logger.info('worker nodes are up and running')
                    else:
                        missing_node = self.get_missing_node(expected_nodes=self._expected_nodes['worker'], actual_nodes=worker_nodes.split())
                        raise MissingWorkerNodes(missing_node)
        else:
            missing_node = self.get_missing_node(expected_nodes=self._expected_nodes['master'], actual_nodes=master_nodes.split())
            raise MissingMasterNodes(missing_node)

    @staticmethod
    @logger_time_stamp
    @typechecked
    def install_ocp_resources(resources: list, upgrade_version: str = None):
        """
        This method installs OCP resources 'cnv', 'lso', 'odf'
        :param resources:
        :param upgrade_version: upgrade version, default None
        :return:
        """
        create_ocp_resource = CreateOCPResource()
        for resource in resources:
            create_ocp_resource.create_resource(resource=resource, upgrade_version=upgrade_version)

    @logger_time_stamp
    def update_ocp_github_credentials(self):
        """
        This method updates GitHub secrets kubeconfig and kubeadmin_password
        :return:
        """
        self._github_operations.create_secret(secret_name=f'{self._ocp_env_flavor}_KUBECONFIG', unencrypted_value=self._get_kubeconfig())
        self._github_operations.create_secret(secret_name=f'{self._ocp_env_flavor}_KUBEADMIN_PASSWORD',
                                              unencrypted_value=self._get_kubeadmin_password())

    def get_ocp_install_time(self):
        """
        This method returns installation time
        :param self:
        :return:
        """
        install_log = self._remote_ssh.run_command(self._provision_installer_log)
        return install_log.split()[-1].strip('"')
