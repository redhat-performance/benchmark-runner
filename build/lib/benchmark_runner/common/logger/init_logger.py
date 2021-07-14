import sys
import os
import logging


logger_category_name = 'benchmark_runner.benchmark'
logger = logging.getLogger(logger_category_name)  # instantiating a logger
handler = logging.StreamHandler(sys.stdout)
log_path = os.getcwd()
fileHandler = logging.FileHandler(filename=f'{log_path}/benchmark_runner.log', mode='w+')
logger.addHandler(handler)
logger.addHandler(fileHandler)


def get_log_path():
    """
    This method return log path
    :return:
    """
    return f'{log_path}/benchmark_runner.log'

