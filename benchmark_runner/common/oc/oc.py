
import os
import time
from typeguard import typechecked
from tenacity import retry, stop_after_attempt

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc_exceptions import PodNotCreateTimeout, PodNotInitializedTimeout, PodNotReadyTimeout, \
    PodNotCompletedTimeout, PodTerminateTimeout, PodNameNotExist, LoginFailed, VMNotCreateTimeout, VMTerminateTimeout, \
    YAMLNotExist, VMNameNotExist, VMNotInitializedTimeout, VMNotReadyTimeout, VMNotCompletedTimeout, \
    OCPResourceNotCreateTimeout
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.main.environment_variables import environment_variables


class OC(SSH):
    """
    This class run OC commands
    """
    # time out for all waits is 5000 sec
    TIME_OUT = 5000
    # wait time out
    SHORT_WAIT_TIME = 300
    # sleep time between checks is 5 sec
    SLEEP_TIME = 3

    def __init__(self, kubeadmin_password: str = ''):
        super().__init__()
        self.__kubeadmin_password = kubeadmin_password
        self.__environment_variables_dict = environment_variables.environment_variables_dict

    def get_ocp_server_version(self):
        """
        This method return ocp server version
        :return:
        """
        return self.run("oc version -o json | jq '.openshiftVersion'")

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
    def _get_vmi_name(self, vm_name: str, namespace: str):
        """
        This method return pod name if exist or raise error
        :return:
        """
        try:
            return self.run(f'oc get -n {namespace} vmi -o name | grep {vm_name}', is_check=True)
        except Exception as err:
            raise VMNameNotExist(vm_name=vm_name)

    @typechecked
    def _is_vmi_exist(self, vm_name: str, namespace: str):
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

    @logger_time_stamp
    def get_pods(self):
        """
        This method get pods
        :return:
        """
        return self.run('oc get pods', is_check=True)

    @logger_time_stamp
    def get_vmi(self):
        """
        This method get vmi
        :return:
        """
        return self.run('oc get vmi', is_check=True)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_create(self, pod_name: str,
                            namespace: str = environment_variables.environment_variables_dict['namespace'],
                            timeout: int = TIME_OUT, sleep_time: int = SLEEP_TIME):
        """
        This method is wait till pod name is creating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param sleep_time:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self._is_pod_exist(pod_name=pod_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise PodNotCreateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_create(self, vm_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = TIME_OUT, sleep_time: int = SLEEP_TIME):
        """
        This method is wait till vm name is creating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param sleep_time:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self._is_vmi_exist(vm_name=vm_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise VMNotCreateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_terminate(self, pod_name: str,
                               namespace: str = environment_variables.environment_variables_dict['namespace'],
                               timeout: int = TIME_OUT, sleep_time: int = SLEEP_TIME):
        """
        This method is wait till pod name is terminating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param sleep_time:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if not self._is_pod_exist(pod_name=pod_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise PodTerminateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_terminate(self, vm_name: str,
                              namespace: str = environment_variables.environment_variables_dict['namespace'],
                              timeout: int = TIME_OUT, sleep_time: int = SLEEP_TIME):
        """
        This method is wait till vm name is terminating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param sleep_time:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if not self._is_vmi_exist(vm_name=vm_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise VMTerminateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def create_pod_sync(self, yaml: str, pod_name: str,
                        namespace: str = environment_variables.environment_variables_dict['namespace'],
                        timeout: int = TIME_OUT):
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
    def create_vm_sync(self, yaml: str, vm_name: str, timeout: int = TIME_OUT):
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
                        timeout: int = TIME_OUT):
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
                       timeout: int = TIME_OUT):
        """
        This method delete vm yaml in async, only if exist and return false if not exist
        :param namespace:
        :param timeout:
        :param vm_name:
        :param yaml:
        :return:
        """
        if self._is_vmi_exist(vm_name=vm_name, namespace=namespace):
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
    def wait_for_pod_completed(self, label: str, workload: str = '',
                               namespace: str = environment_variables.environment_variables_dict['namespace'],
                               timeout: int = TIME_OUT):
        """
        This method wait to pod to be completed
        :param workload:
        :param namespace:
        :param label:
        :param timeout:
        :return:
        """
        try:
            result = self.run(
                f"oc --namespace {namespace} wait --for=condition=complete -l {label}-{self.__get_short_uuid(workload=workload)} jobs --timeout={timeout}s")
            if 'met' in result:
                return True
        except Exception as err:
            raise PodNotCompletedTimeout(workload=workload)

    @logger_time_stamp
    def wait_for_vm_completed(self, workload: str = '',
                              namespace: str = environment_variables.environment_variables_dict['namespace'],
                              timeout: int = TIME_OUT, sleep_time: int = SLEEP_TIME):
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
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise VMNotCompletedTimeout(workload=workload)

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
    def wait_for_ocp_resource_create(self, resource: str, verify_cmd: str, status: str = '', count_local_storage: bool = False, count_openshift_storage: bool = False, kata_worker_machine_count: bool = False, timeout: int = TIME_OUT,
                                     sleep_time: int = SLEEP_TIME):
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
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise OCPResourceNotCreateTimeout(resource)

    @typechecked
    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
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
                                              verify_cmd="oc get csv -n openshift-cnv $(oc get csv -n openshift-cnv --no-headers | awk '{ print $1; }') -ojsonpath='{.status.phase}'",
                                              status='Succeeded')
        return True

    @typechecked
    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
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
    @retry(stop=stop_after_attempt(3))
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
                                                      verify_cmd="oc get csv -n openshift-storage $(oc get csv -n openshift-storage --no-headers | awk '{ print $1; }') -ojsonpath='{.status.phase}'",
                                                      status='Succeeded')
                    self.wait_for_ocp_resource_create(resource='ocs',
                                                      verify_cmd='oc get pod -n openshift-storage | grep osd | grep -v prepare | wc -l',
                                                      count_openshift_storage=True)
        return True

    @typechecked
    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def create_kata(self, path: str, resource_list: list):
        """
        This method create kata resource
        :param path:path of resource files
        :param resource_list: kata resource lists
        :return:
        """
        for resource in resource_list:
            logger.info(f'run {resource}')
            self._create_async(yaml=os.path.join(path, resource))
            # for first script wait for virt-operator
            if '01_operator.yaml' in resource:
                # Wait that cnv operator will be created
                self.wait_for_ocp_resource_create(resource='kata',
                                                  verify_cmd='oc -n openshift-sandboxed-containers-operator wait deployment/controller-manager --for=condition=Available',
                                                  status='deployment.apps/controller-manager condition met')
            # for second script wait for refresh status
            else:
                # verify if there are workers nodes
                if self.wait_for_ocp_resource_create(resource='ocs',
                                                  verify_cmd="oc get mcp -n openshift-sandboxed-containers-operator $( oc get mcp -n openshift-sandboxed-containers-operator --no-headers | awk '{ print $1; }' | awk NR==2) -ojsonpath='{.status.machineCount}'",
                                                  kata_worker_machine_count=True):
                    # Wait till workers UPDATED==True
                    self.wait_for_ocp_resource_create(resource='kata',
                                                      verify_cmd="oc get mcp -n openshift-sandboxed-containers-operator $( oc get mcp -n openshift-sandboxed-containers-operator --no-headers | awk '{ print $1; }' | awk NR==2) -ojsonpath='{.status.conditions[3].status}'",
                                                      status='True')
                # There are only master nodes
                else:
                    # Wait till masters UPDATED==True
                    self.wait_for_ocp_resource_create(resource='kata',
                                                      verify_cmd="oc get mcp -n openshift-sandboxed-containers-operator $( oc get mcp -n openshift-sandboxed-containers-operator --no-headers | awk '{ print $1; }' | awk NR==1) -ojsonpath='{.status.conditions[3].status}'",
                                                      status='True')
        return True
