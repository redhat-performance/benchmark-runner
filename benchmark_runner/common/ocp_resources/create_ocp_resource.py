import ast
import os
from jinja2 import Template

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.ocp_resources.create_lso import CreateLSO
from benchmark_runner.common.ocp_resources.create_odf import CreateODF
from benchmark_runner.common.ocp_resources.create_kata import CreateKata
from benchmark_runner.common.ocp_resources.create_cnv import CreateCNV
from benchmark_runner.common.ocp_resources.create_nhc_snr import CreateNHCSNR
from benchmark_runner.common.ocp_resources.create_custom import CreateCustom
from benchmark_runner.common.ocp_resources.migrate_infra import MigrateInfra


class CreateOCPResource:
    """
    This class create ocp resources
    """
    def __init__(self):
        self.__dir_path = f'{os.path.dirname(os.path.realpath(__file__))}'
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__oc = OC(kubeadmin_password=self.__environment_variables_dict.get('kubeadmin_password', ''))
        self.__oc.login()
        self.__oc.populate_additional_template_variables(self.__environment_variables_dict)
        self.__worker_disk_prefix = self.__environment_variables_dict.get('worker_disk_prefix', '')
        self.__worker_disk_ids = self.__environment_variables_dict.get('worker_disk_ids', '')
        if self.__worker_disk_ids:
            if self.__worker_disk_ids:
                # Solved GitHub Actions issue that env variable detect as string instead of dict/ list -skip for Jenkins
                if self.__environment_variables_dict.get('git_token', ''):
                    self.__worker_disk_ids = self.__worker_disk_ids.replace('"', '')
                self.__worker_disk_ids = ast.literal_eval(self.__worker_disk_ids)

    @staticmethod
    def __get_yaml_files(path: str, extensions: list = ['.yaml', '.sh']):
        file_list = []
        for file in os.listdir(path):
            for extension in extensions:
                if file.endswith(extension):
                    file_list.append(file)
        return file_list

    def remove_resource_files(self, path: str, extensions: list = ['.yaml', '.sh']):
        """
        This method remove yamls files in path
        :param path: The path
        :param extensions: File type to delete
        :return:
        """
        file_list = self.__get_yaml_files(path=path, extensions=extensions)
        for file in file_list:
            os.remove(os.path.join(path, file))

    def get_sorted_resources(self, resource: str):
        """
        This method update environment variable inside yaml file
        :param resource:
        :return:
        """
        for resource_file in os.listdir(os.path.join(self.__dir_path, resource, 'template')):
            with open(os.path.join(self.__dir_path, resource, 'template', resource_file)) as f:
                template_str = f.read()
            tm = Template(template_str, keep_trailing_newline=True)
            data = tm.render(self.__environment_variables_dict)
            resource_file = resource_file.replace('_template', '')
            with open(os.path.join(self.__dir_path, resource, resource_file), 'w') as f:
                f.write(data)
        resource_file_list = self.__get_yaml_files(path=os.path.join(self.__dir_path, resource))
        resource_file_list = sorted(resource_file_list, key=lambda x: os.path.splitext(x)[0])
        return resource_file_list

    def create_resource(self, resource: str, upgrade_version: str):
        """
        This method create resource with verification
        :param resource:
        :param upgrade_version:
        :return:
        """
        # remove resource files
        self.remove_resource_files(path=os.path.join(self.__dir_path, resource))
        resource_files = self.get_sorted_resources(resource=resource)
        if 'lso' == resource:
            create_lso = CreateLSO(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            create_lso.create_lso(upgrade_version)
        elif 'odf' == resource:
            create_odf = CreateODF(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files, worker_disk_ids=self.__worker_disk_ids, worker_disk_prefix=self.__worker_disk_prefix)
            create_odf.create_odf(upgrade_version)
        elif 'kata' == resource:
            create_kata = CreateKata(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            create_kata.create_kata()
        elif 'cnv' == resource:
            create_cnv = CreateCNV(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            create_cnv.create_cnv()
        elif 'nhc_snr' == resource:
            create_nhc_snr = CreateNHCSNR(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            create_nhc_snr.create_nhc_snr()
        elif 'infra' == resource:
            create_infra = MigrateInfra(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            create_infra.migrate_infra()
        elif 'custom' == resource:
            create_custom = CreateCustom(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            create_custom.create_custom()
            # remove resource files
        self.remove_resource_files(path=os.path.join(self.__dir_path, resource))
