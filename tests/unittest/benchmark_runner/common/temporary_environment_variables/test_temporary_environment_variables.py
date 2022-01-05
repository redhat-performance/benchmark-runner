
import mock
import pytest
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.main.temporary_environment_variables import TemporaryEnvironmentVariables
from benchmark_runner.main.environment_variables import environment_variables

def test_golden_files():
    """
    Simple unit test to ensure that an environment variable gets
    restored when TemporaryEnvironmentVariable exits scope
    """

    # Outer temporary environment variables so we don't smash
    # the real ones during a test
    with TemporaryEnvironmentVariables():
        environment_variables.environment_variables_dict['test_var'] = 'Test_1'
        assert(environment_variables.environment_variables_dict['test_var'] == 'Test_1')

        with TemporaryEnvironmentVariables():
            environment_variables.environment_variables_dict['test_var'] = 'Test_2'

        assert(environment_variables.environment_variables_dict['test_var'] == 'Test_1')

        with TemporaryEnvironmentVariables():
            environment_variables.environment_variables_dict['test_var'] = 'Test_2'
            assert('test_var' in environment_variables.environment_variables_dict)
            del environment_variables.environment_variables_dict['test_var']
            assert('test_var' not in environment_variables.environment_variables_dict)

        assert(environment_variables.environment_variables_dict['test_var'] == 'Test_1')
