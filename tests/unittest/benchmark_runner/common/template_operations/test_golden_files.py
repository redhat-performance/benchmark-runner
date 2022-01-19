
from tests.unittest.benchmark_runner.common.template_operations.golden_files import GoldenFiles
from benchmark_runner.main.temporary_environment_variables import TemporaryEnvironmentVariables


def test_golden_files():
    """
    This tests that generated YAML files match expected
    previously generated files
    """
    with TemporaryEnvironmentVariables():
        golden_files = GoldenFiles()
        assert(golden_files.compare_golden_files())


test_golden_files()
