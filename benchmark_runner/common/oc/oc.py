
import os
import ast
import time
from enum import Enum
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc_exceptions import PodNotCreateTimeout, PodNotInitializedTimeout, PodNotReadyTimeout, \
    PodNotCompletedTimeout, PodTerminateTimeout, PodNameNotExist, LoginFailed, VMNotCreateTimeout, VMDeleteTimeout, \
    YAMLNotExist, VMNameNotExist, VMNotInitializedTimeout, VMNotReadyTimeout, VMStateTimeout, VMNotCompletedTimeout, ExecFailed, PodFailed, DVStatusTimeout
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.main.environment_variables import environment_variables


class VMStatus(Enum):
    Stopped = 'Stopped'
    Starting = 'Starting'
    Running = 'Running'


class OC(SSH):
    """
    This class run OC commands
    """

    SHORT_TIMEOUT = 600
    # sleep time between checks is 5 sec
    SLEEP_TIME = 3

    def __init__(self, kubeadmin_password: str = ''):
        super().__init__()
        self.__kubeadmin_password = kubeadmin_password
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self._run_artifacts = self.__environment_variables_dict.get('run_artifacts_path', '')
        self.__elasticsearch_url = self.__environment_variables_dict.get('elasticsearch_url', '')
        self.__kata_csv = self.__environment_variables_dict.get('kata_csv', '')
        self.__cli = self.__environment_variables_dict.get('cli', '')
        self.__worker_disk_prefix = self.__environment_variables_dict.get('worker_disk_prefix', '')
        self.__worker_disk_ids = self.__environment_variables_dict.get('worker_disk_ids', '')
        if self.__worker_disk_ids:
            self.__worker_disk_ids = ast.literal_eval(self.__worker_disk_ids)

    def get_ocp_server_version(self):
        """
        This method returns ocp server version
        :return:
        """
        return self.run(f"{self.__cli} get clusterversion version -o jsonpath='{{.status.desired.version}}'")

    def get_cnv_version(self):
        """
        This method returns cnv version
        :return:
        """
        return self.run(f"{self.__cli} get csv -n openshift-cnv $(oc get csv -n openshift-cnv --no-headers | awk '{{ print $1; }}') -ojsonpath='{{.spec.version}}'")

    def get_odf_version(self):
        """
        This method returns odf version
        :return:
        """
        return self.run(f"{self.__cli} get csv -n openshift-storage -ojsonpath='{{.items[0].spec.labels.full_version}}'")

    def remove_lso_path(self):
        """
        The method removes lso path on each node
        @return:
        """
        self.run(fr"""{self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\\n'}}{{end}}" |  xargs -I{{}} oc debug node/{{}} -- chroot /host sh -c "rm -rf /mnt/local-storage/local-sc" """)

    def get_worker_disk_ids(self):
        """
        The method returns worker disk ids only when there are worker disk ids
        """
        workers_disk_ids = []
        if self.__worker_disk_ids:
            for node, disk_ids in self.__worker_disk_ids.items():
                for disk_id in disk_ids:
                    workers_disk_ids.append(disk_id)
        return workers_disk_ids

    def get_pv_disk_ids(self):
        """
        This method returns list of pv disk ids
        """
        pv_ids = self.run(f"{self.__cli} get pv -o jsonpath={{.items[*].metadata.annotations.'storage\.openshift\.com/device-id'}}")
        # SATA disks in /dev/disk/by-id conventionally are prefixed with `wwn-0x` and `scsi-3`; ODF requires use of the `wwn-0x` prefix while LSO requires the `scsi-3` prefix.  We have to be prepared to use either prefix, but as they are the same length, we can presently strip the first 6 characters of the name.
        return [pv[len(self.__worker_disk_prefix):] for pv in pv_ids.split()]

    def get_free_disk_id(self):
        """
        This method returns free disk (workers_all_disk_ids - workers_odf_pv_disk_ids) with its prefix only when there are worker disk ids
        """
        workers_disk_ids = self.get_worker_disk_ids()
        workers_pv_disk_ids = self.get_pv_disk_ids()
        free_disk_id = f'{self.__worker_disk_prefix}{list(set(workers_disk_ids) - set(workers_pv_disk_ids))[0]}'
        if free_disk_id:
            return free_disk_id
        else:
            raise Exception('Missing free disk id')

    @typechecked
    def run_debug_node(self, node: str, cmd: str):
        """
        This method runs command in debug node
        :param: node
        :param: cmd
        :return:
        """
        self.run(f"{self.__cli} debug node/{node} --no-tty=true -- chroot /host sh -c '{cmd}'")

    def get_kata_operator_version(self):
        """
        This method returns kata operator version
        :return:
        """
        return self.run(f"{self.__cli} get csv -n openshift-sandboxed-containers-operator $({self.__cli} get csv -n openshift-sandboxed-containers-operator --no-headers | awk '{{ print $1; }}') -ojsonpath='{{.spec.version}}'")

    @typechecked
    def get_kata_rpm_version(self, node: str):
        """
        This method returns sandboxed containers (kata) rpm version
        @param: node
        :return:
        """
        kata_rpm_version = self.run(f"{self.__cli} debug node/{node} -- chroot /host rpm -q --queryformat='%{{VERSION}}-%{{RELEASE}}' kata-containers 2>/dev/null")
        return '.'.join(kata_rpm_version.split('.')[:3])

    def _get_kata_default_channel(self):
        """
        This method retrieves the default channel for Kata
        """
        return self.run(f"{self.__cli} get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojsonpath='{{.status.defaultChannel}}'")

    def _get_kata_default_channel_field(self, channel_field: str):
        """
        This method retrieves a field from the packagemanifest for the default Kata channel
        """
        default_channel = f'"{self._get_kata_default_channel()}"'
        command = f"{self.__cli} get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojson | jq -r '[foreach .status.channels[] as $channel ([[],[]];0;(if ($channel.name == {default_channel}) then $channel.{channel_field} else null end))] | flatten | map (select (. != null))[]'"
        return self.run(command)

    def _get_kata_csv(self):
        """
        This method retrieves the CSV of the sandboxed containers operator for installation"
        """
        return self._get_kata_default_channel_field("currentCSV")

    def _get_kata_catalog_source(self):
        """
        This method retrieves the catalog source of the sandboxed containers operator for installation"
        """
        return self.run(f"{self.__cli} get packagemanifest -n openshift-marketplace sandboxed-containers-operator -ojsonpath='{{.status.catalogSource}}'")

    def _get_kata_channel(self):
        """
        This method retrieves the channel of the sandboxed containers operator for installation"
        """
        return self._get_kata_default_channel_field("name")

    def _get_kata_namespace(self):
        """
        This method retrieves the namespace of the sandboxed containers operator for installation"
        """
        return self._get_kata_default_channel_field('currentCSVDesc.annotations."operatorframework.io/suggested-namespace"')

    def set_kata_threads_pool(self, thread_pool_size: str):
        """
        This method sets kata thread-pool-size in every worker node
        @param thread_pool_size:
        @return:
        """
        self.run(fr"""{self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\\n'}}{{end}}" |  xargs -I{{}} oc debug node/{{}} -- chroot /host sh -c "mkdir -p /etc/kata-containers; cp /usr/share/kata-containers/defaults/configuration.toml /etc/kata-containers/; sed -i 's/thread-pool-size=1/thread-pool-size={thread_pool_size}/' /etc/kata-containers/configuration.toml" """)

    def delete_kata_threads_pool(self):
        """
        This method deletes kata thread-pool-size from every worker node
        @return:
        """
        self.run(fr"""{self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\\n'}}{{end}}" |  xargs -I{{}} oc debug node/{{}} -- chroot /host sh -c "rm -f /etc/kata-containers/configuration.toml" """)

    @typechecked
    def populate_additional_template_variables(self, env: dict):
        """
        This method populates any additional variables needed for setup templates
        """
        if self.__kata_csv:  # custom kata version
            env['kata_csv'] = self.__kata_csv
        else:  # latest kata version
            env['kata_csv'] = self._get_kata_csv()
        env['kata_channel'] = self._get_kata_channel()
        env['kata_catalog_source'] = self._get_kata_catalog_source()
        env['kata_namespace'] = self._get_kata_namespace()

    def is_cnv_installed(self):
        """
        This method checks if cnv operator is installed
        :return:
        """
        verify_cmd = f"{self.__cli} get csv -n openshift-cnv -ojsonpath='{{.items[0].status.phase}}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def is_odf_installed(self):
        """
        This method checks if odf operator is installed
        :return:
        """
        verify_cmd = f"{self.__cli} get csv -n openshift-storage -ojsonpath='{{.items[0].status.phase}}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def check_dv_status(self,
                        status: str,
                        namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method checks dv status
        :return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        verify_cmd = f"{self.__cli} get dv {namespace} -ojsonpath='{{.items[].status.phase}}'"
        if status in self.run(verify_cmd):
            return True
        return False

    @typechecked
    @logger_time_stamp
    def wait_for_dv_status(self,
                           status: str = 'Succeeded',
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits for methods status
        @return: True/ False if reach to status
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            if self.check_dv_status(status=status):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise DVStatusTimeout(status=status)

    def verify_odf_installation(self, namespace: str = 'openshift-storage'):
        """
        This method verifies ODF installation
        :return: True ODF passed, False failed
        """
        self.run(
            f"oc patch storagecluster ocs-storagecluster -n {namespace} --type json --patch '[{{ \"op\": \"replace\", \"path\": \"/spec/enableCephTools\", \"value\": true }}]'")
        self.wait_for_patch(pod_name='rook-ceph-tools', label='app=rook-ceph-tools', label_uuid=False, namespace=namespace)
        health_check = self.run(
            f"oc -n {namespace} rsh {self._get_pod_name(pod_name='rook-ceph-tools', namespace=namespace)} ceph health")
        return 'HEALTH_OK' == health_check.strip()

    def get_odf_disk_count(self):
        """
        This method returns odf disk count
        :return:
        """
        if self.is_odf_installed():
            return int(self.run(f"{self.__cli} get --no-headers pod -n openshift-storage | grep osd | grep -cv prepare"))

    def is_kata_installed(self):
        """
        This method checks if kata operator is installed
        :return:
        """
        verify_cmd = "oc get csv -n openshift-sandboxed-containers-operator -ojsonpath='{.items[0].status.phase}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def get_master_nodes(self):
        """
        This method returns master nodes
        :return:
        """
        return self.run(fr""" {self.__cli} get nodes -l node-role.kubernetes.io/master= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\n'}}{{end}}" """)

    def get_worker_nodes(self):
        """
        This method returns worker nodes
        :return:
        """
        return self.run(fr""" {self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\n'}}{{end}}" """)

    def delete_available_released_pv(self):
        """
        This method deletes available or released pv because that avoid launching new pv
        """
        pv_status_list = self.run(fr"{self.__cli} get pv -ojsonpath={{..status.phase}}").split()
        for ind, pv_status in enumerate(pv_status_list):
            if pv_status == 'Available' or pv_status == 'Released':
                available_pv = self.run(fr"{self.__cli} get pv -ojsonpath={{.items[{ind}].metadata.name}}")
                logger.info(f'Delete {pv_status} pv {available_pv}')
                self.run(fr"{self.__cli} delete pv {available_pv}")

    def clear_node_caches(self):
        """
        This method clears the node's buffer cache
        """
        return self.run(fr""" {self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\n'}}{{end}}" |  xargs -I{{}} {self.__cli} debug node/{{}} -- chroot /host sh -c "sync; echo 3 > /proc/sys/vm/drop_caches" """)

    def __get_short_uuid(self, workload: str):
        """
        This method returns uuid
        :return:
        """
        long_uuid = self.get_long_uuid(workload=workload)
        uuids = long_uuid.split('-')
        short_uuid = uuids[0]
        return short_uuid

    def get_num_active_nodes(self):
        """
        This method returns the number of active nodes
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
    def apply_security_privileged(self, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method applies security privileged for namespace
        @param namespace:
        @return:
        """
        return self.run(f"{self.__cli} create serviceaccount -n {namespace} {namespace}; "
                        f"{self.__cli} adm policy add-scc-to-user -n {namespace} privileged -z {namespace}")

    @typechecked
    @logger_time_stamp
    def create_async(self, yaml: str, is_check: bool = False):
        """
        This method creates yaml in async
        @param yaml:
        @param is_check:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'{self.__cli} create -f {yaml}', is_check=is_check)
        else:
            raise YAMLNotExist(yaml)

    @typechecked
    @logger_time_stamp
    def delete_async(self, yaml: str):
        """
        This method deletes yaml in async
        :param yaml:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'{self.__cli} delete -f {yaml}')
        else:
            raise YAMLNotExist(yaml)

    @typechecked
    def _get_pod_name(self, pod_name: str,
                      namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns pod name if exist or raise error
        :param pod_name:
        :param namespace:
        :return:
        """
        try:
            namespace = f'-n {namespace}' if namespace else ''
            return self.run(f'{self.__cli} get {namespace} pods -o name | grep {pod_name}')
        except Exception as err:
            raise PodNameNotExist(pod_name=pod_name)

    def pod_exists(self, pod_name: str,
                   namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns True if exist or False if not
        :param pod_name:
        :param namespace:
        :return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        result = self.run(f'{self.__cli} get {namespace} pods -o name | grep {pod_name}')
        if pod_name in result:
            return True
        else:
            return False

    def pod_label_exists(self, label_name: str,
                         namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns True if pod exist or not by label
        :param label_name:
        :param namespace:
        :return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        result = self.run(f"{self.__cli} get {namespace} pod -l={label_name} -ojsonpath='{{.items}}'")
        if result != '[]':
            return True
        else:
            return False

    @typechecked()
    def get_long_uuid(self, workload: str):
        """
        This method returns uuid
        :return:
        """
        long_uuid = self.run(
            f"{self.__cli} -n {environment_variables.environment_variables_dict['namespace']} get benchmark/{workload} -o jsonpath={{.status.uuid}}")
        return long_uuid

    def get_ocp_major_version(self):
        """
        This method returns ocp major version
        @return:
        """
        return int(self.get_ocp_server_version().split('.')[0])

    def get_ocp_minor_version(self):
        """
        This method returns ocp minor version
        @return:
        """
        return int(self.get_ocp_server_version().split('.')[1])

    def get_prom_token(self):
        """
        This method returns prometheus token
        :return:
        """
        # OCP 4.10 and below
        if self.get_ocp_major_version() <= 4 and self.get_ocp_minor_version() <= 10:
            prom_token = self.run(f"{self.__cli} -n openshift-monitoring sa get-token prometheus-k8s")
        else:
            prom_token = self.run(f"{self.__cli} sa new-token -n openshift-monitoring prometheus-k8s 2>/dev/null")
        return prom_token

    def collect_events(self):
        """
        This method collects event log
        :return: output_filename
        """
        output_filename = os.path.join(self._run_artifacts, f'events.log')
        self.run(f"{self.__cli} get events -A > '{output_filename}' ")
        return output_filename

    @logger_time_stamp
    def login(self):
        """
        This method logs in to the cluster
        :return:
        """
        try:
            if self.__kubeadmin_password and self.__kubeadmin_password != '':
                self.run(f'{self.__cli} login -u kubeadmin -p {self.__kubeadmin_password}', is_check=True)
        except Exception as err:
            raise LoginFailed
        return True

    @typechecked
    @logger_time_stamp
    def get_pod(self, label: str, database: str = '', namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method gets pods according to label
        :param label:
        :param database:
        :param namespace:
        :return:
        """
        if database:
            return self.run(
                f"{self.__cli} get pods -n '{database}-db'" + " --no-headers | awk '{ print $1; }' | grep " + database,
                is_check=True).rstrip().decode('ascii')
        else:
            namespace = f'-n {namespace}' if namespace else ''
            return self.run(f"{self.__cli} get pods {namespace} --no-headers | awk '{{ print $1; }}' | grep -w '{label}'", is_check=True).rstrip().decode('ascii')

    @typechecked
    @logger_time_stamp
    def save_pod_log(self, pod_name: str, database: str = '', log_type: str = ''):
        """
        This method saves pod log in log_path
        :param pod_name: pod name with uuid
        :param database: database
        :param log_type: log type extension
        :return: output_filename
        """
        if log_type:
            output_filename = os.path.join(self._run_artifacts, f'{pod_name}{log_type}')
        else:
            output_filename = os.path.join(self._run_artifacts, pod_name)
        if database:
            self.run(f"{self.__cli} logs -n '{database}-db' {pod_name} > '{output_filename}' ")
        # manager logs of benchmark-controller-manager
        elif 'benchmark-controller-manager' in pod_name:
            self.run(f"{self.__cli} logs -n {environment_variables.environment_variables_dict['namespace']} {pod_name} manager > '{output_filename}' ")
        else:
            self.run(f"{self.__cli} logs -n {environment_variables.environment_variables_dict['namespace']} {pod_name} > '{output_filename}' ")
        return output_filename

    def describe_pod(self, pod_name: str, namespace: str = ''):
        """
        This method describes pod into log
        :param pod_name: pod name with uuid
        :param namespace: namespace
        :return: output_filename
        """
        output_filename = os.path.join(self._run_artifacts, f'describe-{pod_name}')
        self.run(f"{self.__cli} describe pod -n {namespace} {pod_name} > '{output_filename}' ")
        return output_filename

    @logger_time_stamp
    def get_pods(self):
        """
        This method retrieves information on benchmark-runner pods in oc get pod format
        :return:
        """
        return self.run(f'{self.__cli} get pods', is_check=True)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_create(self, pod_name: str,
                            namespace: str = environment_variables.environment_variables_dict['namespace'],
                            timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits till pod name is creating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            if self.pod_exists(pod_name=pod_name, namespace=namespace):
                self.describe_pod(pod_name=pod_name, namespace=namespace)
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        self.describe_pod(pod_name=pod_name, namespace=namespace)
        raise PodNotCreateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_terminate(self, pod_name: str,
                               namespace: str = environment_variables.environment_variables_dict['namespace'],
                               timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits till pod name is terminating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            if not self.pod_exists(pod_name=pod_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise PodTerminateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def create_pod_sync(self, yaml: str, pod_name: str,
                        namespace: str = environment_variables.environment_variables_dict['namespace'],
                        timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method creates pod yaml in async
        :param namespace:
        :param timeout:
        :param pod_name:
        :param yaml:
        :return:
        """
        self.create_async(yaml)
        return self.wait_for_pod_create(pod_name=pod_name, namespace=namespace, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def delete_pod_sync(self, yaml: str, pod_name: str,
                        namespace: str = environment_variables.environment_variables_dict['namespace'],
                        timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method deletes pod yaml in async, only if exist and return false if not exist
        :param namespace:
        :param timeout:
        :param pod_name:
        :param yaml:
        :return:
        """
        if self.pod_exists(pod_name, namespace):
            self.delete_async(yaml)
            return self.wait_for_pod_terminate(pod_name=pod_name, namespace=namespace, timeout=timeout)
        else:
            return False

    @typechecked
    def delete_namespace(self, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method deletes namespace
        :param namespace:
        :return:
        """
        self.run(f'{self.__cli} delete ns {namespace}')

    @typechecked
    @logger_time_stamp
    def wait_for_initialized(self, label: str, workload: str = '', status: str = 'Initialized', label_uuid: bool = True,
                             namespace: str = environment_variables.environment_variables_dict['namespace'],
                             timeout: int = SHORT_TIMEOUT):
        """
        This method waits to pod to be initialized
        :param namespace:
        :param label:
        :param status:
        :param label_uuid: need to get uuid from label (benchmark-operator)
        :param timeout:
        :param workload:
        :return:
        """
        try:
            namespace = f'-n {namespace}' if namespace else ''
            if label_uuid:
                result = self.run(
                    f"{self.__cli} {namespace} wait --for=condition={status} pod -l {label}-{self.__get_short_uuid(workload=workload)} --timeout={timeout}s",
                    is_check=True)
            else:
                return self.run(
                    f"{self.__cli} {namespace} wait --for=condition={status} pod -l {label} --timeout={timeout}s",
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
    def wait_for_patch(self, pod_name: str, label: str, label_uuid: bool, namespace: str, timeout: int = SHORT_TIMEOUT):
        """
        This method waits for patch, needs to wait that pod is created and then wait for ready
        @param pod_name:
        @param label:
        @param label_uuid:
        @param namespace:
        @param timeout:
        @return:
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            if self._get_pod_name(pod_name=pod_name, namespace=namespace) and self.wait_for_ready(label=label, label_uuid=label_uuid, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise PodNotReadyTimeout(label)

    @typechecked
    @logger_time_stamp
    def wait_for_ready(self, label: str, run_type: str = 'pod', workload: str = '', status: str = 'ready', label_uuid: bool = True,
                       namespace: str = environment_variables.environment_variables_dict['namespace'],
                       timeout: int = SHORT_TIMEOUT):
        """
        This method waits for the pod/vm to be ready
        :param label:
        :param run_type:pod or vm
        :param workload:
        :param namespace:
        :param status:
        :param label_uuid: need to get uuid from label (benchmark-operator)
        :param timeout:
        :return:
        """
        try:
            namespace = f'-n {namespace}' if namespace else ''
            if label_uuid:
                result = self.run(
                    f"{self.__cli} {namespace} wait --for=condition={status} {run_type} -l {label}-{self.__get_short_uuid(workload=workload)} --timeout={timeout}s",
                    is_check=True)
            else:
                result = self.run(
                    f"{self.__cli} {namespace} wait --for=condition={status} {run_type} -l {label} --timeout={timeout}s",
                    is_check=True)
            if 'met' in result.decode("utf-8"):
                return True
        except Exception as err:
            if 'vm' in workload:
                raise VMNotReadyTimeout(workload=workload)
            else:
                raise PodNotReadyTimeout(workload=workload)

    @typechecked
    def exec(self, command: str, pod_name: str, namespace: str = environment_variables.environment_variables_dict['namespace'], container: str = ''):
        """
        This method executes a command within a specified pod and optional container and returns the output
        :param command:
        :param pod_name:
        :param namespace:
        :param container:
        :return:
        """
        try:
            namespace = f'-n {namespace}' if namespace else ''
            container = f'-c {container}' if container else ''
            return self.run(f'{self.__cli} exec {namespace} {pod_name} {container} -- {command}')
        except Exception as err:
            raise ExecFailed(command, pod_name, err)

    @typechecked
    def terminate_pod_sync(self, pod_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method deletes a pod based on name and namespace only
        :param pod_name:
        :param namespace:
        :param timeout:
        :return:
        """
        if self.pod_exists(pod_name, namespace):
            try:
                namespace = f'-n {namespace}' if namespace else ''
                self.run(f'{self.__cli} delete pod {namespace} {pod_name} timeout={timeout}')
            except Exception as err:
                raise PodTerminateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_ready(self, pod_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits for a pod to be ready and running
        :param pod_name:
        :param namespace:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        self.wait_for_pod_create(pod_name=pod_name, namespace=namespace, timeout=timeout)
        current_wait_time = 0
        namespace = f'-n {namespace}' if namespace else ''
        while timeout <= 0 or current_wait_time <= timeout:
            answer = self.run(f'{self.__cli} get pod {namespace} {pod_name} --no-headers -ocustom-columns=Status:status.phase 2>/dev/null')
            if answer == 'Running':
                return
            elif answer == 'Error':
                raise PodFailed(pod_name)
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise PodNotReadyTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_completed(self, label: str, workload: str = '', label_uuid: bool = True, job: bool = True,
                               namespace: str = environment_variables.environment_variables_dict['namespace'],
                               timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits for a pod to be completed
        :param workload:
        :param label:
        :param label_uuid: need to get uuid from label (benchmark-operator)
        :param job: kind is job instead of pod
        :param timeout:
        :param namespace:
        :return:
        """
        try:
            current_wait_time = 0
            namespace = f'-n {namespace}' if namespace else ''
            while current_wait_time <= timeout:
                if label_uuid and job:
                    result = self.run(
                        f"{self.__cli} {namespace} wait --for=condition=complete -l {label}-{self.__get_short_uuid(workload=workload)} jobs --timeout={OC.SHORT_TIMEOUT}s")
                    if 'met' in result:
                        return True
                    result = self.run(
                        f"{self.__cli} {namespace} wait --for=condition=failed -l {label}-{self.__get_short_uuid(workload=workload)} jobs --timeout={OC.SLEEP_TIME}s")
                    if 'met' in result:
                        return False
                if not job:
                    result = self.run(f"{self.__cli} get pod -l {label}" + " -n benchmark-runner --no-headers | awk '{ print $3; }'")
                    if 'Completed' in result:
                        return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        except Exception as err:
            raise PodNotCompletedTimeout(workload=workload)

    def describe_vmi(self, vm_name: str, namespace: str):
        """
        This method describes vmi into log
        :param vm_name: vm name with uuid
        :param namespace: namespace
        :return: output_filename
        """
        output_filename = os.path.join(self._run_artifacts, f'describe-{vm_name}')
        self.run(f"{self.__cli} describe vmi -n {namespace} {vm_name} > '{output_filename}' ")
        return output_filename

    @typechecked
    def _get_vm_name(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns VM name if the vm exists, otherwise raise VMNameNotExist exception
        :param vm_name:
        :param namespace:
        :return: VM name or raise VMNameNotExist
        """
        try:
            namespace = f'-n {namespace}' if namespace else ''
            return self.run(f'{self.__cli} get {namespace} vmi -o name | grep {vm_name}', is_check=True)
        except Exception as err:
            raise VMNameNotExist(vm_name=vm_name)

    @typechecked
    def vm_exists(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns True or False if vm name exist
        :param vm_name:
        :param namespace:
        :return: True or False
        """
        namespace = f'-n {namespace}' if namespace else ''
        result = self.run(f'{self.__cli} get {namespace} vmi -o name | grep {vm_name}')
        if vm_name in result:
            return True
        else:
            return False

    @typechecked
    @logger_time_stamp
    def get_vm(self, label: str = '', namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method gets vm according to label
        :param label:
        :param namespace:
        :return:
        """
        if label:
            namespace = f'-n {namespace}' if namespace else ''
            return self.run(
                cmd=f"{self.__cli} get vmi {namespace} --no-headers | awk '{{ print $1; }}' | grep -w '{label}'", is_check=True).rstrip().decode('ascii')
        else:
            return self.run(f'{self.__cli} get vmi', is_check=True)

    @logger_time_stamp
    def __verify_vm_log_complete(self, vm_name: str, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method verifies that vm log is complete
        :param vm_name: vm name with uuid
        :return:
        """
        output_filename = f"{self._run_artifacts}/{vm_name}"
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            with open(output_filename) as file:
                if '-----END SSH HOST KEY KEYS-----' in file.read():
                    return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMNotCompletedTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def get_exposed_vm_port(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        The method gets exposed vm port
        @param vm_name:
        @return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        return self.run(cmd=f"{self.__cli} get service {vm_name} {namespace} -o jsonpath={{.spec.ports[].nodePort}}")

    @logger_time_stamp
    def get_nodes_addresses(self):
        """
        This method returns dictionary of nodes and corresponding IP addresses, e.g. {node1:ip1, node2:ip2, node3:ip3 }
        :return:
        """
        node_ips = self.run(f"{self.__cli} get node -ojsonpath='{{$.items[*].status.addresses[*].address}}'")
        node_ips_list = node_ips.split()
        return dict([(k, v) for k, v in zip(node_ips_list[1::2], node_ips_list[::2])])

    @logger_time_stamp
    def wait_for_vm_status(self, vm_name: str = '', status: VMStatus = VMStatus.Stopped,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = SHORT_TIMEOUT):
        """
        This method waits for VM to reach the specified status
        :param vm_name:
        :param status: Stopped, Starting, Running
        :param namespace:
        :param timeout:
        :return:
        """
        current_wait_time = 0
        namespace = f'-n {namespace}' if namespace else ''
        while timeout <= 0 or current_wait_time <= timeout:
            check_vm_status = f"{self.__cli} get vm {vm_name} {namespace} -o jsonpath={{.status.printableStatus}}"
            result = self.run(check_vm_status)
            if result == status.name:
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMStateTimeout(vm_name=vm_name, state=status)

    def wait_for_vm_login(self, vm_name: str = '', node_ip: str = '', vm_node_port: str = '',
                          timeout: int = SHORT_TIMEOUT):
        """
        This method waits for VM to be accessible via ssh login
        :param vm_name:
        :param node_ip:
        :param vm_node_port:
        :param timeout:
        :return:
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            check_vm_login = f"""if [ "$(ssh -o 'BatchMode=yes' -o ConnectTimeout=1 root@{node_ip} -p {vm_node_port} 2>&1|egrep 'denied|verification failed')" ]; then echo 'True'; else echo 'False'; fi"""
            result = self.run(check_vm_login)
            if result == 'True':
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMStateTimeout(vm_name=vm_name, state='login')

    @logger_time_stamp
    def get_vm_node(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method gets vm node
        :param vm_name:
        :param namespace:
        :return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        return self.run(f"{self.__cli} get vmi {vm_name} {namespace} -o jsonpath={{.metadata.labels.'kubevirt\.io/nodeName'}}")

    @typechecked
    @logger_time_stamp
    def wait_for_vm_create(self, vm_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits till vm name is creating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            if self.vm_exists(vm_name=vm_name, namespace=namespace):
                self.describe_vmi(vm_name=vm_name, namespace=namespace)
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        self.describe_vmi(vm_name=vm_name, namespace=namespace)
        raise VMNotCreateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def create_vm_sync(self, yaml: str, vm_name: str,
                       namespace: str = environment_variables.environment_variables_dict['namespace'],
                       timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method creates vm synchronously
        :param timeout:
        :param vm_name:
        :param yaml:
        :return:
        """
        self.create_async(yaml)
        return self.wait_for_vm_create(vm_name=vm_name, namespace=namespace, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def delete_vm_sync(self, yaml: str, vm_name: str,
                       namespace: str = environment_variables.environment_variables_dict['namespace'],
                       timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method deletes specified VM synchronously; return False if it does not exist
        :param namespace:
        :param timeout:
        :param vm_name:
        :param yaml:
        :return: return False if vm does not exist
        """
        if self.vm_exists(vm_name=vm_name, namespace=namespace):
            self.delete_async(yaml)
            return self.wait_for_vm_delete(vm_name=vm_name, namespace=namespace, timeout=timeout)
        else:
            return False

    @logger_time_stamp
    def delete_all_vms(self, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method deletes all vms
        :return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        self.run(f"{self.__cli} delete vm --all --grace-period 0 {namespace}")

    @logger_time_stamp
    def wait_for_vm_completed(self, workload: str = '', vm_name: str = '',
                              namespace: str = environment_variables.environment_variables_dict['namespace'],
                              timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits for the VM to complete
        :param vm_name: The vm name
        :param workload:
        :param namespace:
        :return: True or raise error VMNotCompletedTimeout
        """
        current_wait_time = 0
        namespace = f'-n {namespace}' if namespace else ''
        while timeout <= 0 or current_wait_time <= timeout:
            if self.run(
                    f"{self.__cli} {namespace} get benchmark {workload} -o jsonpath={{.status.complete}}") == 'true':
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMNotCompletedTimeout(workload=workload)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_delete(self, vm_name: str,
                           namespace: str = environment_variables.environment_variables_dict['namespace'],
                           timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits till VM delete; raise VMTerminateTimeout if it does not delete within the specified timeout
        :param vm_name:
        :param namespace:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            if not self.vm_exists(vm_name=vm_name, namespace=namespace):
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMDeleteTimeout(vm_name)

    @logger_time_stamp
    def wait_for_vm_log_completed(self, vm_name: str = '', end_stamp: str = '', output_filename: str = '',
                                  timeout: int = int(environment_variables.environment_variables_dict['timeout']),
                                  sleep_time: int = 30):
        """
        This method wait to vm to be completed by end sign string
        :param vm_name:
        :param end_stamp: end of run stamp
        :param output_filename:
        :param timeout:
        :param sleep_time:
        :return: True or through timeout
        """
        if not output_filename:
            output_filename = os.path.join(self._run_artifacts, vm_name)
        current_wait_time = 0
        # wait initialize time till vm log create
        time.sleep(sleep_time)
        while timeout <= 0 or current_wait_time <= timeout:
            with open(output_filename, 'r') as file:
                data = file.read()
                if end_stamp in data:
                    return True
                else:
                    # sleep for x seconds
                    time.sleep(sleep_time)
                    current_wait_time += sleep_time
        raise VMNotCompletedTimeout(workload=vm_name)

    @logger_time_stamp
    def extract_vm_results(self, vm_name: str = '', start_stamp: str = '', end_stamp: str = '', output_filename: str = ''):
        """
        This method extracts vm results from vm output log
        :param vm_name:
        :param start_stamp: start of run stamp
        :param end_stamp: end of run stamp
        :param output_filename:
        :return:
        """
        data_index = 1
        title_index = 2
        if not output_filename:
            output_filename = os.path.join(self._run_artifacts, vm_name)
        results_list = []
        with open(output_filename) as infile:
            # VM logs results start
            start = False
            for line in infile:
                if start_stamp in line or 'podman' in line and not start:
                    start = True
                    continue
                elif end_stamp in line:
                    return results_list
                elif start:
                    # Filter 'cloud-init' and CSV lines only
                    if 'cloud-init' in line and ',' in line:
                        if vm_name in line:
                            # filter the title, placed after the second :
                            results_list.append(line.strip().split(':')[title_index:])
                        else:
                            # filter the data, placed after the first :
                            results_list.append(line.strip().split(':')[data_index:])
        return results_list
