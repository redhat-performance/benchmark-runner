
import pytest

from benchmark_runner.benchmark_operator.benchmark_operator_exceptions import VMWorkloadNeedElasticSearch
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads


def test_empty_elasticsearch_environment_parameter():
    """
    This method raise error when elasticsearch not exist in VM workload
    """
    with pytest.raises(VMWorkloadNeedElasticSearch):
        BenchmarkOperatorWorkloads(workload='stressng_vm')
