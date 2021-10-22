
import os
from jinja2 import Template
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.oc.oc import OC


def update_environment_variable(dir_path: str, yaml_file: str, environment_variable_dict: dict = None):
    """
    This method update environment variable inside yaml file
    :param dir_path:
    :param yaml_file:
    :param environment_variable_dict: add it for testing purpose
    :return:
    """
    if not environment_variable_dict:
        environment_variable_dict = environment_variables.environment_variables_dict
    oc = OC(kubeadmin_password=environment_variable_dict.get('kubeadmin_password', ''))
    # set prom token
    environment_variable_dict['prom_token'] = oc.get_prom_token()
    # Jinja render yaml file
    with open(os.path.join(dir_path, yaml_file)) as f:
        template_str = f.read()
    tm = Template(template_str)
    data = tm.render(environment_variable_dict)
    yaml_file = yaml_file.replace('_template', '')
    with open(os.path.join(dir_path, yaml_file), 'w') as f:
        f.write(data)


def delete_generate_file(full_path_yaml: str):
    """
    This method update environment variable inside yaml file
    :param full_path_yaml:
    :return:
    """
    if os.path.isfile(full_path_yaml):
        os.remove(os.path.join(full_path_yaml))
