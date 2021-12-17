
import pytest
import os
from uuid import uuid4

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import render_yaml_file
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
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
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    if oc._is_pod_exist(pod_name='stressng-pod-workload', namespace=test_environment_variable['namespace']):
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    if os.path.isfile(os.path.join(f'{templates_path}', 'stressng_pod.yaml')):
        os.remove(os.path.join(f'{templates_path}', 'stressng_pod.yaml'))


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method is create benchmark operator pod once for ALL tests
    :return:
    """
    print('Deploy benchmark-operator pod')

    # delete benchmark-operator pod if exist
    benchmark_operator = BenchmarkOperatorWorkloads(kubeadmin_password=test_environment_variable['kubeadmin_password'], es_host=test_environment_variable['elasticsearch'],
                                                    es_port=test_environment_variable['elasticsearch_port'])
    benchmark_operator.make_undeploy_benchmark_controller_manager_if_exist(runner_path=test_environment_variable['runner_path'])
    benchmark_operator.make_deploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])
    yield
    print('Undeploy benchmark-operator pod')
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
        oc.create_pod_sync(yaml=os.path.join(templates_path, 'stressng_pod.yaml'), pod_name=f'{workload}-workload')
        oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
        oc.wait_for_ready(label='app=stressng_workload', workload=workload)
        oc.wait_for_pod_completed(label='app=stressng_workload', workload=workload)
        # system-metrics
        if test_environment_variable['system_metrics']:
            es = ESOperations(es_host=test_environment_variable['elasticsearch'],
                              es_port=test_environment_variable['elasticsearch_port'])
            assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
            assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
            assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
            assert es.verify_es_data_uploaded(index='system-metrics-test', uuid=oc.get_long_uuid(workload=workload))
        if test_environment_variable['elasticsearch']:
            # verify that data upload to elastic search
            es = ESOperations(es_host=test_environment_variable['elasticsearch'],
                              es_port=test_environment_variable['elasticsearch_port'])
            assert es.verify_es_data_uploaded(index='stressng-pod-test-results', uuid=oc.get_long_uuid(workload=workload))
    except ElasticSearchDataNotUploaded as err:
        raise err
    except Exception as err:
        raise err
