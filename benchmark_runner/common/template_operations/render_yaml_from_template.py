
import os
from jinja2 import Template
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.oc.oc import OC


def render_yaml_string(template_str: str, environment_variable_dict: dict = None):
    """
    This method renders a YAML string from the environment or alternative optional environment
    :param dir_path:
    :param yaml_file:
    :param environment_variable_dict: add it for testing purpose
    :return yaml text:
    """
    if not environment_variable_dict:
        environment_variable_dict = environment_variables.environment_variables_dict
    # Allow faking the Prometheus token so that we can generate deterministic test files
    if 'prom_token_override' in environment_variable_dict:
        environment_variable_dict['prom_token'] = environment_variable_dict.get('prom_token_override', '')
    else:
        oc = OC(kubeadmin_password=environment_variable_dict.get('kubeadmin_password', ''))
        # set prom token, skip if running on kubernetes just for now
        if environment_variable_dict.get("cluster") != 'kubernetes':
            environment_variable_dict['prom_token'] = oc.get_prom_token()
    return Template(template_str, keep_trailing_newline=True).render(environment_variable_dict)


def render_yaml_file(dir_path: str, yaml_file: str, environment_variable_dict: dict = None):
    """
    This method renders a YAML file from the environment or alternative optional environment
    :param dir_path:
    :param yaml_file:
    :param environment_variable_dict: Optional environment dictionary, default the Linux environment
    :return yaml text:
    """
    # Jinja render yaml file
    with open(os.path.join(dir_path, yaml_file)) as f:
        return render_yaml_string(f.read(), environment_variable_dict)
