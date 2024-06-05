import time

from typeguard import typechecked
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc import OC

logger.setLevel('INFO')


class AzureOperations:
    """
    This class is responsible to all the operations against Azure vms
    """
    SLEEP_TIME = 300

    def __init__(self, azure_clientid: str, azure_secret: str, azure_tenantid: str, azure_subscriptionid: str, azure_resource_group_name: str, kubeadmin_password: str):
        self.__azure_clientid = azure_clientid
        self.__azure_secret = azure_secret
        self.__azure_tenantid = azure_tenantid
        self.__azure_subscriptionid = azure_subscriptionid
        self.__azure_resource_group_name = azure_resource_group_name
        self.__credentials = ServicePrincipalCredentials(client_id=self.__azure_clientid, secret=self.__azure_secret,
                                                         tenant=self.__azure_tenantid)
        self.__compute_client = ComputeManagementClient(self.__credentials, self.__azure_subscriptionid)
        self.__kubeadmin_password = kubeadmin_password

    @typechecked()
    @logger_time_stamp
    def restart_vm(self, vm_name: str = ''):
        """
        This method restarts azure vm
        :return:
        """
        vm_restart = self.__compute_client.virtual_machines.restart(self.__azure_resource_group_name, vm_name)
        logger.info('Waiting till VM restart')
        vm_restart.wait()
        vm_instance = self.__compute_client.virtual_machines.get(self.__azure_resource_group_name, vm_name)
        return vm_instance

    @typechecked()
    @logger_time_stamp
    def start_vm(self, vm_name: str = ''):
        """
        This method starts azure vm
        :return:
        """
        vm_start = self.__compute_client.virtual_machines.start(self.__azure_resource_group_name, vm_name)
        logger.info('Waiting till VM is running')
        vm_start.wait()
        vm_instance = self.__compute_client.virtual_machines.get(self.__azure_resource_group_name, vm_name)
        return vm_instance

    @typechecked()
    @logger_time_stamp
    def stop_vm(self, vm_name: str = ''):
        """
        This method stops azure vm
        :return:
        """
        vm_stop = self.__compute_client.virtual_machines.deallocate(self.__azure_resource_group_name, vm_name)
        logger.info('Waiting till VM Stopped (deallocated)')
        vm_stop.wait()
        vm_instance = self.__compute_client.virtual_machines.get(self.__azure_resource_group_name, vm_name)
        return vm_instance

    @typechecked()
    @logger_time_stamp
    def get_vm_status(self, vm_name: str = ''):
        """
        This method return vm status
        :return:
        """
        vm_instance = self.__compute_client.virtual_machines.get(self.__azure_resource_group_name, vm_name)
        return vm_instance

    @logger_time_stamp
    def oc_login(self):
        """
        This method login to the cluster with new credentials
        :return:
        """
        oc = OC(kubeadmin_password=self.__kubeadmin_password)
        oc.login()
        return oc

    def verify_sno_cluster_is_up(self):
        """
        This method verifies sno cluster is up and running
        @return:
        """
        master_nodes = self.oc_login().get_master_nodes()
        if len(master_nodes.split()) == 1:
            return True
        else:
            return False

    def start_cluster_with_verification(self, vm_name: str, max_retry=3):
        """
        This method starts cluster with verification
        @param vm_name:
        @param max_retry: 3
        @return:
        """
        for attempt in range(1, max_retry + 1):
            logger.info(f"Attempt {attempt} to start the cluster...")
            try:
                logger.info('Start VM')
                self.start_vm(vm_name=vm_name)
                logger.info(f"Wait {self.SLEEP_TIME} seconds till cluster is up and running")
                time.sleep(self.SLEEP_TIME)
                # Check if the cluster is up
                if self.verify_sno_cluster_is_up():
                    logger.info("Cluster is up and running!")
                    return True
                else:
                    logger.info("Cluster is not up yet.")
            except Exception as e:
                logger.error(f"Error occurred during attempt {attempt} to start the cluster: {str(e)}")
                logger.info('Stop Cluster VM')
                self.stop_vm(vm_name=vm_name)

        logger.error(f"Failed to start the cluster after {max_retry} attempts.")
        return False
