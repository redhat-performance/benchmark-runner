
# Tests that run benchmark-runner workloads

import pytest
from benchmark_runner.common.oc.oc import OC, VMStatus
from benchmark_runner.common.oc.oc_exceptions import YAMLNotExist, PodNotCreateTimeout, PodTerminateTimeout, VMNotCreateTimeout
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
    # Generate stressng and uperf native templates
    for kind in ('pod_job', 'vm_direct'):
        __generate_yamls(workloads=['stressng'], kind=kind)
    __generate_yamls(workloads=['uperf'], kind='pod_server')
    __generate_yamls(workloads=['uperf'], kind='pod_client')
    __generate_yamls(workloads=['uperf'], kind='vm_direct')
    yield
    # After all tests
    for kind in kinds:
        __delete_test_objects(workloads=['vdbench', 'bootstorm'], kind=kind)
    __delete_test_objects(workloads=['stressng'], kind='pod_job')
    __delete_test_objects(workloads=['stressng'], kind='vm_direct')
    __delete_test_objects(workloads=['uperf'], kind='pod_server')
    __delete_test_objects(workloads=['uperf'], kind='pod_client')
    __delete_test_objects(workloads=['uperf'], kind='vm_direct')
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


def test_benchmark_runner_stressng_pod_create_complete_get_pod_info():
    """
    This method tests stressng pod create, complete, get_pod, get_pod_ip, get_pod_node, get_cluster_name
    Tests: wait_for_pod_create (label), wait_for_pod_completed, get_pod, get_pod_ip, get_pod_node, get_cluster_name
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    namespace = test_environment_variable['namespace']
    assert oc.create_async(yaml=os.path.join(f'{templates_path}', 'stressng_pod_job.yaml'))
    assert oc.wait_for_pod_create(label='app=stressng_workload-test123', namespace=namespace)
    assert oc.wait_for_pod_completed(label='app=stressng_workload-test123', label_uuid=False, job=True, namespace=namespace)
    # Test get_pod, get_pod_ip, get_pod_node on completed pod
    pod_name = oc.get_pod(label='stressng-pod', namespace=namespace)
    assert pod_name
    pod_ip = oc.get_pod_ip(pod_name=pod_name, namespace=namespace)
    assert pod_ip
    pod_node = oc.get_pod_node(pod_name=pod_name, namespace=namespace)
    assert pod_node
    # Test get_cluster_name
    cluster_name = oc.get_cluster_name()
    assert cluster_name



def test_benchmark_runner_uperf_pod_server_client_create_ready_get_ip_node_delete():
    """
    This method tests uperf pod server+client create, ready, get_pod_ip, get_pod_node, delete
    Tests: create_async, wait_for_pod_create (pod_name), wait_for_initialized, wait_for_ready,
           get_pod_ip (label and pod_name), get_pod_node (label and pod_name)
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    namespace = test_environment_variable['namespace']
    # Create server
    assert oc.create_async(yaml=os.path.join(f'{templates_path}', 'uperf_pod_server.yaml'))
    assert oc.wait_for_pod_create(pod_name='uperf-server', namespace=namespace)
    server_label = 'app=uperf-bench-server-0-test123'
    assert oc.wait_for_initialized(label=server_label, label_uuid=False, namespace=namespace)
    assert oc.wait_for_ready(label=server_label, label_uuid=False, namespace=namespace)
    # Test get_pod_ip and get_pod_node by label
    server_ip = oc.get_pod_ip(label=server_label, namespace=namespace)
    assert server_ip
    server_node = oc.get_pod_node(label=server_label, namespace=namespace)
    assert server_node
    # Create client with server IP
    client_yaml = os.path.join(f'{templates_path}', 'uperf_pod_client.yaml')
    with open(client_yaml, 'r') as f:
        content = f.read()
    content = content.replace('SERVER_IP_PLACEHOLDER', server_ip)
    with open(client_yaml, 'w') as f:
        f.write(content)
    assert oc.create_async(yaml=client_yaml)
    assert oc.wait_for_pod_create(pod_name='uperf-client', namespace=namespace)
    assert oc.wait_for_initialized(label='app=uperf-bench-client', label_uuid=False, namespace=namespace)
    assert oc.wait_for_ready(label='app=uperf-bench-client', label_uuid=False, namespace=namespace)
    # Test get_pod_ip and get_pod_node by pod_name
    client_pod = oc.get_pod(label='uperf-client', namespace=namespace)
    assert client_pod
    client_ip = oc.get_pod_ip(pod_name=client_pod, namespace=namespace)
    assert client_ip
    client_node = oc.get_pod_node(pod_name=client_pod, namespace=namespace)
    assert client_node


