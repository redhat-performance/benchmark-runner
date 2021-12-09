
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
        self.__dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
        self.__current_run_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'current_run')
        if self.__run_type == 'test_ci':
            self.__environment_variables_dict['es_suffix'] = '-test-ci'
        else:
            self.__environment_variables_dict['es_suffix'] = ''
        # hammerdb storage
        if self.__environment_variables_dict.get('ocs_pvc', '') == 'True':
            self.__storage_type = 'ocs_pvc'
        else:
            self.__storage_type = 'ephemeral'

    def __get_workload_name(self, workload: str):
        return workload.split('_')[0]

    def __get_workload_kind(self, workload: str):
        return workload.split('_')[1]

    def __get_workload_extra(self, workload: str):
        return '_'.join(workload.split('_')[2:])

    def __get_workload_template_kind(self, workload: str):
        """
        Kata shares templates with pod
        """
        kind = self.__get_workload_kind(workload)
        if kind == 'kata' or kind == 'pod':
            return 'pod'
        elif kind == 'vm':
            return 'vm'
        else:
            return None

    def __get_yaml_template_by_workload(self, workload: str, extension='.yaml', skip: str = 'data'):
        """
        This method return yaml names in benchmark_operator folder
        :return:
        """
        # Kata reuses the pod templates
        kind = self.__get_workload_template_kind(workload)
        base_workload = self.__get_workload_name(workload)
        full_workload = f'{base_workload}_{kind}'
        if not full_workload:
            return None

        for filename in os.listdir(os.path.join(self.__dir_path, base_workload, 'internal_data')):
            if filename.endswith(extension):
                if filename.startswith(full_workload) and skip not in filename:
                    return os.path.splitext(filename)[0]

    def __get_subdict(self, dictionary: dict, key: str, value: str):
        if key in dictionary:
            subdict = dictionary[key]
            if value in subdict:
                return subdict[value]
            elif 'default' in subdict:
                return subdict['default']
        return dict()

    @logger_time_stamp
    def generate_yamls_internal(self, workload: str):
        """
        Generate required .yaml files as a dictionary of file names and contents
        :return: Dictionary <filename:contents>
        """
        workload_template = self.__get_yaml_template_by_workload(workload=workload)
        workload_name = self.__get_workload_name(workload)
        workload_dir_path = os.path.join(self.__dir_path, workload_name)
        self.__environment_variables_dict['workload_name'] = workload_name
        common_data = yaml.load(render_yaml_file(self.__dir_path, 'common.yaml', self.__environment_variables_dict), Loader=yaml.FullLoader)['common_data']
        common_data = {**self.__environment_variables_dict, **common_data}
        workload_data = yaml.load(render_yaml_file(workload_dir_path, f'{workload_name}_data_template.yaml', common_data), Loader=yaml.FullLoader)
        render_data = workload_data['shared_data']

        kind = self.__get_workload_kind(workload)
        render_data['kind'] = kind
        render_data['workload_name'] = workload_name
        kind_data = self.__get_subdict(workload_data, 'kind_data', kind)
        run_type_data = self.__get_subdict(workload_data, 'run_type_data', self.__run_type)
        kind_runtype_data = self.__get_subdict(kind_data, 'run_type_data', self.__run_type)

        render_data = {**common_data, **render_data,
                       **kind_data, **run_type_data, **kind_runtype_data}
        workload_file_suffix=''

        answer = {}
        if workload_name == 'hammerdb':
            database = self.__get_workload_extra(workload)
            database_data = self.__get_subdict(workload_data, 'database_data', database)

            database_kind_data = self.__get_subdict(database_data, 'kind_data', kind)
            database_runtype_data = self.__get_subdict(database_data, 'run_type_data', self.__run_type)
            render_data = {**render_data, **database_data, **database_kind_data, **database_runtype_data}
            workload_file_suffix=f'_{database}'

            # Jinja render database pod yaml
            if kind == 'pod' or kind == 'kata':
                # Override any more generic data
                database_name = f'{database}_template.yaml'
                with open(os.path.join(workload_dir_path, 'internal_data', database_name)) as f:
                    database_template = Template(f.read())
                answer[f'{database}.yaml'] = database_template.render(render_data)

        # Jinja render workload yaml
        with open(os.path.join(workload_dir_path, 'internal_data', f'{workload_template}.yaml')) as f:
            tm = Template(f.read())
        workload_file_name = workload_template.replace('_template', '')
        answer[f'{workload_file_name}{workload_file_suffix}.yaml'] = tm.render(render_data)

        return answer

    @logger_time_stamp
    def generate_files(self, data_files: dict):
        for filename, data in data_files.items():
            with open(os.path.join(self.__current_run_path, filename), 'w') as f:
                f.write(data)

    @logger_time_stamp
    def generate_yamls(self, workload: str):
        """
        This method generate workload yaml from template
        :return:
        """

        self.generate_files(self.generate_yamls_internal(workload=workload))

    # The following routines are for testing purposes,
    # in particular to allow a known environment to be set up for golden file testing
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
