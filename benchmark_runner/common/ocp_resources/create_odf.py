
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import ODFInstallationFailed


class CreateODF(CreateOCPResourceOperations):
    """
    This class is created ODF operator
    """
    ODF_CSV_NUM = 4

    def __init__(self, oc: OC, path: str, resource_list: list, worker_disk_ids: list, worker_disk_prefix: str, odf_catalog_image: str = ''):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list
        self.__worker_disk_ids = worker_disk_ids
        self.__worker_disk_prefix = worker_disk_prefix
        self.__odf_catalog_image = odf_catalog_image.strip() if odf_catalog_image else ''

    @logger_time_stamp
    def create_odf(self, upgrade_version: str):
        """
        This method creates odf operator
        :param upgrade_version:
        :return:
        """
        if upgrade_version:
            self.__oc.apply_async(yaml=os.path.join(self.__path, '07_subscription.yaml'))
            logger.info(f'Wait till ODF upgrade to version: {upgrade_version}')
            self.verify_csv_installation(namespace='openshift-storage', operator='odf', upgrade_version=upgrade_version, csv_num=self.ODF_CSV_NUM)
        else:
            if self.__odf_catalog_image:
                idms_path = os.path.join(self.__path, 'idms.yaml')
                logger.info(f'Extracting idms.yaml from catalog image: {self.__odf_catalog_image}')
                self.__oc.run(cmd=f"cd {self.__path} && oc image extract '{self.__odf_catalog_image}' --file='/idms.yaml' --confirm")
                if os.path.exists(idms_path) and open(idms_path).read().strip():
                    logger.info('Applying IDMS for catalog image mirrors')
                    self.__oc.run(cmd=f'oc apply -f {idms_path}')
                    logger.info('Waiting for MCP rollout after IDMS apply')
                    self.wait_for_ocp_resource_create(operator='odf',
                                                      verify_cmd="oc get mcp master worker -o jsonpath='{range .items[*]}{.status.conditions[?(@.type==\"Updated\")].status}{\"\\n\"}{end}' | grep -cx True || true",
                                                      status=str(len(['master', 'worker'])))
                else:
                    logger.info('No idms.yaml found in catalog image, skipping IDMS apply')
            for resource in self.__resource_list:
                logger.info(f'run {resource}')
                if resource.endswith('.sh'):
                    # Ceph disk deletion - reference: https://rook.io/docs/rook/v1.12/Getting-Started/ceph-teardown/#delete-the-data-on-hosts
                    if '01_delete_disks.sh' == resource:
                        delete_node_disk = ''
                        for node, disk_ids in self.__worker_disk_ids.items():
                            for disk_id in disk_ids:
                                disk = f'/dev/disk/by-id/{self.__worker_disk_prefix}{disk_id}'
                                delete_node_disk += f"""sudo mkfs.ext4 -F {disk}; sudo sgdisk --zap-all {disk}; sudo wipefs -a {disk}; sudo dd if=/dev/zero of='{disk}' bs=20M count=100 oflag=direct,dsync;"""
                                logger.info(f'{node}: {delete_node_disk}')
                                self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {self.__path}/./{resource} "{node}" "{delete_node_disk}"')
                                delete_node_disk = ''
                    else:
                        self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {self.__path}/./{resource}')
                else:  # yaml
                    yaml_path = os.path.join(self.__path, resource)
                    # skip empty rendered templates (e.g. catalog source when odf_catalog_image is not set)
                    if not open(yaml_path).read().strip():
                        logger.info(f'Skipping empty template: {resource}')
                        continue
                    self.__oc.create_async(yaml=yaml_path)
                    if '00_catalog_source.yaml' in resource:
                        # wait for catalog source to be ready before subscribing
                        self.wait_for_ocp_resource_create(operator='odf',
                                                          verify_cmd="oc get catalogsource odf-catalog-source -n openshift-marketplace -o jsonpath='{.status.connectionState.lastObservedState}' | grep -c READY || true",
                                                          status='1')
                    if '04_local_volume_set.yaml' in resource:
                        # openshift local storage - diskmaker
                        self.wait_for_ocp_resource_create(operator='odf',
                                                          verify_cmd=r"""oc get pod -n openshift-local-storage -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep diskmaker | wc -l""",
                                                          count_disk_maker=True)
                        # openshift persistence volume - pv
                        self.wait_for_ocp_resource_create(operator='odf',
                                                          verify_cmd=r"""oc get pv -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | grep local | wc -l""",
                                                          count_openshift_storage=True)
                    if '07_subscription.yaml' in resource:
                        # Must be run after installing the storage cluster because CSVs sometimes fail
                        self.verify_csv_installation(namespace='openshift-storage', operator='odf', csv_num=self.ODF_CSV_NUM)
                    elif '08_storage_cluster.yaml' in resource:
                        self.wait_for_ocp_resource_create(operator='odf',
                                                          verify_cmd='oc get pod -n openshift-storage | grep osd | grep -v prepare | wc -l',
                                                          count_openshift_storage=True)
            # Verify ODF installation
            if not self.__oc.verify_odf_installation():
                raise ODFInstallationFailed
            return True
