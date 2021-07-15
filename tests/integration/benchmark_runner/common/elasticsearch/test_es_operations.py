
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import delete_generate_file, \
    update_environment_variable
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from tests.integration.benchmark_runner.get_environment_parameters import *


def __delete_pod_and_yamls():
    """
    This method delete benchmark_operator
    :return:
    """
    oc = OC(kubeadmin_password=environment_variable['kubeadmin_password'])
    oc.login()
    oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng.yaml'), pod_name='stressng-workload')
    delete_generate_file(full_path_yaml=os.path.join(f'{templates_path}', 'stressng.yaml'))


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method is clearing yaml before and after test
    :return:
    """
    print('Install benchmark-operator pod')
    benchmark_operator = BenchmarkOperatorWorkloads(kubeadmin_password=environment_variable['kubeadmin_password'], es_host=environment_variable['elasticsearch'],
                                                    es_port=environment_variable['elasticsearch_port'], workload=environment_variable['workload'])
    benchmark_operator.helm_install_benchmark_operator()
    yield
    print('Delete benchmark-operator pod')
    benchmark_operator.helm_delete_benchmark_operator()


@pytest.fixture(autouse=True)
def before_after_each_test_fixture():
    """
    This method is clearing yaml before and after test
    :return:
    """
    # before each test
    update_environment_variable(dir_path=templates_path, yaml_file='stressng_template.yaml', environment_variable_dict=environment_variable)
    yield
    # After all tests
    __delete_pod_and_yamls()
    print('Test End')


def test_verify_es_data_uploaded_stressng_pod():
    """
    This method verify that the data upload properly to elasticsearch
    :return:
    """
    oc = OC(kubeadmin_password=environment_variable['kubeadmin_password'])
    oc.login()
    try:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng.yaml'), pod_name='stressng-workload')
        oc.wait_for_initialized(label='app=stressng_workload')
        oc.wait_for_ready(label='app=stressng_workload')
        oc.wait_for_completed(label='app=stressng_workload')
        if environment_variable['elasticsearch']:
            # verify that data upload to elastic search
            es = ESOperations(es_host=environment_variable['elasticsearch'],
                              es_port=environment_variable['elasticsearch_port'])
            assert es.verify_es_data_uploaded(index='ripsaw-stressng-results', uuid=oc.get_long_uuid())
    except ElasticSearchDataNotUploaded as err:
        raise err
    except Exception as err:
        raise err
