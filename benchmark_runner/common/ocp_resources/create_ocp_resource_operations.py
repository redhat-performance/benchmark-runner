
import time
from typeguard import typechecked

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import OCPResourceCreationTimeout, ODFInstallationFailed


class CreateOCPResourceOperations:
    """
    This class creates OCP resources
    """
    def __init__(self, oc: OC):
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self.__oc = oc

    @staticmethod
    @typechecked
    def _replace_in_file(file_path: str, old_value: str, new_value: str):
        """
        This method replaces string in file
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

    @typechecked
    @logger_time_stamp
    def wait_for_ocp_resource_create(self, resource: str, verify_cmd: str, status: str = '', count_disk_maker: bool = False, count_openshift_storage: bool = False, kata_worker_machine_count: bool = False, verify_installation: bool = False, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits till operator is created or throw exception after timeout
        :param resource: The resource cnv, local storage, odf, kata
        :param verify_cmd: Verify command that resource was created successfully
        :param status: The final success status
        :param count_disk_maker: count disk maker
        :param count_openshift_storage: count openshift storage disks
        :param kata_worker_machine_count: count kata worker machine
        :param verify_installation: Verify that the installation was successful
        :param timeout: Timeout duration for OpenShift resource creation.
        :return: True if met the result
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            # Count openshift-storage/ pv
            if count_openshift_storage:
                if int(self.__oc.run(verify_cmd)) == self.__oc.get_num_active_nodes() * int(environment_variables.environment_variables_dict['num_odf_disk']):
                    return True
                else:
                    # Verify ODF installation that all Ceph disks are operational. If not, raise an exception.
                    if verify_installation:
                        raise ODFInstallationFailed(disk_num=self.__oc.run(verify_cmd))
                # Count disk maker (worker/master number * disk maker)
            elif count_disk_maker:
                if int(self.__oc.run(verify_cmd)) == int(self.__oc.get_num_active_nodes()) * 2:
                    return True
                # Count worker machines
            elif kata_worker_machine_count:
                if int(self.__oc.run(verify_cmd)) > 0:
                    return True
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
        raise OCPResourceCreationTimeout(resource)

    def apply_non_approved_patch(self, approved_values_list: list, namespace: str, resource: str):
        """
        This method returns the index of not approved InstallPlan
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
        This method applies not approved InstallPlan
        :param namespace:
        :param resource:
        :return:
        """
        install_plan_cmd = 'oc get InstallPlan -n namespace -ojsonpath={..spec.approved}'.replace('namespace', namespace).strip()
        approved_values_list = self.__oc.run(cmd=install_plan_cmd).split()
        while 'false' in approved_values_list:
            self.apply_non_approved_patch(approved_values_list, namespace, resource)
            approved_values_list = self.__oc.run(cmd=install_plan_cmd).split()
