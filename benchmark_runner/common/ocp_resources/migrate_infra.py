
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateODF(CreateOCPResourceOperations):
    """
    This class is create OCP resources
    """
    def __init__(self, oc: OC, path: str, resource_list: list, ibm_blk_disk_name: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list
        self.__ibm_blk_disk_name = ibm_blk_disk_name

    @logger_time_stamp
    def create_odf(self):
        """
        This method create odf
        :return:
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            if resource == '01_cluster-monitoring-configmap-template.yaml':
                nodes = self.__oc.get_master_nodes().split()
                if len(nodes) < 1:
                    pass
                for node in nodes:
                    self.run(f'oc label {node} node-role.kubernetes.io/infra=')
                self.__oc._create_async(yaml=os.path.join(self.__path, resource))
        return True