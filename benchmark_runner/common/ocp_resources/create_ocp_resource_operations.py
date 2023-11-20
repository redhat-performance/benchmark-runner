
import time
from typeguard import typechecked

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import OCPResourceCreationTimeout


class CreateOCPResourceOperations:
    """
    This class creates OCP resources
    """
    # Expected CSVs List names
    EXPECTED_ODF_CSV = ['mcg-operator', 'ocs-operator', 'odf-csi-addons-operator', 'odf-operator']

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
    def wait_for_ocp_resource_create(self, resource: str, verify_cmd: str, status: str = '', count_disk_maker: bool = False, count_openshift_storage: bool = False, kata_worker_machine_count: bool = False, count_csv_names: bool = False, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits till operator is created or throw exception after timeout
        :param resource: The resource cnv, local storage, odf, kata
        :param verify_cmd: Verify command that resource was created successfully
        :param status: The final success status
        :param count_disk_maker: count disk maker
        :param count_openshift_storage: count openshift storage disks
        :param kata_worker_machine_count: count kata worker machine
        :param timeout: Timeout duration for OpenShift resource creation.
        :return: True if met the result
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            cmd = self.__oc.run(verify_cmd)
            # Count openshift-storage/ pv
            if count_openshift_storage:
                if int(cmd) == self.__oc.get_num_active_nodes() * int(environment_variables.environment_variables_dict['num_odf_disk']):
                    return True
            # Count disk maker (worker/master number * disk maker)
            elif count_disk_maker:
                if int(cmd) == int(self.__oc.get_num_active_nodes()) * 2:
                    return True
            # Count worker machines
            elif kata_worker_machine_count:
                if int(cmd) > 0:
                    return True
            # Count CSV
            elif count_csv_names:
                # Wait to CSV
                if cmd:
                    # ODF operator: not all CSV are started on the same time
                    if resource == 'odf':
                        # Verify each CSV name
                        if all(any(actual_csv.startswith(expected_csv) for actual_csv in cmd.split()) for expected_csv in self.EXPECTED_ODF_CSV):
                            return True
                    # default 1 CSV
                    else:
                        return True
            elif status:
                # catch equal or contains
                if status in cmd:
                    return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise OCPResourceCreationTimeout(resource)

    def verify_csv_installation(self, namespace: str, resource: str):
        """
        This method verifies csv installation
        :param namespace:
        :param resource:
        """
        csv_names = self.__oc.run(f"oc get csv -n {namespace} -ojsonpath={{$.items[*].metadata.name}}")
        for csv_name in csv_names.split():
            self.wait_for_ocp_resource_create(resource=resource,
                                              verify_cmd=f"oc get csv -n {namespace} {csv_name} -ojsonpath='{{.status.phase}}'",
                                              status='Succeeded')

    def apply_patch(self, namespace: str, resource: str):
        """
        This method applies an InstallPlan that has not been approved
        :param namespace:
        :param resource:
        :return:
        """
        install_plan_cmd = f"oc get InstallPlan -n {namespace} -ojsonpath={{$.items[*].metadata.name}}"
        install_plan_names = self.__oc.run(cmd=install_plan_cmd).split()
        for name in install_plan_names:
            check_approved = f"oc get InstallPlan -n {namespace} {name} -ojsonpath={{..spec.approved}}"
            approved = self.__oc.run(cmd=check_approved)
            # APPROVED false - need to patch
            if not {'true': True, 'false': False}.get(approved.lower(), False):
                install_plan_cmd = (f"oc patch InstallPlan -n {namespace} {name} -p '{{\"spec\":{{\"approved\":true}}}}' --type merge")
                self.__oc.run(cmd=install_plan_cmd)
                # Wait till installPlan is approved
                self.wait_for_ocp_resource_create(resource=resource,
                                                  verify_cmd=check_approved,
                                                  status="true")
                # Wait till CSV name is created
                self.wait_for_ocp_resource_create(resource=resource,
                                                  verify_cmd=f"oc get csv -n {namespace} -ojsonpath={{$.items[*].metadata.name}}",
                                                  count_csv_names=True)
                # Verify CSV installation
                self.verify_csv_installation(namespace=namespace, resource=resource)
