
import os
import time
from typeguard import typechecked

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import KataInstallationFailed
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations
from benchmark_runner.main.environment_variables import environment_variables


class CreateKata(CreateOCPResourceOperations):
    """
    This class is create OCP resources
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    def __install_and_wait_for_resource_with_retry(self, yaml_file: str, resource_type: str, resource: str):
        """
        Create a resource where the creation process itself may fail
        without indicating an error and then have to be retried.
        :param yaml_file:YAML file to create the resource
        :param resource_type:type of resource to create
        :param resource: name of resource to create
        :return:
        """
        timeout = int(environment_variables.environment_variables_dict['timeout'])
        current_wait_time = 0
        while timeout <= 0 or current_wait_time < timeout:
            self.__oc._create_async(yaml_file)
            # We cannot wait for a condition here, because the
            # create_async may simply not work even if it returns success.
            time.sleep(OC.SLEEP_TIME)
            if self.__oc.run(f'if oc get {resource_type} {resource} > /dev/null 2>&1 ; then echo succeeded; fi') == 'succeeded':
                return True
            current_wait_time += OC.SLEEP_TIME
        return False

    @logger_time_stamp
    def create_kata(self):
        """
        This method create kata resource
        :return:
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            if '01_operator.yaml' == resource:
                # Wait for kataconfig CRD to exist
                self.__oc._create_async(os.path.join(self.__path, resource))
                self.wait_for_ocp_resource_create(resource='kata',
                                                  verify_cmd='if oc get crd kataconfigs.kataconfiguration.openshift.io >/dev/null 2>&1 ; then echo succeeded ; fi',
                                                  status='succeeded')
            elif '02_config.yaml' == resource:
                # This one's tricky.  The problem is that it appears
                # that the kataconfigs CRD can exist, but attempting
                # to apply it doesn't "take" unless some other things
                # are already up.  So we have to keep applying the
                # kataconfig until it's present.
                if not self.__install_and_wait_for_resource_with_retry(os.path.join(self.__path, resource), 'kataconfig', 'example-kataconfig'):
                    raise KataInstallationFailed('Failed to apply kataconfig resource')
                # Next, we have to wait for the kata bits to actually install
                self.wait_for_ocp_resource_create(resource='kata',
                                                  verify_cmd="oc get kataconfig -ojsonpath='{.items[0].status.installationStatus.IsInProgress}'",
                                                  status='false')
                total_nodes_count = self.__oc.run(cmd="oc get kataconfig -ojsonpath='{.items[0].status.total_nodes_count}'")
                completed_nodes_count = self.__oc.run(cmd="oc get kataconfig -ojsonpath='{.items[0].status.installationStatus.completed.completed_nodes_count}'")
                if total_nodes_count != completed_nodes_count:
                    raise KataInstallationFailed(f'not all nodes installed successfully total {total_nodes_count} != completed {completed_nodes_count}')
            elif '03_ocp48_patch.sh' == resource:
                self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {os.path.join(self.__path, resource)}')
        return True
