
# Tests that run benchmark-runner workloads

import os
import tempfile
import pytest
from csv import DictReader
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
    __generate_yamls(workload='stressng', kind='vm')
    yield
    # After all tests
    __delete_test_objects(workload='vdbench')
    __delete_test_objects(workload='stressng', kind='vm')
    oc.delete_namespace(namespace=test_environment_variable['namespace'])
    # revert to defaults namespace
    test_environment_variable['namespace'] = 'benchmark-runner'
    print('Test End')


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
    template_file = os.path.join(f'{templates_path}', 'stressng_vm_template.yaml')
    vm_yaml = os.path.join(f'{templates_path}', 'stressng_vm_ssh.yaml')
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
        result = virtctl.virtctl_ssh(vm_name=vm_name, command='echo hello', namespace=namespace, key_path=key_path, username='fedora')
        if result is not None and 'hello' in result:
            break
        time.sleep(5)
    assert result is not None
    assert 'hello' in result

    # Test wait_for_vm_workload_completed (public method that combines SSH wait + file wait + SCP)
    local_path = os.path.join(tempfile.mkdtemp(), 'stressng.json')
    assert virtctl.wait_for_vm_workload_completed(vm_name=vm_name, file_path='/tmp/stressng.json',
                                                   local_path=local_path, namespace=namespace,
                                                   key_path=key_path, username='fedora', timeout=300)
    assert os.path.exists(local_path)

    # Cleanup
    assert oc.delete_vm_sync(vm_name=vm_name, namespace=namespace)
    if os.path.exists(vm_yaml):
        os.remove(vm_yaml)


def test_virtctl_vdbench_vm_ephemeral_file_count_scp_and_parse():
    """
    Test the vdbench VM ephemeral flow: Secret-based cloud-init with SSH key,
    emptyDisk storage, wait_for_vm_completed_by_file_count, count_remote_vm_files,
    and scp_vm_files.
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    virtctl = Virtctl()
    namespace = test_environment_variable['namespace']
    vm_name = 'vdbench-vm-test'

    # Generate SSH key and inject into environment for template rendering
    key_path = os.path.join(tempfile.mkdtemp(), 'vm_key')
    virtctl.generate_ssh_key(key_path=key_path)
    pub_key = virtctl.get_ssh_public_key(key_path=key_path)
    test_environment_variable['ssh_public_key'] = pub_key

    # Render vdbench VM ephemeral template (Secret + VirtualMachine with emptyDisk)
    vm_yaml = os.path.join(templates_path, 'vdbench_vm_ephemeral_test.yaml')
    rendered = render_yaml_file(dir_path=templates_path, yaml_file='vdbench_vm_ephemeral_template.yaml',
                                environment_variable_dict=test_environment_variable)
    with open(vm_yaml, 'w') as f:
        f.write(rendered)

    # Create namespace + Secret + VM
    oc.create_async(yaml=vm_yaml)
    assert oc.wait_for_vm_create(vm_name=vm_name, namespace=namespace, timeout=600)
    assert oc.wait_for_ready(label='app=vdbench-test', run_type='vm', label_uuid=False,
                             namespace=namespace, timeout=600)

    # Wait for CSV files (IO_OPERATION=oltp1,oltp2 => 2 files expected)
    assert virtctl.wait_for_vm_completed_by_file_count(
        vm_name=vm_name, remote_dir='/workload/', expected_count=2,
        namespace=namespace, key_path=key_path, username='cloud-user', timeout=1200)

    # Verify count_remote_vm_files
    csv_count = virtctl.count_remote_vm_files(
        vm_name=vm_name, remote_dir='/workload/', file_type='.csv',
        namespace=namespace, key_path=key_path, username='cloud-user')
    assert csv_count >= 2

    # SCP files to local
    local_dir = tempfile.mkdtemp()
    local_files = virtctl.scp_vm_files(
        vm_name=vm_name, remote_dir='/workload/', local_dir=local_dir,
        namespace=namespace, key_path=key_path, username='cloud-user')
    assert len(local_files) >= 2
    for local_file in local_files:
        assert os.path.exists(local_file)
        assert os.path.getsize(local_file) > 0
        with open(local_file, 'r') as f:
            reader = DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert 'Run' in rows[0]

    # Cleanup
    assert oc.delete_vm_sync(yaml=vm_yaml, vm_name=vm_name, namespace=namespace, timeout=600)
    if os.path.exists(vm_yaml):
        os.remove(vm_yaml)
