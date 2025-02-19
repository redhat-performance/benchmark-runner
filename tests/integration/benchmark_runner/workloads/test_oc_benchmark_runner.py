
# Tests that run benchmark-runner workloads

import pytest
from benchmark_runner.common.oc.oc import OC, VMStatus
from benchmark_runner.common.virtctl.virtctl import Virtctl
from benchmark_runner.common.template_operations.render_yaml_from_template import render_yaml_file
from tests.integration.benchmark_runner.test_environment_variables import *


def __generate_yamls(workloads: list, kind: str):
    """
    This method creates YAML files from templates, substituting environment variables.
    :return:
    """
    for workload in workloads:
        yaml_template = f'{workload}_{kind}_template.yaml'
        if os.path.exists(os.path.join(templates_path, yaml_template)):
            yaml_file = f'{workload}_{kind}.yaml'
            data = render_yaml_file(dir_path=templates_path, yaml_file=yaml_template, environment_variable_dict=test_environment_variable)
            with open(os.path.join(templates_path, yaml_file), 'w') as f:
                f.write(data)


def __delete_test_objects(workloads: list, kind: str):
    """
    This method deletes logs and YAML files if they exist
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    for workload in workloads:
        workload_name = f'{workload}-{kind}'
        workload_yaml = f'{workload}_{kind}.yaml'
        workload_log = f'{workload}_{kind}.log'
        if os.path.exists(os.path.join(templates_path, workload_yaml)):
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
    kinds = ('pod', 'vm')
    for kind in kinds:
        __generate_yamls(workloads=['vdbench', 'bootstorm'], kind=kind)
    yield
    # After all tests
    for kind in kinds:
        __delete_test_objects(workloads=['vdbench', 'bootstorm'], kind=kind)
    oc.delete_namespace(namespace=test_environment_variable['namespace'])
    # revert to defaults namespace
    test_environment_variable['namespace'] = 'benchmark-operator'
    print('Test End')


def test_benchmark_runner_bootstorm_vm_create_start_running_delete():
    """
    This method tests bootstorm vm create, start, running, delete
    :return:
    """
    vm_name = 'bootstorm-vm-72e726b0'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.create_async(yaml=os.path.join(f'{templates_path}', 'bootstorm_vm.yaml'))
    assert oc.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Stopped, namespace=test_environment_variable['namespace'])
    virtctl = Virtctl()
    assert virtctl.start_vm_sync(vm_name=vm_name, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Running, namespace=test_environment_variable['namespace'])


@pytest.mark.skip(reason="Disable ODF")
def test_benchmark_runner_vdbench_pod_create_initialized_ready_complete_delete():
    """
    This method tests vdbench pod create, initialized, ready, complete, delete
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_pod.yaml'), pod_name='vdbench-pod', namespace=test_environment_variable['namespace'])
    assert oc.wait_for_initialized(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_ready(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_pod_completed(label='app=vdbench', label_uuid=False, job=False, namespace=test_environment_variable['namespace'])


@pytest.mark.skip(reason="Disable ODF - use: 'pytest -s' for running it")
def test_benchmark_runner_vdbench_vm_create_ready_complete_delete():
    """
    This method tests vdbench vm create, ready, complete, delete
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    vm_name = 'vdbench-vm'
    assert oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_vm.yaml'),
                            vm_name=vm_name, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_ready(label='app=vdbench', run_type='vm', label_uuid=False, namespace=test_environment_variable['namespace'])
    # Create vm log should be direct after vm is ready
    virtctl = Virtctl()
    virtctl.save_vm_log(vm_name=vm_name, output_filename=os.path.join(f'{templates_path}', 'vdbench_vm.log'), namespace=test_environment_variable['namespace'])
    assert oc.wait_for_vm_log_completed(vm_name=vm_name, end_stamp='@@~@@END-WORKLOAD@@~@@', output_filename=os.path.join(f'{templates_path}', 'vdbench_vm.log'))


@pytest.mark.skip(reason="Disable kata")
def test_benchmark_runner_vdbench_kata_create_initialized_ready_complete_delete():
    """
    This method tests wait for kata create, initialized, ready, complete, delete
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'vdbench_kata.yaml'), pod_name='vdbench-kata', namespace=test_environment_variable['namespace'])
    assert oc.wait_for_initialized(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_ready(label='app=vdbench', label_uuid=False, namespace=test_environment_variable['namespace'])
    assert oc.wait_for_pod_completed(label='app=vdbench', label_uuid=False, job=False, namespace=test_environment_variable['namespace'])
