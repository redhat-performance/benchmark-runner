import os
import re
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
            logger.info(f'Wait until LVMS upgrade to version: {upgrade_version}')
            self.__wait_for_lvms_csv(upgrade_version=upgrade_version)
            return True

        if not self.__lvms_version:
            raise ValueError('LVMS_VERSION must be set to install LVMS')
        if not self.__lvms_device_paths:
            raise ValueError('LVMS_DEVICE_PATHS must be set to install LVMS')
        for device in self.__lvms_device_paths:
            # The paths are passed unquoted to pvremove/wipefs as root inside the node's chroot:
            # anything but a plain /dev path could change or extend those commands
            if not re.fullmatch(r'/dev/[A-Za-z0-9._:/-]+', device):
                raise ValueError(f'Invalid LVMS device path: {device}')

        self.__delete_lvmcluster()

        for resource in self.__resource_list:
            resource_path = os.path.join(self.__path, resource)
            logger.info(f'run {resource}')
            if resource == '00_clean_devices.sh':
                self.__clean_devices(clean_devices_script=resource_path)
                continue

            if resource == '05_lvmcluster.yaml':
                # The previous LVMCluster may still be terminating: removing the degraded volume group in
                # the device cleanup unblocks its finalizer, so wait for it to be gone before recreating it
                self.__wait_for_lvmcluster_delete(must_be_deleted=True)

            # apply is idempotent: the openshift-storage namespace and its OperatorGroup are shared with ODF
            self.__oc.apply_async(yaml=resource_path)

            if resource == '03_catalogsource.yaml':
                # wait for the catalog source to be ready before subscribing
                self.wait_for_ocp_resource_create(operator='lvms',
                                                  verify_cmd=f"oc get catalogsource redhat-operators-v{self.__lvms_version.replace('.', '')} -n openshift-marketplace -o jsonpath='{{.status.connectionState.lastObservedState}}'",
                                                  status='READY')
            elif resource == '04_subscription.yaml':
                self.__wait_for_lvms_csv()
            elif resource == '05_lvmcluster.yaml':
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
        # --wait=false is mandatory: a plain 'oc delete' blocks until the finalizers release, and the
        # finalizer is released by vg-manager, the very component that a degraded volume group breaks.
        # An unbounded block there would deadlock, because the device cleanup that clears the volume
        # group only runs after this call returns. The wait below is bounded for the same reason.
        self.__oc.run(f'oc delete lvmcluster {self.__lvms_cluster_name} -n {self.NAMESPACE} --ignore-not-found --wait=false')
        # oc delete returns before the LVMS finalizer releases the volume groups
        self.__wait_for_lvmcluster_delete(timeout=self.LVMCLUSTER_GRACEFUL_DELETE_TIMEOUT)
        time.sleep(self.SLEEP_TIME)

    def __wait_for_lvmcluster_delete(self, timeout: int = None, must_be_deleted: bool = False):
        """
        This method waits until the LVMCluster is fully deleted, its finalizer releases the volume groups
        :param timeout: wait timeout in seconds, defaults to LVMCLUSTER_DELETE_TIMEOUT
        :param must_be_deleted: raise when the LVMCluster still exists after the wait
        :return:
        """
        timeout = timeout or self.LVMCLUSTER_DELETE_TIMEOUT
        self.__oc.run(f'oc wait lvmcluster/{self.__lvms_cluster_name} -n {self.NAMESPACE} --for=delete --timeout={timeout}s 2>/dev/null || true')
        if must_be_deleted:
            # Fail here rather than applying the LVMCluster to a terminating object and timing out on its Ready wait
            remaining = self.__oc.run(f'oc get lvmcluster {self.__lvms_cluster_name} -n {self.NAMESPACE} --ignore-not-found -o name 2>/dev/null || true').strip()
            if remaining:
                raise RuntimeError(f'LVMCluster {self.__lvms_cluster_name} was not deleted within {timeout} seconds')

    def __clean_devices(self, clean_devices_script: str):
        """
        This method removes the LVMS volume groups and LVM signatures from every worker node
        :param clean_devices_script: path to the clean devices script
        :return:
        """
        # Any existing @lvms tagged VG must be removed first: it may hold devices that are no longer
        # part of LVMS_DEVICE_PATHS, and vg-manager adopts it instead of creating a new one, then fails
        # to shrink it (vgreduce: Physical volume still in use) leaving the LVMCluster Degraded.
        # vgs output is piped through xargs -r: an empty list must not expand to a bare 'vgchange -an',
        # which would deactivate every volume group on the node, including unrelated ones.
        lvms_vgs = 'vgs --noheadings -o vg_name --select vg_tags=lvms 2>/dev/null'
        cleanup_steps = [('deactivate volume groups', f'{lvms_vgs} | xargs -r vgchange -an'),
                         ('remove volume groups', f'{lvms_vgs} | xargs -r vgremove -ff')]
        for device in self.__lvms_device_paths:
            # Wiping the wrong block device cannot be undone, so each device is first checked to be a
            # real block device, unmounted and not a member of a volume group left behind by anything
            # other than LVMS; a failed check stops the cleanup before anything is written
            cleanup_steps.extend([
                (f'check {device}',
                 f'if test -b {device}; then :; else echo \'{device} is not a block device\' >&2; exit 1; fi; '
                 f'if findmnt -rn -S {device} >/dev/null 2>&1; then echo \'{device} is mounted\' >&2; exit 1; fi; '
                 f'if pvs --noheadings -o vg_name --select pv_name={device} 2>/dev/null | grep -q .; then '
                 f'echo \'{device} belongs to a volume group\' >&2; exit 1; fi'),
                (f'remove the PV label from {device}',
                 f'if pvs --noheadings -o pv_name --select pv_name={device} 2>/dev/null | grep -q .; then pvremove -ff {device}; fi'),
                (f'wipe the signatures from {device}', f'wipefs -a {device}'),
            ])
        worker_nodes = self.__oc.get_worker_nodes().split()
        if not worker_nodes:
            logger.warning('No worker nodes found, skipping LVMS device cleanup')
            return
        self.__oc.run(cmd=f'chmod +x "{clean_devices_script}"', is_check=True)
        for node in worker_nodes:
            for label, cleanup_command in cleanup_steps:
                logger.info(f'{node}: {label}: {cleanup_command}')
                # is_check: every step is checked on its own, so a failure names the step and stops
                # the run before the LVMCluster is created
                self.__oc.run(cmd=f'"{clean_devices_script}" "{node}" "{cleanup_command}"', is_check=True)

    def __wait_for_lvms_csv(self, upgrade_version: str = None):
        """
        This method waits for the LVMS CSV, targeting it by name because openshift-storage also holds ODF CSVs
        :param upgrade_version: in upgrade mode, wait for this major.minor version
        :return:
        """
        # Require Succeeded phase in both modes: during an upgrade the new CSV already carries the target
        # version while still Pending/Installing, so a version-only match would return too early.
        jq_filter = f'.items[] | select(.metadata.name | startswith("{self.OPERATOR_NAME}")) | select(.status.phase == "Succeeded")'
        if upgrade_version:
            self.wait_for_ocp_resource_create(operator='lvms',
                                              verify_cmd=f"oc get csv -n {self.NAMESPACE} -o json | jq -r '{jq_filter} | .spec.version' | awk -F. '{{print $1\".\"$2}}'",
                                              status=upgrade_version)
        else:
            self.wait_for_ocp_resource_create(operator='lvms',
                                              verify_cmd=f"oc get csv -n {self.NAMESPACE} -o json | jq -r '{jq_filter} | .status.phase'",
                                              status='Succeeded')
