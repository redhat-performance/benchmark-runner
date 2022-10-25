
# Tests that run benchmark-runner workloads
import os
import time

import pytest
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.template_operations.render_yaml_from_template import render_yaml_file
from tests.integration.benchmark_runner.test_environment_variables import *


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
    # revert bach to default namespace
    workload_name = f'{workload}-{kind}'
    workload_yaml = f'{workload}_{kind}.yaml'
    workload_log = f'{workload}_{kind}.log'
    if oc.pod_exists(pod_name=workload_name, namespace=test_environment_variable['namespace']):
        oc.delete_pod_sync(yaml=os.path.join(templates_path, workload_yaml), pod_name=workload_name)
    if os.path.isfile(os.path.join(templates_path, workload_yaml)):
        os.remove(os.path.join(templates_path, workload_yaml))
    if os.path.isfile(os.path.join(templates_path, workload_log)):
        os.remove(os.path.join(templates_path, workload_log))


@pytest.fixture(autouse=True)
def before_after_each_test_fixture():
    """
    This method creates and deletes YAML files and test objects before and after each test
    :return:
    """
    # before all test: setup
    test_environment_variable['namespace'] = 'benchmark-runner'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    oc.delete_namespace(namespace=test_environment_variable['namespace'])
    # @TODO add vm once implement
    kinds = ('vm', 'pod', 'kata')
    for kind in kinds:
        __generate_yamls(workload='vdbench', kind=kind)
    yield
    # After all tests
    for kind in kinds:
        __delete_test_objects(workload='vdbench', kind=kind)
    oc.delete_namespace(namespace=test_environment_variable['namespace'])
    # revert to defaults namespace
    test_environment_variable['namespace'] = 'benchmark-operator'
    print('Test End')


def test_benchmark_runner_pod_create_initialized_ready_completed_deleted():
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


def test_benchmark_runner_kata_create_initialized_ready_completed_deleted():
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


# capture vm output - Must run it with 'pytest -s'
def test_benchmark_runner_vm_create_initialized_ready_completed_deleted():
    """
    This method test wait for vm create, initialized, ready, completed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    vm_name = 'vdbench-vm'
    assert oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_vm.yaml'), vm_name=vm_name, namespace=test_environment_variable['namespace'], timeout=600)
    assert oc.wait_for_ready(label='app=vdbench', run_type='vm', label_uuid=False, namespace=test_environment_variable['namespace'],  timeout=600)
    assert oc.delete_vm_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_vm.yaml'), vm_name=vm_name, namespace=test_environment_variable['namespace'], timeout=600)
    # Capture section
    #output_filename = os.path.join(f'{templates_path}', 'vdbench_vm.log')
    #vm_name = oc.get_vm(label='vdbench', namespace=test_environment_variable['namespace'])
    #oc.save_vm_log(vm_name=vm_name, output_filename=output_filename, namespace=test_environment_variable['namespace'])
    #assert oc.wait_for_vm_log_completed(vm_name=vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@', output_filename=output_filename)
    #assert oc.extract_vm_results(vm_name=vm_name, start_stamp=vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@', output_filename=output_filename)

