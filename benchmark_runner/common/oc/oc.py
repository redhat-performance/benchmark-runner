
import os
import time
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc_exceptions import PodNotCreateTimeout, PodNotInitializedTimeout, PodNotReadyTimeout, \
    PodNotCompletedTimeout, PodTerminateTimeout, PodNameNotExist, LoginFailed, VMNotCreateTimeout, VMTerminateTimeout, \
    YAMLNotExist, VMNameNotExist, VMNotInitializedTimeout, VMNotReadyTimeout, VMNotCompletedTimeout, \
    OCPResourceNotCreateTimeout, KataInstallationFailed, ExecFailed, PodFailed
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.main.environment_variables import environment_variables


class OC(SSH):
    """
    This class run OC commands
    """

    # wait time out
    SHORT_WAIT_TIME = 300
    # sleep time between checks is 5 sec
    SLEEP_TIME = 3

    def __init__(self, kubeadmin_password: str = ''):
        super().__init__()
        self.__kubeadmin_password = kubeadmin_password
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__run_artifacts = self.__environment_variables_dict.get('run_artifacts_path', '')

    def get_ocp_server_version(self):
        """
        This method return ocp server version
        :return:
        """
        ocp_version_data = self.run('oc version')
        ocp_version_data = ocp_version_data.split('\n')
        for line in ocp_version_data:
            if 'Server Version:' in line:
                data = line.split(':')
                return data[1].strip()

    def get_cnv_version(self):
        """
        This method return cnv version
        :return:
        """
        return self.run("oc get csv -n openshift-cnv $(oc get csv -n openshift-cnv --no-headers | awk '{ print $1; }') -ojsonpath='{.spec.version}'")

    def get_ocs_version(self):
        """
        This method return ocs version
        :return:
        """
        return self.run("oc get csv -n openshift-storage $(oc get csv -n openshift-storage --no-headers | awk '{ print $1; }') -ojsonpath='{.spec.version}' ")

    def get_kata_version(self):
        """
        This method returns kata version
        :return:
        """
        return self.run("oc get csv -n openshift-sandboxed-containers-operator $(oc get csv -n openshift-sandboxed-containers-operator --no-headers | awk '{ print $1; }') -ojsonpath='{.spec.version}' ")

    def _get_kata_csv(self):
        """
        Retrieve the CSV of the sandboxed containers operator for installation"
        """
        return self.run("oc get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojsonpath='{.status.channels[0].currentCSV}'")

    def _get_kata_catalog_source(self):
        """
        Retrieve the catalog source of the sandboxed containers operator for installation"
        """
        return self.run("oc get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojsonpath='{.status.catalogSource}'")

    def _get_kata_channel(self):
        """
        Retrieve the channel of the sandboxed containers operator for installation"
        """
        return self.run("oc get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojsonpath='{.status.channels[0].name}'")

    def _get_kata_namespace(self):
        """
        Retrieve the namespace of the sandboxed containers operator for installation"
        """
        return self.run(r"oc get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojsonpath='{.status.channels[0].currentCSVDesc.annotations.operatorframework\.io/suggested-namespace}'")

    @typechecked
    def populate_additional_template_variables(self, env: dict):
        """
        Populate any additional variables needed for setup templates
        """
        env['kata_csv'] = self._get_kata_csv()
        env['kata_catalog_source'] = self._get_kata_catalog_source()
        env['kata_channel'] = self._get_kata_channel()
        env['kata_namespace'] = self._get_kata_namespace()

    def is_cnv_installed(self):
        """
        This method check if cnv operator is installed
        :return:
        """
        verify_cmd = "oc get csv -n openshift-cnv -ojsonpath='{.items[0].status.phase}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def is_ocs_installed(self):
        """
        This method check if ocs operator is installed
        :return:
        """
        verify_cmd = "oc get csv -n openshift-storage -ojsonpath='{.items[0].status.phase}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def is_kata_installed(self):
        """
        This method check if kata operator is installed
        :return:
        """
        verify_cmd = "oc get csv -n openshift-sandboxed-containers-operator -ojsonpath='{.items[0].status.phase}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def get_master_nodes(self):
        """
        This method return master nodes
        :return:
        """
        return self.run(r""" oc get nodes -l node-role.kubernetes.io/master= -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" """)

    def get_worker_nodes(self):
        """
        This method return worker nodes
        :return:
        """
        return self.run(r""" oc get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" """)

    def __get_short_uuid(self, workload: str):
        """
        This method return uuid
        :return:
        """
        long_uuid = self.get_long_uuid(workload=workload)
        uuids = long_uuid.split('-')
        short_uuid = uuids[0]
        return short_uuid

    @typechecked
    def _create_async(self, yaml: str):
        """
        This method create yaml in async
        :param yaml:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'oc create -f {yaml}')
        else:
            raise YAMLNotExist(yaml)

    @typechecked
    def _delete_async(self, yaml: str):
        """
        This method delete yaml in async
        :param yaml:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'oc delete -f {yaml}')
        else:
            raise YAMLNotExist(yaml)

    @typechecked
    def _get_pod_name(self, pod_name: str,
                      namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method return pod name if exist or raise error
        :param pod_name:
        :param namespace:
        :return:
        """
        try:
            return self.run(f'oc get -n {namespace} pods -o name | grep {pod_name}')
        except Exception as err:
            raise PodNameNotExist(pod_name=pod_name)

    def _is_pod_exist(self, pod_name: str,
                      namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method return True if exist or False if not
        :param pod_name:
        :param namespace:
        :return:
        """
        result = self.run(f'oc get -n {namespace} pods -o name | grep {pod_name}')
        if pod_name in result:
            return True
        else:
            return False

    @typechecked
    def _get_vm_name(self, vm_name: str, namespace: str):
        """
        This method return pod name if exist or raise error
        :return:
        """
        try:
            return self.run(f'oc get -n {namespace} vmi -o name | grep {vm_name}', is_check=True)
        except Exception as err:
            raise VMNameNotExist(vm_name=vm_name)

    @typechecked
    def _is_vm_exist(self, vm_name: str, namespace: str):
        """
        This method return pod name if exist or empty string
        :return:
        """
        result = self.run(f'oc get -n {namespace} vmi -o name | grep {vm_name}')
        if vm_name in result:
            return True
        else:
            return False

    @typechecked()
    def get_long_uuid(self, workload: str):
        """
        This method return uuid
        :return:
        """
        long_uuid = self.run(
            f"oc -n {environment_variables.environment_variables_dict['namespace']} get benchmark/{workload} -o jsonpath={{.status.uuid}}")
        return long_uuid

    def get_prom_token(self):
        """
        This method return prometheus token
        :return:
        """
        long_uuid = self.run(f"oc -n openshift-monitoring sa get-token prometheus-k8s")
        return long_uuid

    @logger_time_stamp
    def login(self):
        """
        This method login to the cluster
        :return:
        """

        try:
            if self.__kubeadmin_password and self.__kubeadmin_password != '':
                self.run(f'oc login -u kubeadmin -p {self.__kubeadmin_password}', is_check=True)
        except Exception as err:
            raise LoginFailed
        return True

    @typechecked
    @logger_time_stamp
    def get_pod(self, label: str, database: str = ''):
        """
        This method get pods according to label
        :param label:
        :param database:
        :return:
        """
        if database:
            return self.run(
                f"oc get pods -n '{database}-db'" + " --no-headers | awk '{ print $1; }' | grep " + database,
                is_check=True).rstrip().decode('ascii')
        else:
            return self.run(
                "oc get pods -n " + environment_variables.environment_variables_dict['namespace'] + " --no-headers | awk '{ print $1; }' | grep " + label,
                is_check=True).rstrip().decode('ascii')

    @typechecked
    @logger_time_stamp
    def get_vm(self, label: str = ''):
        """
        This method get vm according to label
        :param label:
        :return:
        """
        if label:
            return self.run(
                cmd="oc get vmi -n " + environment_variables.environment_variables_dict['namespace'] + " --no-headers | awk '{ print $1; }' | grep " + label,
                is_check=True).rstrip().decode('ascii')
        else:
            return self.run('oc get vmi', is_check=True)

    @typechecked
    @logger_time_stamp
    def save_pod_log(self, pod_name: str, database: str = ''):
        """
        This method save pod log in log_path
        :param pod_name: pod name with uuid
        :param database: database
        :return:
        """
        output_filename = os.path.join(self.__run_artifacts, pod_name)
        if database:
            self.run(f"oc logs -n '{database}-db' {pod_name} > {output_filename} ")
        # manager logs of benchmark-controller-manager
        elif 'benchmark-controller-manager' in pod_name:
            self.run(f"oc logs -n {environment_variables.environment_variables_dict['namespace']} {pod_name} manager > {output_filename} ")
        else:
            self.run(f"oc logs -n {environment_variables.environment_variables_dict['namespace']} {pod_name} > {output_filename} ")

    @typechecked
    @logger_time_stamp
    def save_vm_log(self, vm_name: str):
        """
        This method save vm log in log_path
        :param vm_name: vm name with uuid
        :return:
        """
        output_filename = f"{self.__run_artifacts}/{vm_name}"
        self.run(
            cmd=f"virtctl console -n {environment_variables.environment_variables_dict['namespace']} {vm_name} | tee -a {output_filename} > {output_filename} ",
            background=True)

    @logger_time_stamp
    def get_pods(self):
        """
        This method get pods
        :return:
        """
        return self.run('oc get pods', is_check=True)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_create(self, pod_name: str,
                            namespace: str = environment_variables.environment_variables_dict['namespace'],
                            timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method is wait till pod name is creating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self._is_pod_exist(pod_name=pod_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise PodNotCreateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_create(self, vm_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method is wait till vm name is creating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self._is_vm_exist(vm_name=vm_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMNotCreateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_terminate(self, pod_name: str,
                               namespace: str = environment_variables.environment_variables_dict['namespace'],
                               timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method is wait till pod name is terminating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if not self._is_pod_exist(pod_name=pod_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise PodTerminateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_terminate(self, vm_name: str,
                              namespace: str = environment_variables.environment_variables_dict['namespace'],
                              timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method is wait till vm name is terminating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if not self._is_vm_exist(vm_name=vm_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMTerminateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def create_pod_sync(self, yaml: str, pod_name: str,
                        namespace: str = environment_variables.environment_variables_dict['namespace'],
                        timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method create pod yaml in async
        :param namespace:
        :param timeout:
        :param pod_name:
        :param yaml:
        :return:
        """
        self._create_async(yaml)
        return self.wait_for_pod_create(pod_name=pod_name, namespace=namespace, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def create_vm_sync(self, yaml: str, vm_name: str, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method create vm yaml in async
        :param timeout:
        :param vm_name:
        :param yaml:
        :return:
        """
        self._create_async(yaml)
        return self.wait_for_vm_create(vm_name=vm_name, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def delete_pod_sync(self, yaml: str, pod_name: str,
                        namespace: str = environment_variables.environment_variables_dict['namespace'],
                        timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method delete pod yaml in async, only if exist and return false if not exist
        :param namespace:
        :param timeout:
        :param pod_name:
        :param yaml:
        :return:
        """
        if self._is_pod_exist(pod_name, namespace):
            self._delete_async(yaml)
            return self.wait_for_pod_terminate(pod_name=pod_name, namespace=namespace, timeout=timeout)
        else:
            return False

    @typechecked
    @logger_time_stamp
    def delete_vm_sync(self, yaml: str, vm_name: str,
                       namespace: str = environment_variables.environment_variables_dict['namespace'],
                       timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method delete vm yaml in async, only if exist and return false if not exist
        :param namespace:
        :param timeout:
        :param vm_name:
        :param yaml:
        :return:
        """
        if self._is_vm_exist(vm_name=vm_name, namespace=namespace):
            self._delete_async(yaml)
            return self.wait_for_vm_terminate(vm_name=vm_name, namespace=namespace, timeout=timeout)
        else:
            return False

    @typechecked
    @logger_time_stamp
    def wait_for_initialized(self, label: str, workload: str = '', status: str = 'Initialized', label_uuid: bool = True,
                             namespace: str = environment_variables.environment_variables_dict['namespace'],
                             timeout: int = SHORT_WAIT_TIME):
        """
        This method wait to pod to be initialized
        :param namespace:
        :param label:
        :param status:
        :param label_uuid: The label include uuid
        :param timeout:
        :param workload:
        :return:
        """
        try:
            if label_uuid:
                result = self.run(
                    f"oc --namespace {namespace} wait --for=condition={status} pod -l {label}-{self.__get_short_uuid(workload=workload)} --timeout={timeout}s",
                    is_check=True)
            else:
                return self.run(
                    f"oc --namespace {namespace} wait --for=condition={status} pod -l {label} --timeout={timeout}s",
                    is_check=True)
            if 'met' in result.decode("utf-8"):
                return True
        except Exception as err:
            if 'vm' in workload:
                raise VMNotInitializedTimeout(workload=workload)
            else:
                raise PodNotInitializedTimeout(workload=workload)

    @typechecked
    @logger_time_stamp
    def wait_for_ready(self, label: str, workload: str = '', status: str = 'ready', label_uuid: bool = True,
                       namespace: str = environment_variables.environment_variables_dict['namespace'],
                       timeout: int = SHORT_WAIT_TIME):
        """
        This method wait to pod to be ready
        :param workload:
        :param namespace:
        :param label:
        :param status:
        :param label_uuid:  The label include uuid
        :param timeout:
        :return:
        """
        try:
            if label_uuid:
                result = self.run(
                    f"oc --namespace {namespace} wait --for=condition={status} pod -l {label}-{self.__get_short_uuid(workload=workload)} --timeout={timeout}s",
                    is_check=True)
            else:
                result = self.run(
                    f"oc --namespace {namespace} wait --for=condition={status} pod -l {label} --timeout={timeout}s",
                    is_check=True)
            if 'met' in result.decode("utf-8"):
                return True
        except Exception as err:
            if 'pod' in workload:
                raise PodNotReadyTimeout(workload=workload)
            else:
                raise VMNotReadyTimeout(workload=workload)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_completed(self, label: str, workload: str = '', namespace: str = environment_variables.environment_variables_dict['namespace'], timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method wait to pod to be completed
        :param workload:
        :param label:
        :param timeout:
        :param namespace:
        :return:
        """
        try:
            current_wait_time = 0
            while current_wait_time <= timeout:
                result = self.run(
                    f"oc --namespace {namespace} wait --for=condition=complete -l {label}-{self.__get_short_uuid(workload=workload)} jobs --timeout={OC.SHORT_WAIT_TIME}s")
                if 'met' in result:
                    return True
                result = self.run(
                    f"oc --namespace {namespace} wait --for=condition=failed -l {label}-{self.__get_short_uuid(workload=workload)} jobs --timeout={OC.SLEEP_TIME}s")
                if 'met' in result:
                    return False
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        except Exception as err:
            raise PodNotCompletedTimeout(workload=workload)

    @logger_time_stamp
    def wait_for_vm_completed(self, workload: str = '',
                              namespace: str = environment_variables.environment_variables_dict['namespace'],
                              timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method wait to pod to be completed
        :param workload:
        :param namespace:
        :return:
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self.run(
                    f"oc --namespace {namespace} get benchmark {workload} -o jsonpath={{.status.complete}}") == 'true':
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMNotCompletedTimeout(workload=workload)

    @typechecked
    def exec(self, command: str, pod_name: str, namespace: str = '', container: str = ''):
        """
        oc exec a command and return the answer
        :param command:
        :param pod_name:
        :param namespace:
        :param container:
        :return:
        """
        try:
            if namespace != '':
                namespace = f'-n {namespace}'
            if container != '':
                container = f'-c {container}'
            return self.run(f'oc exec {namespace} {pod_name} {container} -- {command}')
        except Exception as err:
            raise ExecFailed(command, pod_name, err)

    @typechecked
    def terminate_pod_sync(self, pod_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        Delete a pod based on name and namespace only
        :param pod_name:
        :param namespace:
        :param timeout:
        :return:
        """
        if self._is_pod_exist(pod_name, namespace):
            try:
                if namespace != '':
                    namespace = f'-n {namespace}'
                self.run(f'oc delete pod {namespace} {pod_name} timeout={timeout}')
            except Exception as err:
                raise PodTerminateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_ready(self, pod_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        Wait for a pod to be ready and running
        :param pod_name:
        :param namespace:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        self.wait_for_pod_create(pod_name=pod_name, namespace=namespace, timeout=timeout)
        current_wait_time = 0
        if namespace != '':
            namespace=f'-n {namespace}'
        while current_wait_time <= timeout:
            answer = self.run(f'oc get pod {namespace} {pod_name} --no-headers -ocustom-columns=Status:status.phase 2>/dev/null')
            if answer == 'Running':
                return
            elif answer == 'Error':
                raise PodFailed(pod_name)
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise PodNotReadyTimeout(pod_name)

    def __get_num_active_nodes(self):
        """
        This method return the number of active nodes
        :return:
        """
        # count the number of active master/worker nodes
        if self.get_worker_nodes():
            count_nodes = len(self.get_worker_nodes().split())
        else:
            count_nodes = len(self.get_master_nodes().split())
        return count_nodes

    @typechecked
    @logger_time_stamp
    def wait_for_ocp_resource_create(self, resource: str, verify_cmd: str, status: str = '', count_local_storage: bool = False, count_openshift_storage: bool = False, kata_worker_machine_count: bool = False, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method is wait till operator is created or throw exception after timeout
        :param resource: The resource cnv, local storage, ocs, kata
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
                if int(self.run(verify_cmd)) == self.__get_num_active_nodes() * int(environment_variables.environment_variables_dict['num_ocs_disk']):
                    return True
                # Count local storage disks (worker/master * (discovery+manager)
            elif count_local_storage:
                if int(self.run(verify_cmd)) == self.__get_num_active_nodes() * 2:
                    return True
                # Count worker machines
            elif kata_worker_machine_count:
                if int(self.run(verify_cmd)) > 0:
                    return True
                else:
                    return False
            # verify query return positive result
            if status:
                if self.run(verify_cmd) == status:
                    return True
            else:
                if self.run(verify_cmd) != '':
                    return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise OCPResourceNotCreateTimeout(resource)

    @typechecked
    @logger_time_stamp
    def create_cnv(self, path: str, resource_list: list):
        """
        This method create cnv resource
        :param path:path of resource files
        :param resource_list: cnv resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            self._create_async(yaml=os.path.join(path, resource))
            # for first script wait for virt-operator
            if '01_subscription.yaml' in resource:
                # Wait that cnv operator will be created
                self.wait_for_ocp_resource_create(resource='cnv',
                                                  verify_cmd='oc -n openshift-cnv wait deployment/virt-operator --for=condition=Available',
                                                  status='deployment.apps/virt-operator condition met')
            # for second script wait for refresh status
            else:
                time.sleep(10)
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
            self._create_async(yaml=os.path.join(path, resource))
        # verify once after create all resource files
        self.wait_for_ocp_resource_create(resource='local_storage',
                                          verify_cmd="oc -n openshift-local-storage wait deployment/local-storage-operator --for=condition=Available",
                                          status='deployment.apps/local-storage-operator condition met')
        return True

    @typechecked
    @logger_time_stamp
    def create_ocs(self, path: str, resource_list: list, ibm_blk_disk_name: list):
        """
        This method create ocs
        :param ibm_blk_disk_name: ibm ocs disk blk name
        :param path:path of resource files
        :param resource_list: ocs resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                # build sgdisks path dynamically
                if '01_sgdisks.sh' == resource:
                    sgdisks_cmd = ''
                    for disk_name in ibm_blk_disk_name:
                        sgdisks_cmd += f'sgdisk --zap-all /dev/{disk_name};'
                    self.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource} "{sgdisks_cmd}"')
                else:
                    self.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource}')
            else:  # yaml
                self._create_async(yaml=os.path.join(path, resource))
                if '04_local_volume_set.yaml' in resource:
                    # openshift local storage
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd=r"""oc get pod -n openshift-local-storage -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep diskmaker""")
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd=r"""oc get pod -n openshift-local-storage -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep diskmaker | wc -l""", count_local_storage=True)
                    # openshift persistence volume (pv)
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd=r"""oc get pv -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep local""")
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd=r"""oc get pv -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep local | wc -l""",
                                                      count_openshift_storage=True)
                elif '07_subscription.yaml' in resource:
                    # wait till ocs operator installed
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd="oc -n openshift-storage wait deployment/ocs-operator --for=condition=Available",
                                                      status='deployment.apps/ocs-operator condition met')
                elif '08_storage_cluster.yaml' in resource:
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd=r"""oc get pod -n openshift-storage | grep osd | grep -v prepare""")
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd="oc get csv -n openshift-storage -ojsonpath='{.items[0].status.phase}'",
                                                      status='Succeeded')
                    self.wait_for_ocp_resource_create(resource='ocs',
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
            if resource.endswith('.yaml'):
                self._create_async(yaml=os.path.join(path, resource))
                # for first script wait for virt-operator
                if '01_operator.yaml' == resource:
                    # Wait that cnv operator will be created
                    self.wait_for_ocp_resource_create(resource='kata',
                                                      verify_cmd='oc -n openshift-sandboxed-containers-operator wait deployment/sandboxed-containers-operator-controller-manager --for=condition=Available',
                                                      status='deployment.apps/sandboxed-containers-operator-controller-manager condition met')
                # for second script wait for kataconfig installation to no longer be in progress
                elif '02_config.yaml' == resource:
                    self.wait_for_ocp_resource_create(resource='kata',
                                                      verify_cmd="oc get kataconfig -ojsonpath='{.items[0].status.installationStatus.IsInProgress}'",
                                                      status='false')
                    total_nodes_count = self.run(cmd="oc get kataconfig -ojsonpath='{.items[0].status.total_nodes_count}'")
                    completed_nodes_count = self.run(cmd="oc get kataconfig -ojsonpath='{.items[0].status.installationStatus.completed.completed_nodes_count}'")
                    if total_nodes_count != completed_nodes_count:
                        raise KataInstallationFailed(f'not all nodes installed successfully total {total_nodes_count} != completed {completed_nodes_count}')
            else:
                if '03_ocp48_patch.sh' == resource:
                    self.run(cmd=f'chmod +x {os.path.join(path, resource)}; {path}/./{resource}')
        return True
