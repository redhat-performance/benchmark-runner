
# Tests that run benchmark-runner workloads

import pytest
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import render_yaml_file
from tests.integration.benchmark_runner.test_environment_variables import *

test_environment_variable['namespace'] = 'benchmark-runner'


def __generate_yamls(workload: str, kind: str):
    """
    This method creates YAML files from templates, substituting environment variables.
    :return:
    """
    yaml_template = f'{workload}_{kind}_template.yaml'
    yaml_file = f'{workload}_{kind}.yaml'
    data = render_yaml_file(dir_path=templates_path, yaml_file=yaml_template, environment_variable_dict=test_environment_variable)
    with open(os.path.join(templates_path, yaml_file), 'w') as f:
        f.write(data)


def __delete_test_objects(workload: str, kind: str):
    """
    Delete objects and YAML files if they exist
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    workload_name = f'{workload}-{kind}'
    workload_yaml = f'{workload}_{kind}.yaml'
    if oc._is_pod_exist(pod_name=workload_name, namespace=test_environment_variable['namespace']):
        oc.delete_pod_sync(yaml=os.path.join(templates_path, workload_yaml), pod_name=workload_name)
    if os.path.isfile(os.path.join(templates_path, workload_yaml)):
        os.remove(os.path.join(templates_path, workload_yaml))


@pytest.fixture(autouse=True)
def before_after_each_test_fixture():
    """
    This method creates and deletes YAML files and test objects before and after each test
    :return:
    """
    # before all test: setup
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.delete_all_pods(namespace=test_environment_variable['namespace'])
    # @TODO add vm once implement
    kinds = ('pod', 'kata')
    for kind in kinds:
        __generate_yamls(workload='vdbench', kind=kind)
    yield
    # After all tests
    for kind in kinds:
        __delete_test_objects(workload='vdbench', kind=kind)
    assert oc.delete_all_pods(namespace=test_environment_variable['namespace'])
    print('Test End')


def test_wait_for_benchmark_runner_pod_create_initialized_ready_completed_deleted():
    """
    This method test wait for pod create, initialized, ready, completed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_pod.yaml'), pod_name='vdbench-pod', namespace=test_environment_variable['namespace'])
    assert oc.wait_for_initialized(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_ready(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_pod_completed(label='app=vdbench', label_uuid=False, job=False, namespace=test_environment_variable['namespace'])


def test_wait_for_benchmark_runner_kata_create_initialized_ready_completed_deleted():
    """
    This method test wait for kata create, initialized, ready, completed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_kata.yaml'), pod_name='vdbench-kata', namespace=test_environment_variable['namespace'])
    assert oc.wait_for_initialized(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_ready(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_pod_completed(label='app=vdbench', label_uuid=False, job=False, namespace=test_environment_variable['namespace'])
