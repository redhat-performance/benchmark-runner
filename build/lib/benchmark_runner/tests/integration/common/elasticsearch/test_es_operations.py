
import os
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.elasticshearch.es_operations import ESOperations
from benchmark_runner.common.elasticshearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import delete_generate_file, update_environment_variable
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path_up = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
templates_path = os.path.join(dir_path_up, 'templates')


def __delete_pod_and_yamls():
    """
    This method delete benchmark_operator
    :return:
    """
    oc = OC()
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
    benchmark_operator = BenchmarkOperatorWorkloads()
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
    oc = OC()
    oc.login()
    # before each test
    update_environment_variable(dir_path=templates_path, yaml_file='stressng_template.yaml')
    yield
    # After all tests
    __delete_pod_and_yamls()
    print('Test End')


def test_verify_es_data_uploaded():
    """
    This method verify that the data upload properly to elasticsearch
    :return:
    """
    es_host = os.environ.get('elasticsearch', '')
    es_port = os.environ.get('elasticsearch_port', '')
    es = ESOperations(es_host=es_host, es_port=es_port)
    oc = OC()
    oc.login()
    try:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng.yaml'), pod_name='stressng-workload')
        oc.wait_for_initialized(label='app=stressng_workload')
        oc.wait_for_ready(label='app=stressng_workload')
        oc.wait_for_completed(label='app=stressng_workload')
        # verify that data upload to elastic search
        assert es.verify_es_data_uploaded(index='ripsaw-stressng-results', uuid=oc.get_long_uuid())
    except ElasticSearchDataNotUploaded as err:
        raise err
    except Exception as err:
        raise err
