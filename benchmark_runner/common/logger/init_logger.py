
import sys
import os
import logging
from benchmark_runner.main.environment_variables import environment_variables

logger_category_name = 'benchmark_runner.benchmark'
logger = logging.getLogger(logger_category_name)  # instantiating a logger
handler = logging.StreamHandler(sys.stdout)
environment_variables_dict = environment_variables.environment_variables_dict
# log_path = os.getcwd()
# logs folder
run_artifacts = environment_variables_dict.get('run_artifacts', '')
run_artifacts_path = environment_variables_dict.get('run_artifacts_path', '')
if not os.path.isdir(run_artifacts_path):
    os.makedirs(run_artifacts, exist_ok=True)
    os.mkdir(run_artifacts_path)
fileHandler = logging.FileHandler(filename=f'{run_artifacts_path}/benchmark_runner.log', mode='w+')
logger.addHandler(handler)
logger.addHandler(fileHandler)


def get_log_path():
    """
    This method return log path
    :return:
    """
    return f'{run_artifacts_path}/benchmark_runner.log'
