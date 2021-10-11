
import datetime
from typeguard import typechecked
from tenacity import retry, stop_after_attempt

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger, datetime_format
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.remote_ssh.remote_ssh import ConnectionData, RemoteSsh
from benchmark_runner.common.ocp.create_ocp_resource import CreateOcpResource
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.github.github_operations import GitHubOperations


class IBMOperations:
    """
    This class is responsible for all IBM cloud operations, all commands run on remote provision IBM host
    """

    @typechecked
    def __init__(self, user: str):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__ibm_api_key = self.__environment_variables_dict.get('ibm_api_key', '')
        self.__ibm_oc_user = self.__environment_variables_dict.get('provision_oc_user', '')
        # FUNC or PERF
        self.__ocp_env_flavor = self.__environment_variables_dict.get('ocp_env_flavor', '')
        self.__install_ocp_version = self.__environment_variables_dict.get('install_ocp_version', '')
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
        This method return kubeadmin password
        :return:
        """
        return self.__remote_ssh.run_command(f'cat /home/{self.__ibm_oc_user}/clusterconfigs/auth/kubeadmin-password')

    def __get_kubeconfig(self):
        """
        This method return kubeadmin password
        :return:
        """
        return self.__remote_ssh.run_command(f'cat /home/{self.__ibm_oc_user}/clusterconfigs/auth/kubeconfig')

    def __ibm_login_cmd(self):
        """
        This method return ibm login command
        :return:
        """
        return f'ibmcloud login --apikey {self.__ibm_api_key}'

    @staticmethod
    def __ibm_logout_cmd():
        """
        This method return ibm logout command
        :return:
        """
        return 'ibmcloud logout'

    @staticmethod
    def __ibm_ipi_install_ocp_cmd():
        """
        This method return ibm ipi installer cmd
        :return:
        """
        return 'pushd /ipi-installer/baremetal-deploy; chmod +x utils/ibmsetup.sh; ./utils/ibmsetup.sh; popd'

    @logger_time_stamp
    def get_ibm_disks_blk_name(self):
        """
        This method connect to remote provision maachine
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
                                            value=self.__install_ocp_version)

    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def run_ibm_ocp_ipi_installer(self):
        """
        This method run ocp ipi installer with retry mechanism
        :return: True if installation success and raise exception if installation failed
        """
        logger.info(f'Starting OCP IPI installer, Start time: {datetime.datetime.now().strftime(datetime_format)}')
        result = self.__remote_ssh.run_command(
            f'{self.__ibm_login_cmd()};{self.__ibm_ipi_install_ocp_cmd()};{self.__ibm_logout_cmd()}')
        if 'failed=1' in result:
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
        self.__github_operations._create_secret(secret_name=f'{self.__ocp_env_flavor}_KUBECONFIG', unencrypted_value=self.__get_kubeconfig())
        self.__github_operations._create_secret(secret_name=f'{self.__ocp_env_flavor}_KUBEADMIN_PASSWORD',
                                                unencrypted_value=self.__get_kubeadmin_password())
