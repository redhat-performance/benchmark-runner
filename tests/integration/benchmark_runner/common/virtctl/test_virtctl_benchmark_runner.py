
# Tests that run benchmark-runner workloads

import tempfile
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
    __generate_yamls(workload='stressng', kind='vm_direct')
    yield
    # After all tests
    __delete_test_objects(workload='vdbench')
    __delete_test_objects(workload='stressng', kind='vm_direct')
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


def test_virtctl_generate_ssh_key():
    """
    This method tests generate_ssh_key and get_ssh_public_key
    """
    virtctl = Virtctl()
    key_path = os.path.join(tempfile.mkdtemp(), 'test_key')
    result = virtctl.generate_ssh_key(key_path=key_path)
    assert result == key_path
    assert os.path.exists(key_path)
    assert os.path.exists(f'{key_path}.pub')
    pub_key = virtctl.get_ssh_public_key(key_path=key_path)
    assert pub_key.startswith('ssh-rsa ')


def test_virtctl_ssh_ready_and_wait():
    """
    This method tests virtctl_ssh and wait_for_vm_workload_completed
    on a stressng VM with SSH key injected via cloud-init
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    virtctl = Virtctl()
    vm_name = 'stressng-vm-test123'
    namespace = test_environment_variable['namespace']

    # Generate SSH key
    key_path = os.path.join(tempfile.mkdtemp(), 'vm_key')
    virtctl.generate_ssh_key(key_path=key_path)
    pub_key = virtctl.get_ssh_public_key(key_path=key_path)

    # Read template source and inject SSH key, write as rendered YAML
    template_file = os.path.join(f'{templates_path}', 'stressng_vm_direct_template.yaml')
    vm_yaml = os.path.join(f'{templates_path}', 'stressng_vm_direct_ssh.yaml')
    with open(template_file, 'r') as f:
        content = f.read()
    content = content.replace('ssh_pwauth: true', f'ssh_pwauth: true\n              ssh_authorized_keys:\n                - {pub_key}')
    with open(vm_yaml, 'w') as f:
        f.write(content)

    # Create VM
    assert oc.create_vm_sync(yaml=vm_yaml, vm_name=vm_name, namespace=namespace)
    assert oc.wait_for_ready(label='app=stressng-vm-test123', label_uuid=False, namespace=namespace)

    # Test get_vmi_ip and get_vm_node
    vmi_ip = oc.get_vmi_ip(namespace=namespace, vm_name=vm_name)
    assert vmi_ip
    vm_node = oc.get_vm_node(vm_name=vm_name, namespace=namespace)
    assert vm_node

    # Wait for SSH to be ready (cloud-init needs time to install packages + setup SSH)
    import time
    for i in range(0, 180, 5):
        result = virtctl.virtctl_ssh(vm_name=vm_name, command='echo hello', namespace=namespace, key_path=key_path)
        if result is not None and 'hello' in result:
            break
        time.sleep(5)
    assert result is not None
    assert 'hello' in result

    # Test wait_for_vm_workload_completed (public method that combines SSH wait + file wait + SCP)
    local_path = os.path.join(tempfile.mkdtemp(), 'stressng.json')
    assert virtctl.wait_for_vm_workload_completed(vm_name=vm_name, file_path='/tmp/stressng.json',
                                                   local_path=local_path, namespace=namespace,
                                                   key_path=key_path, timeout=300)
    assert os.path.exists(local_path)

    # Cleanup
    assert oc.delete_vm_sync(vm_name=vm_name, namespace=namespace)
    if os.path.exists(vm_yaml):
        os.remove(vm_yaml)
