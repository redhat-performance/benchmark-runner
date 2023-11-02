
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateODF(CreateOCPResourceOperations):
    """
    This class is created ODF operator
    """
    def __init__(self, oc: OC, path: str, resource_list: list, worker_disk_ids: list, worker_disk_prefix: str):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list
        self.__worker_disk_ids = worker_disk_ids
        self.__worker_disk_prefix = worker_disk_prefix

    @logger_time_stamp
    def create_odf(self):
        """
        This method create odf
        :return:
        """
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                # disk cleanup - reference: https://rook.io/docs/rook/v1.12/Getting-Started/ceph-teardown/#delete-the-data-on-hosts
                if '01_delete_disks.sh' == resource:
                    delete_node_disk = ''
                    result_dict = {}
                    for node, disk_ids in self.__worker_disk_ids.items():
                        for disk_id in disk_ids:
                            disk = f'/dev/disk/by-id/{self.__worker_disk_prefix}{disk_id}'
                            delete_node_disk += f"sgdisk --zap-all {disk}; wipefs -a {disk}; dd if=/dev/zero of='{disk}' bs=1M count=100 oflag=direct,dsync; blkdiscard {disk}; partprobe {disk}"
                        result_dict[node] = delete_node_disk
                        delete_node_disk = ''
                    self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {self.__path}/./{resource} "{list(result_dict.keys())[0]}" "{list(result_dict.values())[0]}" "{list(result_dict.keys())[1]}" "{list(result_dict.values())[1]}" "{list(result_dict.keys())[2]}" "{list(result_dict.values())[2]}"')
                else:
                    self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {self.__path}/./{resource}')
            else:  # yaml
                self.__oc.create_async(yaml=os.path.join(self.__path, resource))
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
