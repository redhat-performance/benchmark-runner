
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateLSO(CreateOCPResourceOperations):
    """
    This class is created Local Storage operator
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    @logger_time_stamp
    def create_lso(self, upgrade_version: str):
        """
        This method creates lso operator
        :return:
        """
        if upgrade_version:
            self.__oc.apply_async(yaml=os.path.join(self.__path, '03_subscription.yaml'))
            logger.info(f'Wait till LSO upgrade to version: {upgrade_version}')
            self.verify_csv_installation(namespace='openshift-local-storage', operator='lso', upgrade_version=upgrade_version)
        else:
            for resource in self.__resource_list:
                logger.info(f'run {resource}')
                self.__oc.create_async(yaml=os.path.join(self.__path, resource))

            # verify once after create all resource files
            self.wait_for_ocp_resource_create(operator='lso',
                                              verify_cmd="oc -n openshift-local-storage wait deployment/local-storage-operator --for=condition=Available",
                                              status='deployment.apps/local-storage-operator condition met')
            return True
