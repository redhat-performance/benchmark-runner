
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import delete_generate_file, \
    update_environment_variable
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from tests.integration.benchmark_runner.test_environment_variables import *


def __generate_pod_yamls():
    """
    This method create pod yaml from template and inject environment variable inside
    :return:
    """
    update_environment_variable(dir_path=templates_path, yaml_file='stressng_pod_template.yaml', environment_variable_dict=test_environment_variable)


def __delete_pod_yamls():
    """
    This method delete benchmark_operator
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    if oc._is_pod_exist(pod_name='stressng-pod-workload', namespace=test_environment_variable['namespace']):
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    delete_generate_file(full_path_yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'))


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method is create benchmark operator pod once for ALL tests
    :return:
    """
    print('Install benchmark-operator pod')

    # delete benchmark-operator pod if exist
    benchmark_operator = BenchmarkOperatorWorkloads(kubeadmin_password=test_environment_variable['kubeadmin_password'], es_host=test_environment_variable['elasticsearch'],
                                                    es_port=test_environment_variable['elasticsearch_port'])
    # only for functional environment - put resources limit 0 in manager.yaml
    if test_environment_variable.get('functional_resource_limit'):
        benchmark_operator.change_resource_limit_cpu_benchmark_operator_temp_patch(
            base_path=test_environment_variable.get('runner_path', ''),
            yaml_path='/benchmark-operator/config/manager/manager.yaml')
    benchmark_operator.make_undeploy_benchmark_controller_manager_if_exist(runner_path=test_environment_variable['runner_path'])
    benchmark_operator.make_deploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])
    yield
    print('Delete benchmark-operator pod')
    benchmark_operator.make_undeploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])


@pytest.fixture(autouse=True)
def before_after_each_test_fixture():
    """
    This method is clearing yaml before and after EACH test
    :return:
    """
    # before each test
    __generate_pod_yamls()
    yield
    # After all tests
    __delete_pod_yamls()
    print('Test End')


def test_verify_es_data_uploaded_stressng_pod():
    """
    This method verify that the data upload properly to elasticsearch
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    try:
        workload = 'stressng-pod'
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name=f'{workload}-workload')
        oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
        oc.wait_for_ready(label='app=stressng_workload', workload=workload)
        oc.wait_for_completed(label='app=stressng_workload', workload=workload)
        if test_environment_variable['elasticsearch']:
            # verify that data upload to elastic search
            es = ESOperations(es_host=test_environment_variable['elasticsearch'],
                              es_port=test_environment_variable['elasticsearch_port'])
            assert es.verify_es_data_uploaded(index='stressng-pod-results', uuid=oc.get_long_uuid(workload=workload))
    except ElasticSearchDataNotUploaded as err:
        raise err
    except Exception as err:
        raise err


def test_upload_to_es():
    """
    This method test upload to es
    @return:
    """
    if test_environment_variable['elasticsearch']:
        uuid = '7525d335-28f3-534a-b907-b34d1cdcc20a'
        # verify that data upload to elastic search
        es = ESOperations(es_host=test_environment_variable['elasticsearch'], es_port=test_environment_variable['elasticsearch_port'])
        data = {'tool': 'benchmark-runner', 'uuid': uuid}
        es.upload_to_es(data=data, index='benchmark-runner-test')
        assert es.verify_es_data_uploaded(index='benchmark-runner-test', uuid=uuid)