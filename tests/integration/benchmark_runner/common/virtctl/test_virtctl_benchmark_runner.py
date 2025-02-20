
# Tests that run benchmark-runner workloads

import pytest
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.virtctl.virtctl import Virtctl
from benchmark_runner.common.template_operations.render_yaml_from_template import render_yaml_file
from tests.integration.benchmark_runner.test_environment_variables import *


def __generate_yamls(workload: str, kind: str = 'vm'):
    """
    This method creates YAML files from templates, substituting environment variables.
    :return:
    """
    yaml_template = f'{workload}_{kind}_template.yaml'
    yaml_file = f'{workload}_{kind}.yaml'
    data = render_yaml_file(dir_path=templates_path, yaml_file=yaml_template, environment_variable_dict=test_environment_variable)
    with open(os.path.join(templates_path, yaml_file), 'w') as f:
        f.write(data)


def __delete_test_objects(workload: str, kind: str = 'vm'):
    """
    Delete objects and YAML files if they exist
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
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
    oc.delete_namespace(namespace=test_environment_variable['namespace'])
    __generate_yamls(workload='vdbench')
    yield
    # After all tests
    __delete_test_objects(workload='vdbench')
    oc.delete_namespace(namespace=test_environment_variable['namespace'])
    # revert to defaults namespace
    test_environment_variable['namespace'] = 'benchmark-operator'
    print('Test End')


@pytest.mark.skip(reason="Disable ODF")
# capture vm output - Must run it with 'pytest -s'
def test_benchmark_runner_vm_create_ready_stop_start_expose_delete():
    """
    This method test wait for vm create, ready, stop, start, delete
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    virtctl = Virtctl()
    vm_name = 'vdbench-vm'
    assert oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_vm.yaml'), vm_name=vm_name, namespace=test_environment_variable['namespace'], timeout=600)
    assert oc.wait_for_ready(label='app=vdbench', run_type='vm', label_uuid=False, namespace=test_environment_variable['namespace'],  timeout=600)
    assert virtctl.stop_vm_sync(vm_name=vm_name, namespace=test_environment_variable['namespace'])
    assert virtctl.start_vm_sync(vm_name=vm_name, namespace=test_environment_variable['namespace'])
    virtctl.expose_vm(vm_name=vm_name, namespace=test_environment_variable['namespace'])
    vm_node = oc.get_vm_node(vm_name=vm_name, namespace=test_environment_variable['namespace'])
    assert vm_node
    assert oc.get_nodes_addresses()[vm_node]
    assert oc.get_exposed_vm_port(vm_name=vm_name, namespace=test_environment_variable['namespace'])
    assert oc.delete_vm_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_vm.yaml'), vm_name=vm_name, namespace=test_environment_variable['namespace'], timeout=600)
