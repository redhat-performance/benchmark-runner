
import mock
import pytest
from tests.unittest.benchmark_runner.common.workload_flavors.golden_files import GoldenFiles
from benchmark_runner.main.temporary_environment_variables import TemporaryEnvironmentVariables

def test_golden_files():
    """
    This tests that generated YAML files match expected
    previously generated files
    """
    with TemporaryEnvironmentVariables():
        g = GoldenFiles()
        assert(g.compare_golden_files())

test_golden_files()
