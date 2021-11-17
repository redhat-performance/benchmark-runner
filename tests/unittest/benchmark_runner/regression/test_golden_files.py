
import mock
import pytest
from tests.unittest.benchmark_runner.regression.golden_files import GoldenFiles


def test_golden_files():
    """
    This tests that generated YAML files match expected
    previously generated files
    """
    g = GoldenFiles()
    assert(g.compare_golden_files())

g = GoldenFiles()
assert(g.compare_golden_files())
