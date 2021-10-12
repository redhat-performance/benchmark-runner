
import os
from jinja2 import Template
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp


class CreateOcpResource:
    """
    This class create ocp resources
    """
    def __init__(self):
        self.__dir_path = f'{os.path.dirname(os.path.realpath(__file__))}'
        self.__environment_variable_dict = environment_variables.environment_variables_dict

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
            data = tm.render(self.__environment_variable_dict)
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
        oc = OC(kubeadmin_password=self.__environment_variable_dict.get('kubeadmin_password', ''))
        if 'cnv' == resource:
            oc.create_cnv(path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
        elif 'local_storage' == resource:
            oc.create_local_storage(path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
        elif 'ocs' == resource:
            oc.create_ocs(path=os.path.join(self.__dir_path, resource), resource_list=resource_files, ibm_blk_disk_name=ibm_blk_disk_name)
        elif 'kata' == resource:
            oc.create_kata(path=os.path.join(self.__dir_path, resource), resource_list=resource_files)
        # remove resource files
        self.remove_resource_files(path=os.path.join(self.__dir_path, resource))

