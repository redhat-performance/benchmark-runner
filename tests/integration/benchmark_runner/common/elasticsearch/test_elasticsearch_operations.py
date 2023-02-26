
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.template_operations.render_yaml_from_template import render_yaml_file
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations
from tests.integration.benchmark_runner.test_environment_variables import *


def __generate_pod_yamls():
    """
    This method create pod yaml from template and inject environment variable inside
    :return:
    """
    yaml_template = 'stressng_pod_template.yaml'
    data = render_yaml_file(dir_path=templates_path, yaml_file=yaml_template, environment_variable_dict=test_environment_variable)
    yaml_file = yaml_template.replace('_template', '')
    with open(os.path.join(templates_path, yaml_file), 'w') as f:
        f.write(data)


def __delete_pod_yamls():
    """
    This method delete benchmark_operator
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable.get('kubeadmin_password', ''))
    oc.login()
    if oc.pod_exists(pod_name='stressng-pod-workload', namespace=test_environment_variable.get('namespace', '')):
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    if os.path.isfile(os.path.join(f'{templates_path}', 'stressng_pod.yaml')):
        os.remove(os.path.join(f'{templates_path}', 'stressng_pod.yaml'))


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method is created benchmark operator pod once for ALL tests
    :return:
    """
    print('Deploy benchmark-operator pod')

    # delete benchmark-operator pod if exist
    benchmark_operator = BenchmarkOperatorWorkloadsOperations()
    benchmark_operator.set_login(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    benchmark_operator.make_undeploy_benchmark_controller_manager_if_exist(runner_path=test_environment_variable.get('runner_path', ''))
    benchmark_operator.make_deploy_benchmark_controller_manager(runner_path=test_environment_variable.get('runner_path', ''))
    yield
    print('Undeploy benchmark-operator pod')
    benchmark_operator.make_undeploy_benchmark_controller_manager(runner_path=test_environment_variable.get('runner_path', ''))


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


def test_verify_elasticsearch_data_uploaded_stressng_pod():
    """
    This method verify that the data upload properly to elasticsearch
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    try:
        workload = 'stressng-pod'
        oc.create_pod_sync(yaml=os.path.join(templates_path, 'stressng_pod.yaml'), pod_name=f'{workload}-workload')
        oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
        oc.wait_for_ready(label='app=stressng_workload', workload=workload)
        oc.wait_for_pod_completed(label='app=stressng_workload', workload=workload)
        # system-metrics
        if test_environment_variable['system_metrics']:
            es = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''), es_port=test_environment_variable.get('elasticsearch_port', ''), es_user=test_environment_variable.get('elasticsearch_user', ''), es_password=test_environment_variable.get('elasticsearch_password', ''))
            if test_environment_variable['system_metrics']:
                assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
                assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
                assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
                assert es.verify_elasticsearch_data_uploaded(index='system-metrics-test', uuid=oc.get_long_uuid(workload=workload))
        if test_environment_variable['elasticsearch']:
            # verify that data upload to elastic search
            es = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''), es_port=test_environment_variable.get('elasticsearch_port', ''), es_user=test_environment_variable.get('elasticsearch_user', ''), es_password=test_environment_variable.get('elasticsearch_password', ''))
            assert es.verify_elasticsearch_data_uploaded(index='stressng-pod-test-results', uuid=oc.get_long_uuid(workload=workload))
    except ElasticSearchDataNotUploaded as err:
        raise err
    except Exception as err:
        raise err
