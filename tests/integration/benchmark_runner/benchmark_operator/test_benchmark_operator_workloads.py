
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.benchmark_operator.benchmark_operator_exceptions import VMWorkloadNeedElasticSearch
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from tests.integration.benchmark_runner.test_environment_variables import *

benchmark_operator = BenchmarkOperatorWorkloads(kubeadmin_password=test_environment_variable['kubeadmin_password'],
                                                es_host='',
                                                es_port='')


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method is create benchmark operator pod once for ALL tests
    :return:
    """
    print('Install benchmark-operator pod')
    # only for functional environment - put resources limit 0 in manager.yaml
    if test_environment_variable.get('functional_resource_limit'):
        benchmark_operator.change_resource_limit_cpu_benchmark_operator_temp_patch(
            base_path=test_environment_variable.get('runner_path', ''),
            yaml_path='/benchmark-operator/config/manager/manager.yaml')
    # delete benchmark-operator pod if exist
    benchmark_operator.make_undeploy_benchmark_controller_manager_if_exist(runner_path=test_environment_variable['runner_path'])
    benchmark_operator.make_deploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])
    yield
    print('Delete benchmark-operator pod')
    benchmark_operator.make_undeploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])


def test_empty_elasticsearch_environment_parameter():
    """
    This method raise error when elasticsearch not exist in VM workload
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    with pytest.raises(VMWorkloadNeedElasticSearch):
        benchmark_operator._BenchmarkOperatorWorkloads__verify_elasticsearch_exist_for_vm_workload(workload='stressng_vm')
