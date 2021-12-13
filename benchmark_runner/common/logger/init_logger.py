
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
log_path = environment_variables_dict.get('run_artifacts_path', '')
if not os.path.isdir(log_path):
    os.mkdir(log_path)
fileHandler = logging.FileHandler(filename=f'{log_path}/benchmark_runner.log', mode='w+')
logger.addHandler(handler)
logger.addHandler(fileHandler)


def get_log_path():
    """
    This method return log path
    :return:
    """
    return f'{log_path}/benchmark_runner.log'

