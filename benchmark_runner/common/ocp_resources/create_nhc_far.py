
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateNHCFAR(CreateOCPResourceOperations):
    """
    This class is created node-health-check and fence-agents-remediation operators
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    @logger_time_stamp
    def create_nhc_far(self):
        """
        This method creates node-health-check and fence-agents-remediation operators
        :return:
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            self.__oc.create_async(yaml=os.path.join(self.__path, resource))

            if '03_nhc_subscription.yaml' in resource:
                self.wait_for_ocp_resource_create(operator='nhc',
                                                  verify_cmd="oc get csv -n openshift-workload-availability -o jsonpath='{.items[0].status.phase}'",
                                                  status='Succeeded')
            if '04_far_subscription.yaml' in resource:
                self.wait_for_ocp_resource_create(operator='far',
                                                  verify_cmd="oc get csv -n openshift-workload-availability -o jsonpath='{.items[1].status.phase}'",
                                                  status='Succeeded')
            if '05_nhc_far.yaml' in resource:
                # Verify NHC is enabled
                self.wait_for_ocp_resource_create(operator='nhc_far',
                                                  verify_cmd="oc get nhc -A -o jsonpath='{range .items[*]}{.status.phase}{\"\\n\"}{end}'",
                                                  status='Enabled')
        return True
