
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateLocalStorage(CreateOCPResourceOperations):
    """
    This class is created Local Storage operator
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    @logger_time_stamp
    def create_local_storage(self):
        """
        This method create local storage
        :return:
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            # run in ODF<=4.10
            if '03_catalog_source.yaml' in resource:
                if self._odf_major_version <= 4 and self._odf_minor_version <= 10:
                    self.__oc.create_async(yaml=os.path.join(self.__path, resource))
            # run in ODF<=4.10
            elif '04_1_subscription.yaml' in resource:
                if self._odf_major_version <= 4 and self._odf_minor_version <= 10:
                    self.__oc.create_async(yaml=os.path.join(self.__path, resource))
            # run in ODF>=4.11
            elif '04_2_subscription.yaml' in resource:
                if self._odf_major_version >= 4 and self._odf_minor_version >= 11:
                    self.__oc.create_async(yaml=os.path.join(self.__path, resource))
            else:
                self.__oc.create_async(yaml=os.path.join(self.__path, resource))

        # verify once after create all resource files
        self.wait_for_ocp_resource_create(resource='local_storage',
                                          verify_cmd="oc -n openshift-local-storage wait deployment/local-storage-operator --for=condition=Available",
                                          status='deployment.apps/local-storage-operator condition met')
        return True
