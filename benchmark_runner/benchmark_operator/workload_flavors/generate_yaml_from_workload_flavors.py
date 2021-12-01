
import os
import shutil
import yaml
from jinja2 import Template
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import render_yaml_file
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.main.environment_variables import environment_variables


class TemplateOperations:
    """This class is responsible for template operations"""

    def __init__(self):
        self.initialize_environment(environment_variables.environment_variables_dict)

    def __initialize_dependent_variables__(self):
        self.__run_type = self.__environment_variables_dict.get('run_type', '')
        self.__dir_path = f'{os.path.dirname(os.path.realpath(__file__))}/{self.__run_type}'
        self.__current_run_path = f'{self.__dir_path}/current_run'
        self.__hammerdb_dir_path = os.path.join(self.__dir_path, f'hammerdb')
        self.__hammerdb__internal_dir_path = os.path.join(self.__dir_path, f'hammerdb', 'internal_data')
        # hammerdb storage
        if self.__environment_variables_dict.get('ocs_pvc', '') == 'True':
            self.__storage_type = 'ocs_pvc'
        else:
            self.__storage_type = 'ephemeral'

    def initialize_environment(self, environment: dict = environment_variables.environment_variables_dict):
        self.__environment_variables_dict = environment
        self.__initialize_dependent_variables__()

    def set_environment_variable(self, variable: str, value: str):
        self.__environment_variables_dict[variable] = value
        self.__initialize_dependent_variables__()

    def set_environment_variables(self, update_environment: dict):
        self.__environment_variables_dict = {**self.__environment_variables_dict, **update_environment}
        self.__initialize_dependent_variables__()

    def clear_environment_variable(self, variable):
        self.__environment_variables_dict.pop(variable, '')
        self.__initialize_dependent_variables__()

    def get_current_run_path(self):
        return self.__current_run_path

    @logger_time_stamp
    def __get_yaml_template_by_workload(self, workload: str, extension='.yaml', skip: str = 'data'):
        """
        This method return yaml names in benchmark_operator folder
        :return:
        """
        # Kata reuses the pod templates
        if '_kata' in workload:
            workload = f'{workload[:-len("_kata")]}_pod'

        for file in os.listdir(os.path.join(self.__dir_path, workload.split('_')[0], 'internal_data')):
            if file.endswith(extension):
                if workload and workload in file and skip not in file:
                    return os.path.splitext(file)[0]

    @logger_time_stamp
    def generate_files(self, data_files: dict):
        for filename, data in data_files.items():
            with open(os.path.join(self.__current_run_path, filename), 'w') as f:
                f.write(data)

    def __get_workload_keys(self, workload: str):
        """
        Compute kind and data key from workload name
        """
        if '_pod' in workload:
            return 'pod', 'pod'
        elif '_kata' in workload:
            return 'kata', 'pod'
        elif '_vm' in workload:
            return 'vm', 'vm'
        else:
            return None, None

    @logger_time_stamp
    def generate_hammerdb_yamls_internal(self, workload: str, database: str):
        """
        Generate required .yaml files as a dictionary of file names and contents
        :return: Dictionary <filename:contents>
        """
        # Get hammerdb data
        hammerdb_template = self.__get_yaml_template_by_workload(workload=workload)
        hammerdb_data = yaml.load(render_yaml_file(self.__hammerdb_dir_path, 'hammerdb_data_template.yaml', self.__environment_variables_dict), Loader=yaml.FullLoader)
        database_data = hammerdb_data[database]
        render_data = hammerdb_data['shared_data']

        # merge 3 dictionaries
        kind, template_kind = self.__get_workload_keys(workload)
        render_data['kind'] = kind
        render_data = {**self.__environment_variables_dict, **render_data, **database_data, **hammerdb_data[template_kind]}

        # Jinja render hammerdb yaml
        with open(os.path.join(self.__hammerdb_dir_path, 'internal_data', f'{hammerdb_template}.yaml')) as f:
            tm = Template(f.read())
        hammerdb_name = hammerdb_template.replace('template', '')
        answer = {}
        answer[f'{hammerdb_name}{database}.yaml'] = tm.render(render_data)

        # Jinja render database pod yaml
        if 'pod' in workload or 'kata' in workload:
            # replace parameter from hammerdb_data
            database_name = f'{database}_{self.__storage_type}_template.yaml'
            with open(os.path.join(self.__hammerdb__internal_dir_path, database_name)) as f:
                database_template = Template(f.read())
            answer[f'{database}.yaml'] = database_template.render(render_data)

        return answer

    @logger_time_stamp
    def generate_hammerdb_yamls(self, workload: str, database: str):
        """
        This method generate hammerdb yaml from workload_flavors,
        special generator for 2 yaml file: database and workload
        :return:
        """
        self.generate_files(self.generate_hammerdb_yamls_internal(workload=workload, database=database))

    @logger_time_stamp
    def generate_workload_yamls_internal(self, workload: str):
        """
        This method generate workload yaml from template
        :return: Dictionary <filename:contents>
        """

        workload_template = self.__get_yaml_template_by_workload(workload=workload)
        workload_name = workload.split('_')[0]
        workload_dir_path = os.path.join(self.__dir_path, workload_name)
        workload_data = yaml.load(render_yaml_file(workload_dir_path, f'{workload_name}_data_template.yaml', self.__environment_variables_dict), Loader=yaml.FullLoader)
        render_data = workload_data['shared_data']

        # merge 3 dictionaries
        kind, template_kind = self.__get_workload_keys(workload)
        render_data['kind'] = kind
        render_data = {**self.__environment_variables_dict, **render_data, **workload_data[template_kind]}

        with open(os.path.join(f'{workload_dir_path}', 'internal_data', f'{workload_template}.yaml')) as f:
            tm = Template(f.read())
        workload_file_name = workload_template.replace('_template', '')
        return {f'{workload_file_name}.yaml': tm.render(render_data)}

    @logger_time_stamp
    def generate_workload_yamls(self, workload: str):
        """
        This method generate workload yaml from template
        :return:
        """
        self.generate_files(self.generate_workload_yamls_internal(workload=workload))
