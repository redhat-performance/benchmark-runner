
import os
import time
from typeguard import typechecked

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import OCPResourceNotCreateTimeout, KataInstallationFailed


class CreateOCPResourceOperations:
    """
    This class is create OCP resources
    """
    def __init__(self, oc: OC):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__kubeadmin_password = self.__environment_variables_dict.get('kubeadmin_password', '')
        self.__oc = oc

    @staticmethod
    @typechecked
    def __replace_in_file(file_path: str, old_value: str, new_value: str):
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

    def __install_and_wait_for_resource(self, yaml_file: str, resource_type: str, resource: str):
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

    @typechecked
    @logger_time_stamp
    def create_custom(self, path: str, resource_list: list):
        """
        This method create custom resource
        :param path:path of resource files
        :param resource_list: cnv resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                self.__oc.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource}')
            else:
                self.__oc._create_async(yaml=os.path.join(path, resource))

    @typechecked
    @logger_time_stamp
    def create_cnv(self, path: str, resource_list: list):
        """
        This method create cnv resource
        :param path:path of resource files
        :param resource_list: cnv resource lists
        :return:
        """
        cnv_version = self.__environment_variables_dict.get('cnv_version', '')
        for resource in resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                self.__oc.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource}')
            else:
                self.__oc._create_async(yaml=os.path.join(path, resource))
                if '02_cnv_nightly_catalog_source.yaml' in resource:
                    logger.info('wait for cnv-nightly kubevirt-hyperconverged')
                    self.wait_for_ocp_resource_create(resource=resource,
                                                      verify_cmd="oc get packagemanifest -l catalog=cnv-nightly-catalog-source | grep kubevirt-hyperconverged",
                                                      status="kubevirt-hyperconverged")
                    starting_csv = self.__oc.run(""" oc get packagemanifest -l "catalog=cnv-nightly-catalog-source" -o jsonpath="{$.items[?(@.metadata.name=='kubevirt-hyperconverged')].status.channels[?(@.name==\\"nightly-cnv_version\\")].currentCSV}" """.replace('cnv_version', cnv_version))
                    self.__replace_in_file(file_path=os.path.join(path, '03_operator.yaml'), old_value="@starting_csv@", new_value=starting_csv)
                if '03_operator.yaml' in resource:
                    # wait till get the patch
                    self.wait_for_ocp_resource_create(resource=resource,
                                                      verify_cmd="oc get InstallPlan -n openshift-cnv -ojsonpath={.items[0].metadata.name}",
                                                      status="install-")
                    self.apply_patch(namespace='openshift-cnv', resource='cnv')
                # for second script wait for refresh status
                if '04_hyperconverge.yaml' in resource:
                    # Wait that till succeeded
                    self.wait_for_ocp_resource_create(resource='cnv',
                                                      verify_cmd="oc get csv -n openshift-cnv -ojsonpath='{.items[0].status.phase}'",
                                                      status='Succeeded')
        return True

    @typechecked
    @logger_time_stamp
    def create_local_storage(self, path: str, resource_list: list):
        """
        This method create local storage
        :param path:path of resource files
        :param resource_list: local storage resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            self.__oc._create_async(yaml=os.path.join(path, resource))
        # verify once after create all resource files
        self.wait_for_ocp_resource_create(resource='local_storage',
                                          verify_cmd="oc -n openshift-local-storage wait deployment/local-storage-operator --for=condition=Available",
                                          status='deployment.apps/local-storage-operator condition met')
        return True

    @typechecked
    @logger_time_stamp
    def create_odf(self, path: str, resource_list: list, ibm_blk_disk_name: list):
        """
        This method create odf
        :param ibm_blk_disk_name: ibm odf disk blk name
        :param path:path of resource files
        :param resource_list: odf resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                # build sgdisks path dynamically
                if '01_sgdisks.sh' == resource:
                    sgdisk_list = ''
                    for disk_name in ibm_blk_disk_name:
                        sgdisk_list += f'sgdisk --zap-all /dev/{disk_name};'
                    self.__oc.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource} "{sgdisk_list}"')
                else:
                    self.__oc.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource}')
            else:  # yaml
                self.__oc._create_async(yaml=os.path.join(path, resource))
                if '04_local_volume_set.yaml' in resource:
                    # openshift local storage
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd=r"""oc get pod -n openshift-local-storage -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep diskmaker""")
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd=r"""oc get pod -n openshift-local-storage -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep diskmaker | wc -l""", count_local_storage=True)
                    # openshift persistence volume (pv)
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd=r"""oc get pv -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep local""")
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd=r"""oc get pv -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep local | wc -l""",
                                                      count_openshift_storage=True)
                if '07_subscription.yaml' in resource:
                    # wait till get the patch
                    self.wait_for_ocp_resource_create(resource=resource,
                                                      verify_cmd="oc get InstallPlan -n openshift-storage -ojsonpath={.items[0].metadata.name}",
                                                      status="install-")
                    self.apply_patch(namespace='openshift-storage', resource='odf')
                elif '08_storage_cluster.yaml' in resource:
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd=r"""oc get pod -n openshift-storage | grep osd | grep -v prepare""")
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd="oc get csv -n openshift-storage -ojsonpath='{.items[0].status.phase}'",
                                                      status='Succeeded')
                    self.wait_for_ocp_resource_create(resource='odf',
                                                      verify_cmd='oc get pod -n openshift-storage | grep osd | grep -v prepare | wc -l',
                                                      count_openshift_storage=True)
        return True

    @typechecked
    @logger_time_stamp
    def create_kata(self, path: str, resource_list: list):
        """
        This method create kata resource
        :param path:path of resource files
        :param resource_list: kata resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            if '01_operator.yaml' == resource:
                # Wait for kataconfig CRD to exist
                self.__oc._create_async(yaml=os.path.join(path, resource))
                self.wait_for_ocp_resource_create(resource='kata',
                                                  verify_cmd='if oc get crd kataconfigs.kataconfiguration.openshift.io >/dev/null 2>&1 ; then echo succeeded ; fi',
                                                  status='succeeded')
            elif '02_config.yaml' == resource:
                # This one's tricky.  The problem is that it appears
                # that the kataconfigs CRD can exist, but attempting
                # to apply it doesn't "take" unless some other things
                # are already up.  So we have to keep applying the
                # kataconfig until it's present.
                if not self.__install_and_wait_for_resource(os.path.join(path, resource), 'kataconfig', 'example-kataconfig'):
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
                self.__oc.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource}')
        return True
