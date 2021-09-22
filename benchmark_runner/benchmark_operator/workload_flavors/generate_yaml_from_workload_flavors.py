
import os
import shutil
import yaml
from jinja2 import Template
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import delete_generate_file, update_environment_variable
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.main.environment_variables import environment_variables


class TemplateOperations:
    """This class is responsible for template operations"""

    def __init__(self):
        # environment variables
        self.__environment_variables_dict = environment_variables.environment_variables_dict
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

    def __get_yaml_template_by_workload(self, workload: str, extension='.yaml', skip: str = 'data'):
        """
        This method return yaml names in benchmark_operator folder
        :return:
        """
        for file in os.listdir(os.path.join(self.__dir_path, workload.split('_')[0], 'internal_data')):
            if file.endswith(extension):
                if workload and workload in file and skip not in file:
                    return os.path.splitext(file)[0]

    @logger_time_stamp
    def generate_hammerdb_yamls(self, workload: str, database: str):
        """
        This method generate hammerdb yaml from workload_flavors,
        special generator for 2 yaml file: database and workload
        :return:
        """
        # replace environment variables and generate hammerdb_data.yaml
        update_environment_variable(dir_path=self.__hammerdb_dir_path, yaml_file='hammerdb_data_template.yaml')
        # handle database pod yaml
        if 'pod' in workload:
            # replace environment variables
            update_environment_variable(dir_path=self.__hammerdb__internal_dir_path, yaml_file=f'{database}_{self.__storage_type}_template.yaml')
            shutil.move(os.path.join(self.__hammerdb__internal_dir_path, f'{database}_{self.__storage_type}.yaml'), os.path.join(self.__current_run_path, f'{database}.yaml'))
            delete_generate_file(full_path_yaml=os.path.join(self.__hammerdb__internal_dir_path, f'{database}.yaml'))
        # Get hammerdb data
        with open(os.path.join(self.__hammerdb_dir_path, 'hammerdb_data.yaml'), 'r') as file:
            hammerdb_data = yaml.load(file, Loader=yaml.FullLoader)
        shared_data = hammerdb_data['shared_data']
        shared_data_pod = hammerdb_data['pod']
        shared_data_vm = hammerdb_data['vm']
        database_data = hammerdb_data[database]

        hammerdb_template = self.__get_yaml_template_by_workload(workload=workload)
        with open(os.path.join(self.__hammerdb_dir_path, 'internal_data', f'{hammerdb_template}.yaml')) as f:
            template_str = f.read()
        tm = Template(template_str)
        # merge 3 dictionaries
        if 'vm' in hammerdb_template:
            shared_data = {**shared_data, **shared_data_vm}
            render_data = {**shared_data, **database_data}
        elif 'pod' in hammerdb_template:
            shared_data = {**shared_data, **shared_data_pod}
            render_data = {**shared_data, **database_data}

        data = tm.render(render_data)
        hammerdb_name = hammerdb_template.replace('template', '')
        with open(os.path.join(f'{self.__current_run_path}', f'{hammerdb_name}{database}.yaml'), 'w') as f:
            f.write(data)
        # delete the generate data file with environment variable
        delete_generate_file(os.path.join(self.__hammerdb_dir_path, 'hammerdb_data.yaml'))
        # removing current_run yaml folder is occurred at the end of run: BenchmarkOperatorWorkloads__remove_run_workload_yaml_file

    @logger_time_stamp
    def generate_workload_yamls(self, workload: str):
        """
        This method generate workload yaml from template
        :return:
        """

        # Get workload data
        workload_name = workload.split('_')[0]
        workload_dir_path = os.path.join(self.__dir_path, workload_name)
        update_environment_variable(dir_path=workload_dir_path, yaml_file=f'{workload_name}_data_template.yaml')
        with open(os.path.join(workload_dir_path, f'{workload_name}_data.yaml'), 'r') as file:
            workload_data = yaml.load(file, Loader=yaml.FullLoader)
        shared_data = workload_data['shared_data']
        shared_data_pod = workload_data['pod']
        shared_data_vm = workload_data['vm']

        workload_template = self.__get_yaml_template_by_workload(workload=workload)
        template_file_path = os.path.join(f'{workload_dir_path}', 'internal_data', f'{workload_template}.yaml')
        with open(template_file_path) as f:
            template_str = f.read()
        tm = Template(template_str)

        # merge 3 dictionaries
        if 'vm' in workload_template:
            render_data = {**shared_data, **shared_data_vm}
        elif 'pod' in workload_template:
            render_data = {**shared_data, **shared_data_pod}

        data = tm.render(render_data)
        workload_file_name = workload_template.replace('_template', '')
        with open(os.path.join(f'{self.__current_run_path}', f'{workload_file_name}.yaml'), 'w') as f:
            f.write(data)
        # delete the generate data file with environment variable
        delete_generate_file(os.path.join(workload_dir_path, f'{workload_name}_data.yaml'))
        # removing current_run yaml folder is occurred at the end of run: BenchmarkOperatorWorkloads__remove_run_workload_yaml_file
