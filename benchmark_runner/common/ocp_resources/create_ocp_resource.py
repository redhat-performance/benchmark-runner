
import os
from jinja2 import Template

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.ocp_resources.create_local_storage import CreateLocalStorage
from benchmark_runner.common.ocp_resources.create_odf import CreateODF
from benchmark_runner.common.ocp_resources.create_kata import CreateKata
from benchmark_runner.common.ocp_resources.create_cnv import CreateCNV
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
            tm = Template(template_str)
            data = tm.render(self.__environment_variables_dict)
            resource_file = resource_file.replace('_template', '')
            with open(os.path.join(self.__dir_path, resource, resource_file), 'w') as f:
                f.write(data)
        resource_file_list = self.__get_yaml_files(path=os.path.join(self.__dir_path, resource))
        resource_file_list = sorted(resource_file_list, key=lambda x: os.path.splitext(x)[0])
        return resource_file_list

    def create_resource(self, resource: str, ibm_blk_disk_name: list = []):
        """
        This method create resource with verification
        :param ibm_blk_disk_name: ibm blk name list
        :param resource:
        :return:
        """
        # remove resource files
        self.remove_resource_files(path=os.path.join(self.__dir_path, resource))
        resource_files = self.get_sorted_resources(resource=resource)
        if 'local_storage' == resource:
            self.__create_local_storage = CreateLocalStorage(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            self.__create_local_storage.create_local_storage()
        elif 'odf' == resource:
            self.__create_odf = CreateODF(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files, ibm_blk_disk_name=ibm_blk_disk_name)
            self.__create_odf.create_odf()
        elif 'kata' == resource:
            self.__create_kata = CreateKata(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            self.__create_kata.create_kata()
        elif 'cnv' == resource:
            self.__create_cnv = CreateCNV(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            self.__create_cnv.create_cnv()
        elif 'infra' == resource:
            self.__create_infra = MigrateInfra(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            self.__create_infra.migrate_infra()
        elif 'custom' == resource:
            self.__create_custom = CreateCustom(self.__oc, path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
            self.__create_custom.create_custom()
            # remove resource files
        self.remove_resource_files(path=os.path.join(self.__dir_path, resource))

