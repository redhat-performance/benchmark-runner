
import os
import time
import yaml
import sys
import benchmark_runner
from multiprocessing import Process

from jinja2 import Template, TemplateSyntaxError
from benchmark_runner.common.template_operations.render_yaml_from_template import render_yaml_file
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.main.environment_variables import environment_variables


class TemplateOperations:
    """This class is responsible for template operations"""

    def __init__(self, workload: str = ''):
        self.__workload = workload
        self.initialize_environment(environment_variables.environment_variables_dict)

    def __initialize_dependent_variables__(self):
        self.__run_type = self.__environment_variables_dict.get('run_type', '')
        self.__run_artifacts_path = self.__environment_variables_dict.get('run_artifacts_path', '')
        self.__bulk_sleep_time = int(self.__environment_variables_dict.get('bulk_sleep_time', ''))
        self.__dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
        if self.__run_type == 'test_ci':
            self.__environment_variables_dict['es_suffix'] = '-test-ci'
        else:
            self.__environment_variables_dict['es_suffix'] = ''

    @logger_time_stamp
    def __split_run_bulks(self, iterable: range, limit: int = 1):
        """
        This method splits run into bulk depends on threads limit
        @return: run bulks
        """
        length = len(iterable)
        for ndx in range(0, length, limit):
            yield iterable[ndx:min(ndx + limit, length)]

    def __get_workload_template_kind(self):
        """
        Kata shares templates with pod
        """
        if self.__workload_kind == 'kata' or self.__workload_kind == 'pod':
            if self.__environment_variables_dict.get('kata_cpuoffline_workaround', False):
                logger.warn('*** WARNING: Enabling Kata CPU offline workaround ***')
            return 'pod'
        elif self.__workload_kind == 'vm':
            return 'vm'
        else:
            return None

    @staticmethod
    def __get_sub_dict(dictionary: dict, key: str, value: str):
        """
        Return a sub-dictionary of input dictionary as specified below.
        If dictionary[key][value] exists, return that.
        If dictionary[key][value] does not exist, but dictionary[key]['default'] exists, return
           dictionary[key]['default']
        Otherwise return an empty dictionary.
        :param dictionary: dictionary to be searched
        :param key: key to search for in dictionary
        :param value: value to be searched for under key
        :return: dictionary[key][value] if that exists, dictionary[key]['default'] if that exists, otherwise empty dictionary.
        """
        if key in dictionary:
            subdict = dictionary[key]
            if value in subdict:
                return subdict[value]
            elif 'default' in subdict:
                return subdict['default']
        return dict()

    def __build_template_data(self, previous_data: dict, template_root_data: dict):
        """
        Build data dictionary for rendering from template data.
        """
        template_data = template_root_data.get('template_data')
        shared_data = template_data.get('shared')
        if shared_data is None:
            shared_data = {}
        kind_data = self.__get_sub_dict(template_data, 'kind', self.__workload_kind)
        run_type_data = self.__get_sub_dict(template_data, 'run_type', self.__run_type)
        kind_runtype_data = self.__get_sub_dict(kind_data, 'run_type', self.__run_type)
        extra_data = self.__get_sub_dict(template_data, 'extra', self.__workload_extra_name)
        extra_kind_data = self.__get_sub_dict(extra_data, 'kind', self.__workload_kind)
        extra_runtype_data = self.__get_sub_dict(extra_data, 'run_type', self.__run_type)
        extra_kind_runtype_data = self.__get_sub_dict(extra_kind_data, 'run_type', self.__run_type)

        return {**previous_data, **shared_data,
                **kind_data, **run_type_data, **kind_runtype_data,
                **extra_data, **extra_kind_data, **extra_runtype_data, **extra_kind_runtype_data}

    @logger_time_stamp
    def __generate_yamls_internal(self, scale: str = None, scale_num: str = None, scale_node: str = None, redis: str = None):
        """
        Generate required .yaml files as a dictionary of file names and contents
        @param scale: current scale 0,1,2
        @param scale_num: the scale number
        @param scale_node: the scale node
        @param redis: redis
        """
        # This really belongs in __init__, but some tests rely on
        # being able to create this without an actual workload
        answer = {}
        self.__workload_name = self.__workload.split('_')[0]
        self.__workload_kind = self.__workload.split('_')[1]
        self.__workload_extra_name = '_'.join(self.__workload.split('_')[2:3])
        self.__workload_template_kind = self.__get_workload_template_kind()
        if self.__workload_extra_name:
            self.__standard_output_file = f"{'_'.join([self.__workload_name, self.__workload_template_kind, self.__workload_extra_name])}.yaml"
        else:
            if scale:
                self.__standard_output_file = f"{'_'.join([self.__workload_name, self.__workload_template_kind, scale])}.yaml"
            else:
                self.__standard_output_file = f"{'_'.join([self.__workload_name, self.__workload_template_kind])}.yaml"
        self.__standard_template_file = f"{'_'.join([self.__workload_name, self.__workload_template_kind])}_template.yaml"
        workload_dir_path = os.path.join((os.path.dirname(benchmark_runner.__file__)), "workloads", self.__workload, "template") \
            if self.__environment_variables_dict['template_in_workload_dir'] \
               else os.path.join(self.__dir_path, self.__workload_name)
        template_render_data = {
            'kind': self.__workload_kind,
            'workload_name': self.__workload_name,
            'workload_template_kind': self.__workload_template_kind,
            'workload_extra_name': self.__workload_extra_name,
            'standard_output_file': self.__standard_output_file,
            'standard_template_file': self.__standard_template_file,
            'scale': scale,
            'scale_num': scale_num,
            'scale_node': scale_node
            }
        self.__environment_variables_dict = {**self.__environment_variables_dict, **template_render_data}
        common_data = yaml.load(render_yaml_file(dir_path=self.__dir_path, yaml_file='common_template.yaml', environment_variable_dict=self.__environment_variables_dict), Loader=yaml.FullLoader)['common_data']

        template_render_data = {**self.__environment_variables_dict, **common_data}

        workload_data = yaml.load(render_yaml_file(workload_dir_path, f'{self.__workload_name}_data_template.yaml', template_render_data), Loader=yaml.FullLoader)

        if self.__environment_variables_dict.get("config_from_args"):
            config = dict([kv.split("=") for kv in sys.argv[1:]])
            workload_data["template_data"]["run_type"]["default"] = config

        render_data = self.__build_template_data(template_render_data, workload_data)

        out_files = [{'name': self.__standard_output_file, 'template': self.__standard_template_file}]
        if 'files' in workload_data:
            out_files.extend(workload_data['files'])
        for out_file in out_files:
            filename = out_file['name']
            if 'template' in out_file:
                template_file = out_file['template']
            else:
                file_components = os.path.splitext(filename)
                template_file = f'{file_components[0]}_template{file_components[1]}'
            try:
                with open(os.path.join(workload_dir_path, 'internal_data', template_file)) as f:
                    template = Template(f.read(), keep_trailing_newline=True)
            except TemplateSyntaxError as err:
                raise SyntaxError(f"Error while rendering {template_file}: {err}")
            answer[filename] = f"{template.render(render_data)}"
            # namespace
            if os.path.isfile(os.path.join(self.__dir_path, f'namespace_template.yaml')):
                answer['namespace.yaml'] = render_yaml_file(dir_path=self.__dir_path, yaml_file='namespace_template.yaml', environment_variable_dict=self.__environment_variables_dict)
            # windows workload
            if 'windows' in self.__workload_name:
                answer['windows_dv.yaml'] = render_yaml_file(dir_path=os.path.join(workload_dir_path, 'internal_data'), yaml_file='windows_dv_template.yaml', environment_variable_dict=render_data)
            # vdbench scale
            if scale and redis and 'vdbench' in self.__workload_name:
                    answer['redis.yaml'] = render_yaml_file(dir_path=os.path.join(self.__dir_path, 'scale'), yaml_file='redis_template.yaml', environment_variable_dict=self.__environment_variables_dict)
                    answer['state_signals_exporter_pod.yaml'] = render_yaml_file(dir_path=os.path.join(self.__dir_path, 'scale'), yaml_file='state_signals_exporter_pod_template.yaml', environment_variable_dict=self.__environment_variables_dict)
        for filename, data in answer.items():
            with open(os.path.join(self.__run_artifacts_path, filename), 'w') as f:
                f.write(data)

    @logger_time_stamp
    def generate_yamls(self, scale: str = '', scale_nodes: list = [], redis: str = None, thread_limit: int = None):
        """
        This method generate workload yaml from template
        :return:
        """
        if not scale:
            self.__generate_yamls_internal()
        else:
            proc = []
            scale = int(scale)
            bulks = tuple(self.__split_run_bulks(iterable=range(scale * len(scale_nodes)), limit=thread_limit))
            if scale_nodes:
                for bulk in bulks:
                    for num in bulk:
                        p = Process(target=self.__generate_yamls_internal, args=(str(num), str(scale * len(scale_nodes)), scale_nodes[int(num / scale)], redis,))
                        p.start()
                        proc.append(p)
                    for p in proc:
                        p.join()
                    # sleep between bulks
                    time.sleep(self.__bulk_sleep_time)
            else:
                for scale_num in range(scale):
                    self.__generate_yamls_internal(scale=str(scale_num))

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
        return self.__run_artifacts_path
