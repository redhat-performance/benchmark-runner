
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class MigrateInfra(CreateOCPResourceOperations):
    """
    Migrate infrastructure to master nodes
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    @logger_time_stamp
    def migrate_infra(self):
        """
        Actually migrate infrastructure
        :return: False if anything fails or if no master nodes are found.
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            if resource == '01_cluster-monitoring-configmap-template.yaml':
                nodes = self.__oc.get_master_nodes().split()
                if nodes:
                    for node in nodes:
                        self.__oc.run(f'oc label node {node} node-role.kubernetes.io/infra=')
                    return self.__oc._create_async(yaml=os.path.join(self.__path, resource))
                else:
                    return False
        return False
