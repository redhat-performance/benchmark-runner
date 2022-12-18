
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateCustom(CreateOCPResourceOperations):
    """
    This class is created Custom resource
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    @logger_time_stamp
    def create_custom(self):
        """
        This method create custom resource
        :return:
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {self.__path}/./{resource}')
            else:
                self.__oc.create_async(yaml=os.path.join(self.__path, resource))
