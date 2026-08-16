
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateLVMS(CreateOCPResourceOperations):
    """
    This class creates LVMS (Logical Volume Manager Storage) operator on NVMe devices
    """
    def __init__(self, oc: OC, path: str, resource_list: list, lvms_version: str, lvms_devices: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list
        self.__lvms_version = lvms_version
        self.__lvms_devices = lvms_devices

    @logger_time_stamp
    def create_lvms(self, upgrade_version: str = ''):
        """
        This method creates LVMS operator and LVMCluster
        :param upgrade_version: if set, upgrade existing LVMS
        :return: True if successful
        """
        if upgrade_version:
            self.__oc.apply_async(yaml=os.path.join(self.__path, '01_subscription.yaml'))
            logger.info(f'Wait till LVMS upgrade to version: {upgrade_version}')
            self.verify_csv_installation(namespace='openshift-storage', operator='lvms', upgrade_version=upgrade_version)
        else:
            for resource in self.__resource_list:
                logger.info(f'run {resource}')
                self.__oc.create_async(yaml=os.path.join(self.__path, resource))

                if '01_subscription.yaml' in resource:
                    self.verify_csv_installation(namespace='openshift-storage', operator='lvms')

                elif '02_lvmcluster.yaml' in resource:
                    self.wait_for_ocp_resource_create(
                        operator='lvms',
                        verify_cmd="oc get lvmcluster lvms-nvme -n openshift-storage -o jsonpath='{.status.ready}'",
                        status='true'
                    )

            # Verify StorageClass was created
            sc_name = self.__oc.run("oc get sc -o jsonpath='{.items[?(@.provisioner==\"topolvm.io\")].metadata.name}'")
            if sc_name:
                logger.info(f'LVMS StorageClass created: {sc_name}')
            else:
                logger.warning('LVMS StorageClass not found after LVMCluster creation')

            return True
