
import os
import ast
import shutil
import time
from enum import Enum
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc_exceptions import (PodNotCreateTimeout, PodNotInitializedTimeout, PodNotReadyTimeout, \
    PodNotCompletedTimeout, PodTerminateTimeout, PodNameNotExist, LoginFailed, VMNotCreateTimeout, VMDeleteTimeout, \
    YAMLNotExist, VMNameNotExist, VMNotInitializedTimeout, VMNotReadyTimeout, VMStateTimeout, VMNotCompletedTimeout, \
    ExecFailed, PodFailed, DVStatusTimeout, CSVNotCreateTimeout, UpgradeNotStartTimeout, OperatorInstallationTimeout, \
    OperatorUpgradeTimeout, ODFHealthCheckTimeout, NodeNotReady)
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

    def get_previous_ocp_version(self):
        """
        This method returns the previous OpenShift server version from the history.
        :return: Previous OpenShift server version as a string
        """
        # Run the `oc` command to get the ClusterVersion history and extract the previous version
        return self.run(f"{self.__cli} get clusterversion version -o jsonpath='{{.status.history[1].version}}'")

    def upgrade_ocp(self, upgrade_ocp_version: str):
        """
        This method upgrades OCP version with conditional handling for specific versions.

        @param upgrade_ocp_version: Version to upgrade to
        @return:
        """
        ocp_channel = '.'.join(upgrade_ocp_version.split('.')[:2])

        # see: https://access.redhat.com/articles/7031404
        if ocp_channel == "4.16":
            patch_command = f"{self.__cli} -n openshift-config patch cm admin-acks --patch '{{\"data\":{{\"ack-4.15-kube-1.29-api-removals-in-4.16\":\"true\"}}}}' --type=merge"
            self.run(patch_command)

        upgrade_command = f"{self.__cli} adm upgrade ; sleep 10; {self.__cli} adm upgrade channel stable-{ocp_channel}; sleep 10; {self.__cli} adm upgrade --to={upgrade_ocp_version};"
        self.run(upgrade_command)

    def upgrade_in_progress(self):
        """
        This method returns True when an upgrade is in progress and False when it is not.
        @return: bool
        """
        status = self.run(f"{self.__cli} get clusterversion version -o jsonpath='{{.status.conditions[?(@.type==\"Progressing\")].status}}'")
        return status == 'True'

    @logger_time_stamp
    def wait_for_ocp_upgrade_start(self, upgrade_version: str, timeout: int = SHORT_TIMEOUT):
        """
        This method waits for ocp upgrade to start
        :param upgrade_version:
        :param timeout:
        :return:
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout and not self.upgrade_in_progress():
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        if self.upgrade_in_progress():
            return True
        else:
            raise UpgradeNotStartTimeout(version=upgrade_version)

    def get_upgrade_version(self):
        """
        This method returns upgrade version
        @return:
        """
        return self.run(f"{self.__cli} get clusterversion version -o jsonpath='{{.status.desired.version}}'")

    def get_cluster_status(self):
        """
        This method returns the STATUS from the 'oc get clusterversion' command.
        @return: str - The current status of the cluster version.
        """
        return self.run(f"{self.__cli} get clusterversion version -o jsonpath='{{.status.conditions[?(@.type==\"Progressing\")].message}}'")

    def get_operator_version(self, namespace):
        """
        This method returns the operator version from the specified namespace.
        @param namespace: str - The namespace to search for the operator version.
        @return: major version
        """
        version = self.run(f"{self.__cli} get csv -n {namespace} -o jsonpath='{{.items[0].spec.version}}'")
        return '.'.join(version.split('.')[:2])

    def wait_for_operator_installation(self, operator: str, version: str, namespace: str, timeout: int = SHORT_TIMEOUT):
        """
        This method waits till operator version is installed successfully
        @param operator:
        @param version:
        @param timeout:
        @param namespace:
        @return:
        """
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout and not self.get_operator_version(namespace) == version:
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        if self.get_operator_version(namespace) == version:
            logger.info(f'{operator} operator version: {version} in namespace: {namespace} has been installed successfully')
            return True
        else:
            raise OperatorInstallationTimeout(operator=operator, version=version, namespace=namespace)

    def healthcheck(self, action: str):
        """
        This method stops/resumes ocp health check according to action
        @param action:
        @return:
        """
        if action == 'stop':
            self.run(f"{self.__cli} -n openshift-machine-api annotate mhc $({self.__cli} get machinehealthcheck -n openshift-machine-api -o jsonpath='{{.items[0].metadata.name}}') cluster.x-k8s.io/paused=\"\"")
        elif action == 'resume':
            self.run(f"{self.__cli} -n openshift-machine-api annotate mhc $({self.__cli} get machinehealthcheck -n openshift-machine-api -o jsonpath='{{.items[0].metadata.name}}') cluster.x-k8s.io/paused-")

    def get_cnv_version(self):
        """
        This method returns cnv version
        :return:
        """
        return self.run(f"{self.__cli} get csv -n openshift-cnv -o json | jq -r '.items[] | select(.metadata.name | startswith(\"kubevirt-hyperconverged-operator\")) | .spec.version'")

    def get_odf_version(self):
        """
        This method returns odf version
        :return:
        """
        return self.run(f"{self.__cli} get csv -n openshift-storage -o jsonpath='{{.items[0].spec.labels.full_version}}'")

    def remove_lso_path(self):
        """
        The method removes lso path on each node
        @return:
        """
        self.run(fr"""{self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\\n'}}{{end}}" |  xargs -I{{}} {self.__cli} debug node/{{}} -- chroot /host sh -c "rm -rfv /mnt/local-storage/local-sc/" """)

    def get_worker_disk_ids(self, node: str = None):
        """
        This method returns all worker disk ids or disk ids by node
        :param node:
        :return:
        """
        workers_disk_ids = []

        if node and node in self.__worker_disk_ids:
            workers_disk_ids.extend(self.__worker_disk_ids[node])
        else:
            for node, disk_ids in self.__worker_disk_ids.items():
                workers_disk_ids.extend(disk_ids)

        return workers_disk_ids

    def get_pv_disk_ids(self):
        """
        This method returns list of pv disk ids
        """
        pv_ids = self.run(
            f"{self.__cli} get pv -o jsonpath='{{range .items[*]}}{{.metadata.annotations.storage\\.openshift\\.com/device-id}}{{\"\\n\"}}{{end}}'")
        return [pv[len(self.__worker_disk_prefix):] for pv in pv_ids.split()]

    def get_free_disk_id(self, node: str = None):
        """
        This method returns free disk per node  [workers disk ids - workers pv disk ids]
        """
        workers_disk_ids = self.get_worker_disk_ids(node)
        workers_pv_disk_ids = self.get_pv_disk_ids()
        free_disk_id = f'{self.__worker_disk_prefix}{[disk_id for disk_id in workers_disk_ids if disk_id not in workers_pv_disk_ids][0]}'
        if free_disk_id:
            return free_disk_id
        else:
            raise ValueError('Missing free disk id')

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
        return self.run(f"{self.__cli} get csv -n openshift-sandboxed-containers-operator $({self.__cli} get csv -n openshift-sandboxed-containers-operator --no-headers | awk '{{ print $1; }}') -o jsonpath='{{.spec.version}}'")

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
        return self.run(f"{self.__cli} get packagemanifest -n openshift-marketplace sandboxed-containers-operator -o jsonpath='{{.status.defaultChannel}}'")

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
        return self.run(f"{self.__cli} get packagemanifest -n openshift-marketplace sandboxed-containers-operator -o jsonpath='{{.status.catalogSource}}'")

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
        self.run(fr"""{self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\\n'}}{{end}}" |  xargs -I{{}} {self.__cli} debug node/{{}} -- chroot /host sh -c "mkdir -p /etc/kata-containers; cp /usr/share/kata-containers/defaults/configuration.toml /etc/kata-containers/; sed -i 's/thread-pool-size=1/thread-pool-size={thread_pool_size}/' /etc/kata-containers/configuration.toml" """)

    def delete_kata_threads_pool(self):
        """
        This method deletes kata thread-pool-size from every worker node
        @return:
        """
        self.run(fr"""{self.__cli} get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{{range .items[*]}}{{.metadata.name}}{{'\\n'}}{{end}}" |  xargs -I{{}} {self.__cli} debug node/{{}} -- chroot /host sh -c "rm -f /etc/kata-containers/configuration.toml" """)

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
        verify_cmd = f"{self.__cli} get csv -n openshift-cnv -o jsonpath='{{.items[0].status.phase}}'"
        if 'Succeeded' in self.run(verify_cmd):
            return True
        return False

    def is_odf_installed(self):
        """
        This method checks if odf operator is installed
        :return:
        """
        verify_cmd = f"{self.__cli} get csv -n openshift-storage -o jsonpath='{{.items[0].status.phase}}'"
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
        verify_cmd = f"{self.__cli} get dv {namespace} -o jsonpath='{{.items[].status.phase}}'"
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

    @typechecked
    @logger_time_stamp
    def wait_for_patch(self, pod_name: str, label: str, label_uuid: bool, namespace: str):
        """
        This method waits for patch, needs to wait that pod is created and then wait for ready
        @param pod_name:
        @param label:
        @param label_uuid:
        @param namespace:
        @return:
        """
        self.wait_for_pod_create(pod_name=pod_name, namespace=namespace)
        if self.wait_for_ready(label=label, label_uuid=label_uuid, namespace=namespace):
            return True
        else:
            raise PodNotReadyTimeout(label)

    @typechecked
    @logger_time_stamp
    def wait_for_odf_healthcheck(self, pod_name: str, namespace: str,
                                 timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits for the ODF health check by ensuring the pod is created and reaches the 'HEALTH_OK' status.

        @param pod_name: Name of the pod to check health.
        @param namespace: Namespace where the pod is located.
        @param timeout: Timeout in seconds for waiting. If set to 0 or negative, wait indefinitely.
        @return: True if health check passes within the timeout.
        @raise ODFHealthCheckTimeout: If health check fails within the timeout.
        """
        current_wait_time = 0
        health_check = f"{self.__cli} -n {namespace} rsh {self._get_pod_name(pod_name=pod_name, namespace=namespace)} ceph health"

        while timeout <= 0 or current_wait_time <= timeout:
            if 'HEALTH_OK' == self.run(health_check).strip():
                return True

            # Sleep for a defined interval and update the wait time
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME

        # Raise exception if health check fails within the timeout
        raise ODFHealthCheckTimeout(
            message=f"Health check failed for pod '{pod_name}' in namespace '{namespace}' after {timeout} seconds.")

    @typechecked
    @logger_time_stamp
    def verify_odf_installation(self, namespace: str = 'openshift-storage'):
        """
        This method verifies ODF installation
        :return: True ODF passed, False failed
        """
        # apply patch
        self.run(
            f"{self.__cli} patch storagecluster ocs-storagecluster -n {namespace} --type json --patch '[{{ \"op\": \"replace\", \"path\": \"/spec/enableCephTools\", \"value\": true }}]'")
        self.wait_for_patch(pod_name='rook-ceph-tools', label='app=rook-ceph-tools', label_uuid=False, namespace=namespace)
        return self.wait_for_odf_healthcheck(pod_name='rook-ceph-tools', namespace=namespace)

    def get_odf_disk_count(self):
        """
        This method returns the ODF disk count.
        :return: ODF disk count or -1 if the count cannot be retrieved
        """
        if self.is_odf_installed():
            try:
                # Run the command to get ODF disk count
                disk_count_str = self.run(
                    f"{self.__cli} get --no-headers pod -n openshift-storage | grep osd | grep -cv prepare")
                disk_count = int(disk_count_str)
                return disk_count
            except ValueError as e:
                # Log the error and return -1 as a fallback
                logger.error(f"Error converting ODF disk count to integer: {e}")
                return -1
            except Exception as e:
                # Handle any other unexpected errors
                logger.error(f"Unexpected error while getting ODF disk count: {e}")
                return -1
        else:
            # If ODF is not installed, return -1
            logger.info("ODF is not installed.")
            return -1

    def is_kata_installed(self):
        """
        This method checks if kata operator is installed
        :return:
        """
        verify_cmd = f"{self.__cli} get csv -n openshift-sandboxed-containers-operator -o jsonpath='{{.items[0].status.phase}}'"
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

    @typechecked
    def wait_for_node_ready(self, node: str = None, wait_time: int = None, timeout: int = int(environment_variables.environment_variables_dict['timeout'])):
        """
        This method waits until all nodes are in 'Ready' status or specific node
        @param node: wait for specific node to be ready, when None check all nodes
        @param wait_time: wait time between each loop
        @param timeout: Maximum wait time in seconds, negative value means no timeout (default set in environment variables)
        @return: True if all nodes are in 'Ready' status within the timeout period
        @raises: NodeNotReady if one or more nodes are not ready within the timeout
        """
        wait_time = wait_time or OC.SHORT_TIMEOUT
        nodes_status = None
        current_wait_time = 0
        while timeout <= 0 or current_wait_time <= timeout:
            nodes_status = self.check_node_status(node=node)
            if nodes_status is True:
                return True
            logger.info(f"Waiting for '{nodes_status}' to reach 'Ready' status")
            time.sleep(wait_time)
            current_wait_time += wait_time
        logger.info(f"oc get nodes:\n{self.run('oc get nodes')}")
        raise NodeNotReady(nodes_status=nodes_status)

    @typechecked
    def check_node_status(self, node: str = None):
        """
        This method checks the status of all nodes or a specific node.
        @param node: The name of a specific node to check for "Ready" status; if None, check all nodes.
        @return: True if all nodes are in 'Ready' status, or a dictionary of nodes that are not in 'Ready' status.
        """
        not_ready_nodes = {}

        for node_state in self.get_node_status():
            node_name, node_status = node_state.split()

            # If a specific node is given, only check that node
            if node and node != node_name:
                continue

            if node_status != 'Ready':
                not_ready_nodes[node_name] = node_status
                # If checking a specific node and it's not ready, no need to check further
                if node:
                    break

        return True if not not_ready_nodes else not_ready_nodes

    def get_node_status(self) -> list:
        """
        This method returns node status list
        @return:
        """
        # Get the node name and status for all nodes
        nodes_list = self.run(f"{self.__cli} get nodes --no-headers | awk '{{print $1, $2}}'").splitlines()
        return nodes_list

    def delete_available_released_pv(self):
        """
        This method deletes available or released pv because that avoid launching new pv
        """
        pv_status_list = self.run(fr"{self.__cli} get pv -o jsonpath={{..status.phase}}").split()
        for ind, pv_status in enumerate(pv_status_list):
            if pv_status == 'Available' or pv_status == 'Released':
                available_pv = self.run(fr"{self.__cli} get pv -o jsonpath={{.items[{ind}].metadata.name}}")
                logger.info(f'Delete {pv_status} pv {available_pv}')
                self.run(fr"{self.__cli} delete localvolume -n openshift-local-storage local-disks")
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
    def apply_async(self, yaml: str, is_check: bool = False):
        """
        This method creates yaml in async
        @param yaml:
        @param is_check:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'{self.__cli} apply -f {yaml}', is_check=is_check)
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
        result = self.run(f"{self.__cli} get {namespace} pod -l={label_name} -o jsonpath='{{.items}}'")
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
    def wait_for_upgrade_version(self, operator: str, upgrade_version: str,
                                 namespace: str = environment_variables.environment_variables_dict['namespace'],
                                 timeout: int = int(
                                     environment_variables.environment_variables_dict['timeout'])) -> bool:
        """
        This method waits until all operators' CSVs reach the expected upgrade version.

        :param operator: The operator for which the upgrade is being monitored.
        :param upgrade_version: The expected version that all CSVs should reach.
        :param namespace: The namespace in which the operator CSVs are located.
        :param timeout: The maximum time to wait for the upgrade to complete.
        :return: True if all CSVs reach the expected version, or raise OperatorUpgradeTimeout.
        """
        current_wait_time = 0

        while timeout <= 0 or current_wait_time <= timeout:
            upgrade_versions = self.run(
                f"{self.__cli} get csv -n {namespace} -o custom-columns=:.spec.version --no-headers").splitlines()
            count_upgrade_version = sum(1 for actual_upgrade_version in upgrade_versions if
                                        '.'.join(actual_upgrade_version.split('.')[0:2]) == upgrade_version)

            if len(upgrade_versions) == count_upgrade_version:
                return True

            # Sleep for a predefined time before checking again
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME

        raise OperatorUpgradeTimeout(operator=operator, version=upgrade_version, namespace=namespace)

    @typechecked
    @logger_time_stamp
    def wait_for_csv(self, operator: str, csv_num: int = 1,
                     namespace: str = environment_variables.environment_variables_dict['namespace'],
                     timeout: int = int(environment_variables.environment_variables_dict['timeout'])) -> str:
        """
        This method waits until the required number of CSVs are created or throws an exception after a timeout.

        :param operator: The operator for which the CSVs are being monitored.
        :param csv_num: The required number of CSVs, default is 1.
        :param namespace: The namespace in which the operator CSVs are located.
        :param timeout: The maximum time to wait for the CSVs to be created.
        :return: CSV names if the required number of CSVs are found, or raises CSVNotCreateTimeout.
        """
        current_wait_time = 0

        while timeout <= 0 or current_wait_time <= timeout:
            csv_names = self.run(f"{self.__cli} get csv -n {namespace} -o jsonpath={{$.items[*].metadata.name}}")
            if csv_names and len(csv_names.split()) >= csv_num:
                return csv_names

            # Sleep for a predefined time before checking again
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME

        raise CSVNotCreateTimeout(operator, namespace)

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
    def _get_all_vm_names(self, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns a list of VM names in the given namespace.

        :param namespace: str, the namespace to look for VMs in. Defaults to the namespace in environment_variables_dict.
        :return: list of VM names or an empty list if an error occurs
        """
        namespace_option = f'-n {namespace}' if namespace else ''
        command = f"{self.__cli} get {namespace_option} vm -o jsonpath='{{.items[*].metadata.name}}'"
        try:
            vm_names = self.run(command)
            return vm_names.split() if vm_names else []
        except Exception:
            return []

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
        node_ips = self.run(f"{self.__cli} get node -o jsonpath='{{$.items[*].status.addresses[*].address}}'")
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

    def wait_for_vm_ssh(self, vm_name: str = '', node_ip: str = '', vm_node_port: str = '',
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
            check_vm_ssh = f"""if [ "$(ssh -o 'BatchMode=yes' -o ConnectTimeout=1 root@{node_ip} -p {vm_node_port} 2>&1|egrep 'denied|verification failed')" ]; then echo 'True'; else echo 'False'; fi"""
            result = self.run(check_vm_ssh)
            if result == 'True':
                return True
            # sleep for x seconds
            time.sleep(OC.SLEEP_TIME)
            current_wait_time += OC.SLEEP_TIME
        raise VMStateTimeout(vm_name=vm_name, state='ssh')

    def get_vm_ssh_status(self, node_ip: str = '', vm_node_port: str = ''):
        """
        This method returns True when the VM is active and an error message when it is not, using SSH protocol
        SSh VM by node ip and exposed node port
        :param node_ip:
        :param vm_node_port:
        :return:
        """
        ssh_vm_cmd = f"ssh -o 'BatchMode=yes' -o ConnectTimeout=1 root@{node_ip} -p {vm_node_port}"
        check_ssh_vm_cmd = f"""if [ "$(ssh -o 'BatchMode=yes' -o ConnectTimeout=1 root@{node_ip} -p {vm_node_port} 2>&1|egrep 'denied|verification failed')" ]; then echo 'True'; else echo 'False'; fi"""
        if self.run(check_ssh_vm_cmd) == 'True':
            return 'True'
        else:
            return self.run(ssh_vm_cmd)

    def get_virtctl_vm_status(self, vm_name: str = '', namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method returns True when the VM is active and an error message when it is not, using virtctl protocol
        :param vm_name:
        :param namespace:
        :return: virtctl_status 'True' if successful, or an error message if it fails.
        """
        virtctl_vm_cmd = f"virtctl ssh --local-ssh=true --local-ssh-opts='-o BatchMode=yes' --local-ssh-opts='-o PasswordAuthentication=no' --local-ssh-opts='-o ConnectTimeout=2' root@{vm_name} -n {namespace}"
        check_virtctl_vm_cmd = f"virtctl ssh --local-ssh=true --local-ssh-opts='-o BatchMode=yes' --local-ssh-opts='-o PasswordAuthentication=no' --local-ssh-opts='-o ConnectTimeout=2' root@{vm_name} -n {namespace} 2>&1 |egrep 'denied|verification failed'  && echo 'True' || echo 'False'"
        if 'True' in self.run(check_virtctl_vm_cmd):
            return 'True'
        else:
            return self.run(virtctl_vm_cmd)

    @logger_time_stamp
    def get_vm_node(self, vm_name: str, namespace: str = environment_variables.environment_variables_dict['namespace']):
        """
        This method gets vm node
        :param vm_name:
        :param namespace:
        :return:
        """
        namespace = f'-n {namespace}' if namespace else ''
        command = f"{self.__cli} get vmi {vm_name} {namespace} -o jsonpath={{.metadata.labels.'kubevirt\\.io/nodeName'}}"

        try:
            result = self.run(command)
            if result and "NotFound" not in result:
                return result.strip()
            return None
        except Exception as e:
            # Log the exception details if necessary
            print(f"Error occurred: {e}")
            return None

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

    @typechecked
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

    @typechecked
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

    @typechecked
    @logger_time_stamp
    def generate_odf_must_gather(self, destination_path: str = '/tmp', odf_version: str = None):
        """
        Generates ODF must-gather logs based on the ODF version and stores it in the destination path.

        :param destination_path: The directory where the must-gather logs will be stored. Default is '/tmp'.
        :param odf_version: The version of ODF for which to generate the must-gather logs, Default is None.
        :return: The result of the run command.
        :raises: RuntimeError if the command fails.
        """
        if not odf_version:
            odf_version = ".".join(self.get_odf_version().split(".")[:2])
            if not odf_version:
                raise ValueError("ODF version must be provided")
        logger.info(f'odf version: {odf_version}')
        folder_path = os.path.join(destination_path, f"odf-must-gather-rhel9-v{odf_version}")

        try:
            command = (f"oc adm must-gather --image=registry.redhat.io/odf4/odf-must-gather-rhel9:v{odf_version} "
                       f"--dest-dir={folder_path}")
            self.run(command)
        except Exception as e:
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except Exception as remove_error:
                    raise RuntimeError(f"Failed to remove folder {folder_path}: {remove_error}")
            raise RuntimeError(f"Failed to generate ODF must-gather logs for version {odf_version}: {e}")

    @typechecked
    @logger_time_stamp
    def generate_cnv_must_gather(self, destination_path: str = '/tmp', cnv_version: str = None):
        """
        Generates CNV must-gather logs based on the CNV version and stores it in the destination path.

        :param destination_path: The directory where the must-gather logs will be stored. Default is '/tmp'.
        :param cnv_version: The version of CNV for which to generate the must-gather logs, Default is None.
        :return: The result of the run command.
        :raises: RuntimeError if the command fails.
        """
        if not cnv_version:
            cnv_version = ".".join(self.get_cnv_version().split(".")[:2])
            if not cnv_version:
                raise ValueError("CNV version must be provided")
        logger.info(f'cnv version: {cnv_version}')

        folder_path = os.path.join(destination_path, f"cnv-must-gather-rhel9-v{cnv_version}")

        try:
            command = (f"oc adm must-gather --image=registry.redhat.io/container-native-virtualization/"
                       f"cnv-must-gather-rhel9:v{cnv_version} --dest-dir={folder_path}")
            self.run(command)
        except Exception as e:
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except Exception as remove_error:
                    raise RuntimeError(f"Failed to remove folder {folder_path}: {remove_error}")
            raise RuntimeError(f"Failed to generate CNV must-gather logs for version {cnv_version}: {e}")
