
import os

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.ocp_resources.create_ocp_resource_operations import CreateOCPResourceOperations


class CreateCNV(CreateOCPResourceOperations):
    """
    This class is create CNV nightly build operator
    """
    def __init__(self, oc: OC, path: str, resource_list: list):
        super().__init__(oc)
        self.__oc = oc
        self.__path = path
        self.__resource_list = resource_list

    @logger_time_stamp
    def create_cnv(self):
        """
        This method create cnv resource
        :return:
        """
        cnv_version = self._environment_variables_dict.get('cnv_version', '')
        logger.info('wait for cnv-nightly kubevirt-hyperconverged')
        # cnv_nightly_catalog_source.yaml already run direct through Github actions - just need to wait
        self.wait_for_ocp_resource_create(resource='cnv_nightly_catalog_source.yaml',
                                      verify_cmd="oc get packagemanifest -l catalog=cnv-nightly-catalog-source | grep kubevirt-hyperconverged",
                                      status="kubevirt-hyperconverged")
        starting_csv = self.__oc.run(""" oc get packagemanifest -l "catalog=cnv-nightly-catalog-source" -o jsonpath="{$.items[?(@.metadata.name=='kubevirt-hyperconverged')].status.channels[?(@.name==\\"nightly-cnv_version\\")].currentCSV}" """.replace('cnv_version', cnv_version))
        self._replace_in_file(file_path=os.path.join(self.__path, '01_operator.yaml'), old_value="@starting_csv@", new_value=starting_csv)
        for resource in self.__resource_list:
            logger.info(f'run {resource}')
            if resource.endswith('.sh'):
                self.__oc.run(cmd=f'chmod +x {os.path.join(self.__path, resource)}; {self.__path}/./{resource}')
            else:
                self.__oc._create_async(yaml=os.path.join(self.__path, resource))
                if '01_operator.yaml' in resource:
                    # wait till get the patch
                    self.wait_for_ocp_resource_create(resource=resource,
                                                      verify_cmd="oc get InstallPlan -n openshift-cnv -ojsonpath={.items[0].metadata.name}",
                                                      status="install-")
                    self.apply_patch(namespace='openshift-cnv', resource='cnv')
                # for second script wait for refresh status
                if '02_hyperconverge.yaml' in resource:
                    # Wait that till succeeded
                    self.wait_for_ocp_resource_create(resource='cnv',
                                                      verify_cmd="oc get csv -n openshift-cnv -ojsonpath='{.items[0].status.phase}'",
                                                      status='Succeeded')
        return True

