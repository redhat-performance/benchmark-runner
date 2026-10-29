import os
import time

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateLVMS(CreateOCPResourceOperations):
    """
    This class creates the Logical Volume Manager Storage (LVMS) operator and LVMCluster
    """
    NAMESPACE = 'openshift-storage'
    OPERATOR_NAME = 'lvms-operator'
    LVMCLUSTER_DELETE_TIMEOUT = 300
    # Graceful delete window before the device cleanup force-removes the volume groups
    LVMCLUSTER_GRACEFUL_DELETE_TIMEOUT = 60

    def __init__(self, oc: OC, path: str, resource_list: list, lvms_version: str, lvms_device_paths: list, lvms_cluster_name: str):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list
        self.__lvms_version = lvms_version
        self.__lvms_device_paths = lvms_device_paths
        self.__lvms_cluster_name = lvms_cluster_name

    @logger_time_stamp
    def create_lvms(self, upgrade_version: str):
        """
        This method creates LVMS operator
        :param upgrade_version: target LVMS version in upgrade mode, empty on fresh install
        :return:
        """
        if upgrade_version:
            # Subscription is rendered with source redhat-operators when UPGRADE_OCP_VERSION is set
            self.__oc.apply_async(yaml=os.path.join(self.__path, '04_subscription.yaml'))
            logger.info(f'Wait till LVMS upgrade to version: {upgrade_version}')
            self.__wait_for_lvms_csv(upgrade_version=upgrade_version)
            return True

        if not self.__lvms_version:
            raise ValueError('LVMS_VERSION must be set to install LVMS')
        if not self.__lvms_device_paths:
            raise ValueError('LVMS_DEVICE_PATHS must be set to install LVMS')

        self.__delete_lvmcluster()

        for resource in self.__resource_list:
            resource_path = os.path.join(self.__path, resource)
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                self.__clean_devices(resource_path=resource_path)
                continue

            if '05_lvmcluster.yaml' in resource:
                # The previous LVMCluster may still be terminating: removing the degraded volume group in
                # the device cleanup unblocks its finalizer, so wait for it to be gone before recreating it
                self.__wait_for_lvmcluster_delete()

            # apply is idempotent: the openshift-storage namespace and its OperatorGroup are shared with ODF
            self.__oc.apply_async(yaml=resource_path)

            if '03_catalogsource.yaml' in resource:
                # wait for the catalog source to be ready before subscribing
                self.wait_for_ocp_resource_create(operator='lvms',
                                                  verify_cmd=f"oc get catalogsource redhat-operators-v{self.__lvms_version.replace('.', '')} -n openshift-marketplace -o jsonpath='{{.status.connectionState.lastObservedState}}'",
                                                  status='READY')
            elif '04_subscription.yaml' in resource:
                self.__wait_for_lvms_csv()
            elif '05_lvmcluster.yaml' in resource:
                self.wait_for_ocp_resource_create(operator='lvms',
                                                  verify_cmd=f"oc get lvmcluster {self.__lvms_cluster_name} -n {self.NAMESPACE} -o jsonpath='{{.status.state}}'",
                                                  status='Ready')

        logger.info(f'LVMS StorageClass: {self.__oc.run("oc get sc -o name | grep lvms || true")}')
        logger.info(f'LVMS VolumeSnapshotClass: {self.__oc.run("oc get volumesnapshotclass -o name | grep lvms || true")}')
        return True

    def __delete_lvmcluster(self):
        """
        This method deletes an existing LVMCluster before cleaning the devices
        :return:
        """
        logger.info(f'Delete LVMCluster {self.__lvms_cluster_name} if exists')
        # --wait=false is mandatory: a plain 'oc delete' blocks till the finalizers release, but the
        # finalizer is released by vg-manager, which is the very component that a degraded volume group
        # breaks. Blocking there would deadlock, as the device cleanup that clears the volume group only
        # runs after this call returns.
        self.__oc.run(f'oc delete lvmcluster {self.__lvms_cluster_name} -n {self.NAMESPACE} --ignore-not-found --wait=false')
        # oc delete returns before the LVMS finalizer releases the volume groups
        self.__wait_for_lvmcluster_delete(timeout=self.LVMCLUSTER_GRACEFUL_DELETE_TIMEOUT)
        time.sleep(self.SLEEP_TIME)

    def __wait_for_lvmcluster_delete(self, timeout: int = None):
        """
        This method waits till the LVMCluster is fully deleted, its finalizer releases the volume groups
        :param timeout: wait timeout in seconds, defaults to LVMCLUSTER_DELETE_TIMEOUT
        :return:
        """
        timeout = timeout or self.LVMCLUSTER_DELETE_TIMEOUT
        self.__oc.run(f'oc wait lvmcluster/{self.__lvms_cluster_name} -n {self.NAMESPACE} --for=delete --timeout={timeout}s 2>/dev/null || true')

    def __clean_devices(self, resource_path: str):
        """
        This method removes the LVMS volume groups and LVM signatures from every worker node
        :param resource_path: path to the clean devices script
        :return:
        """
        # Any existing @lvms tagged VG must be removed first: it may hold devices that are no longer
        # part of LVMS_DEVICE_PATHS, and vg-manager adopts it instead of creating a new one, then fails
        # to shrink it (vgreduce: Physical volume still in use) leaving the LVMCluster Degraded.
        # The leading backslash keeps the command substitution from running in the local shell.
        lvms_vgs = '\\$(vgs --noheadings -o vg_name --select vg_tags=lvms 2>/dev/null)'
        cleanup_commands = [f'vgchange -an {lvms_vgs} || true', f'vgremove -ff {lvms_vgs} || true']
        cleanup_commands.extend(f'pvremove -ff {device} || true; wipefs -a {device} || true' for device in self.__lvms_device_paths)
        cleanup_command = '; '.join(cleanup_commands)
        worker_nodes = self.__oc.get_worker_nodes().split()
        if not worker_nodes:
            logger.warning('No worker nodes found, skipping LVMS device cleanup')
            return
        for node in worker_nodes:
            logger.info(f'{node}: {cleanup_command}')
            self.__oc.run(cmd=f'chmod +x {resource_path}; {resource_path} "{node}" "{cleanup_command}"')

    def __wait_for_lvms_csv(self, upgrade_version: str = None):
        """
        This method waits for the LVMS CSV, targeting it by name because openshift-storage also holds ODF CSVs
        :param upgrade_version: in upgrade mode, wait for this major.minor version
        :return:
        """
        jq_filter = f'.items[] | select(.metadata.name | startswith("{self.OPERATOR_NAME}"))'
        if upgrade_version:
            self.wait_for_ocp_resource_create(operator='lvms',
                                              verify_cmd=f"oc get csv -n {self.NAMESPACE} -o json | jq -r '{jq_filter} | .spec.version' | awk -F. '{{print $1\".\"$2}}'",
                                              status=upgrade_version)
        else:
            self.wait_for_ocp_resource_create(operator='lvms',
                                              verify_cmd=f"oc get csv -n {self.NAMESPACE} -o json | jq -r '{jq_filter} | .status.phase'",
                                              status='Succeeded')
