
import time
from typeguard import typechecked

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import OCPResourceNotCreateTimeout


class CreateOCPResourceOperations:
    """
    This class is create OCP resources
    """
    def __init__(self, oc: OC):
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self.__oc = oc

    @staticmethod
    @typechecked
    def _replace_in_file(file_path: str, old_value: str, new_value: str):
        """
        This method replace string in file
        :param file_path:
        :param old_value:
        :param new_value:
        :return:
        """
        # Read in the file
        with open(file_path, 'r') as file:
            file_data = file.read()

        # Replace the target string
        file_data = file_data.replace(old_value, new_value)

        # Write the file out again
        with open(file_path, 'w') as file:
            file.write(file_data)

    def _install_and_wait_for_resource(self, yaml_file: str, resource_type: str, resource: str):
            """
            Create a resource where the creation process itself may fail and has to be retried
            :param yaml_file:YAML file to create the resource
            :param resource_type:type of resource to create
            :param resource: name of resource to create
            :return:
            """
            current_wait_time = 0
            while current_wait_time < int(environment_variables.environment_variables_dict['timeout']):
                self.__oc._create_async(yaml_file)
                # We cannot wait for a condition here, because the
                # create_async may simply not work even if it returns success.
                time.sleep(OC.SLEEP_TIME)
                if self.__oc.run(f'if oc get {resource_type} {resource} > /dev/null 2>&1 ; then echo succeeded; fi') == 'succeeded':
                    return True
                current_wait_time += OC.SLEEP_TIME
            return False

    @typechecked
    @logger_time_stamp
    def wait_for_ocp_resource_create(self, resource: str, verify_cmd: str, status: str = '', count_local_storage: bool = False, count_openshift_storage: bool = False, kata_worker_machine_count: bool = False, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method is wait till operator is created or throw exception after timeout
        :param resource: The resource cnv, local storage, odf, kata
        :param verify_cmd: Verify command that resource was created successfully
        :param status: The final success status
        :param count_local_storage: count local storage disks
        :param count_openshift_storage: count openshift storage disks
        :param kata_worker_machine_count: count kata worker machine
        :return: True if met the result
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            # Count openshift-storage/ pv
            if count_openshift_storage:
                if int(self.__oc.run(verify_cmd)) == self.__oc.get_num_active_nodes() * int(environment_variables.environment_variables_dict['num_odf_disk']):
                    return True
                # Count local storage disks (worker/master * (discovery+manager)
            elif count_local_storage:
                if int(self.__oc.run(verify_cmd)) == self.__oc.get_num_active_nodes() * 2:
                    return True
                # Count worker machines
            elif kata_worker_machine_count:
                if int(self.__oc.run(verify_cmd)) > 0:
                    return True
                else:
                    return False
            # verify query return positive result
            if status:
                # catch equal or contains
                if status in self.__oc.run(verify_cmd):
                    return True
            else:
                if self.__oc.run(verify_cmd) != '':
                    return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise OCPResourceNotCreateTimeout(resource)

    def apply_non_approved_patch(self, approved_values_list: list, namespace: str, resource: str):
        """
        This method return the index of not approved InstallPlan
        :param approved_values_list:
        :param namespace:
        :param resource:
        :return:
        """
        for index, approved in enumerate(approved_values_list):
            # APPROVED false - need to patch
            if approved == 'false':
                install_plan = """ oc get InstallPlan -n namespace -ojsonpath={.items[index].metadata.name} """.replace('index', str(index))
                install_plan = install_plan.replace('namespace', namespace)
                install_plan = self.__oc.run(cmd=install_plan)
                install_plan_cmd = """ oc patch InstallPlan -n namespace install_plan -p '{"spec":{"approved":true}}' --type merge""".replace('install_plan', str(install_plan))
                run_install_plan_cmd = install_plan_cmd.replace('namespace', namespace)
                self.__oc.run(cmd=run_install_plan_cmd)
                # verify current status
                check_status = 'oc get InstallPlan -n namespace -ojsonpath={..spec.approved}'.replace('namespace', namespace).strip()
                result = self.__oc.run(cmd=check_status).split()[index]
                if result == 'true':
                    if resource == 'odf':
                        for ind in range(3):
                            self.wait_for_ocp_resource_create(resource=resource,
                                                              verify_cmd="oc get csv -n namespace -ojsonpath='{.items[ind].status.phase}'".replace('namespace', namespace).replace('ind', str(ind)),
                                                              status='Succeeded')
                    if resource == 'cnv':
                        self.wait_for_ocp_resource_create(resource=resource,
                                                          verify_cmd="oc get csv -n namespace -ojsonpath='{.items[0].status.phase}'".replace('namespace', namespace),
                                                          status='Succeeded')

    def apply_patch(self, namespace: str, resource: str):
        """
        This method return the index of not approved InstallPlan
        :param namespace:
        :param resource:
        :return:
        """
        install_plan_cmd = 'oc get InstallPlan -n namespace -ojsonpath={..spec.approved}'.replace('namespace', namespace).strip()
        approved_values_list = self.__oc.run(cmd=install_plan_cmd).split()
        while 'false' in approved_values_list:
            self.apply_non_approved_patch(approved_values_list, namespace, resource)
            approved_values_list = self.__oc.run(cmd=install_plan_cmd).split()