def test_benchmark_runner_uperf_vm_create_ready_get_vmi_ip_delete():
    """
    This method tests uperf vm server create, ready, get_vmi_ip, get_vm_node, delete
    Tests: create_vm_sync, wait_for_vm_create, wait_for_initialized, wait_for_ready,
           get_vmi_ip, get_vm_node, delete_vm_sync
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    namespace = test_environment_variable['namespace']
    vm_name = 'uperf-server-test123'
    assert oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'uperf_vm_direct.yaml'),
                             vm_name=vm_name, namespace=namespace)
    assert oc.wait_for_initialized(label='app=uperf-server-test123', label_uuid=False, namespace=namespace)
    assert oc.wait_for_ready(label='app=uperf-server-test123', label_uuid=False, namespace=namespace)
    # Test get_vmi_ip and get_vm_node
    vmi_ip = oc.get_vmi_ip(namespace=namespace, vm_name=vm_name)
    assert vmi_ip
    vm_node = oc.get_vm_node(vm_name=vm_name, namespace=namespace)
    assert vm_node
    # Cleanup
    assert oc.delete_vm_sync(yaml=os.path.join(f'{templates_path}', 'uperf_vm_direct.yaml'),
                             vm_name=vm_name, namespace=namespace)


def test_yaml_file_not_exist_error():
    """
    This method tests YAMLNotExist exception when YAML file does not exist
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with pytest.raises(YAMLNotExist) as err:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_nonexistent.yaml'), pod_name='stressng-pod-test123', timeout=1)


def test_create_sync_pod_timeout_error():
    """
    This method creates pod with timeout error
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with pytest.raises(PodNotCreateTimeout) as err:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod_job.yaml'), pod_name='stressng-pod-nonexistent', namespace=test_environment_variable['namespace'], timeout=1)


def test_delete_sync_pod_timeout_error():
    """
    This method deletes pod with timeout error
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    namespace = test_environment_variable['namespace']
    oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod_job.yaml'), pod_name='stressng-pod-test123', namespace=namespace)
    with pytest.raises(PodTerminateTimeout) as err:
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod_job.yaml'), pod_name='stressng-pod-test123', namespace=namespace, timeout=1)


def test_get_long_short_uuid():
    """
    This method tests UUID propagation in native workloads.
    In benchmark-operator, UUID was stored in CRD status (get_long_uuid);
    in native workloads, UUID is a pod label (benchmark-uuid).
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    namespace = test_environment_variable['namespace']
    assert oc.create_async(yaml=os.path.join(f'{templates_path}', 'stressng_pod_job.yaml'))
    assert oc.wait_for_pod_create(label='app=stressng_workload-test123', namespace=namespace)
    # Verify benchmark-uuid label is propagated from template
    assert oc.pod_label_exists(label_name='benchmark-uuid=test-uuid-123', namespace=namespace)


def test_create_sync_vm_timeout_error():
    """
    This method creates vm with timeout error
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with pytest.raises(VMNotCreateTimeout) as err:
        oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'stressng_vm_direct.yaml'), vm_name='stressng-vm-nonexistent', namespace=test_environment_variable['namespace'], timeout=1)


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
