
import copy
from benchmark_runner.main.environment_variables import environment_variables

class TemporaryEnvironmentVariables():
    def __init__(self):
        __saved_environment__ = None

    def __enter__(self):
        temporary_environment = copy.deepcopy(environment_variables.environment_variables_dict)
        self.__saved_environment__ = copy.deepcopy(environment_variables.environment_variables_dict)
        environment_variables.environment_variables_dict = temporary_environment

    def __exit__(self, exception_type, exception_value, traceback):
        if self.__saved_environment__:
            environment_variables.environment_variables_dict = self.__saved_environment__
