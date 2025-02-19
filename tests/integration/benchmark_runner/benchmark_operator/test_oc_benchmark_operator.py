
import time
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import LoginFailed, PodNotCreateTimeout, PodTerminateTimeout, VMNotCreateTimeout, YAMLNotExist
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.common.template_operations.render_yaml_from_template import render_yaml_file
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations
from tests.integration.benchmark_runner.test_environment_variables import *

TESTED_WORKLOAD = 'stressng'


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
    This method deletes objects and YAML files if they exist
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    workload_name = f'{workload}-{kind}-workload'
    workload_yaml = f'{workload}_{kind}.yaml'
    if oc.pod_exists(pod_name=workload_name, namespace=test_environment_variable['namespace']):
        oc.delete_pod_sync(yaml=os.path.join(templates_path, workload_yaml), pod_name=workload_name)
    if os.path.isfile(os.path.join(templates_path, workload_yaml)):
        os.remove(os.path.join(templates_path, workload_yaml))


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method creates benchmark operator pod once for all tests
    :return:
    """
    print('Deploy benchmark-operator pod')
    benchmark_operator = BenchmarkOperatorWorkloadsOperations()
    benchmark_operator.get_oc(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    benchmark_operator.make_undeploy_benchmark_controller_manager_if_exist(runner_path=test_environment_variable['runner_path'])
    benchmark_operator.make_deploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])
    yield
    print('UnDeploy benchmark-operator pod')
    benchmark_operator.make_undeploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])


@pytest.fixture(autouse=True)
def before_after_each_test_fixture():
    """
    This method creates and deletes YAML files and test objects before and after each test
    :return:
    """
    # before all test: setup
    kinds = ('pod', 'vm')
    for kind in kinds:
        __generate_yamls(workload=TESTED_WORKLOAD, kind=kind)
    yield
    # After all tests
    for kind in kinds:
        __delete_test_objects(workload=TESTED_WORKLOAD, kind=kind)
    print('Test End')

###################################################### POD Tests ##################################################


def test_oc_get_pod_name_and_is_pod_exist():
    """
    This method tests get_pod_name and is_pod_exist
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc._get_pod_name(pod_name='benchmark-controller-manager', namespace=test_environment_variable['namespace'])
    assert oc.pod_exists(pod_name='benchmark-controller-manager', namespace=test_environment_variable['namespace'])


def test_yaml_file_not_exist_error():
    """
    This method creates pod with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with pytest.raises(YAMLNotExist) as err:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}1.yaml'), pod_name=f'{TESTED_WORKLOAD}-pod-workload', timeout=1)


def test_create_sync_pod_timeout_error():
    """
    This method creates pod with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with pytest.raises(PodNotCreateTimeout) as err:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_pod.yaml'), pod_name=f'{TESTED_WORKLOAD}-pod-workload', timeout=1)


def test_delete_sync_pod_timeout_error():
    """
    This method deletes pod with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_pod.yaml'), pod_name=f'{TESTED_WORKLOAD}-pod-workload')
    with pytest.raises(PodTerminateTimeout) as err:
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_pod.yaml'), pod_name=f'{TESTED_WORKLOAD}-pod-workload', timeout=1)


def test_get_long_short_uuid():
    """
    This method tests short and long uuid
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_pod.yaml'), pod_name=f'{TESTED_WORKLOAD}-pod-workload')
    assert len(oc.get_long_uuid(workload=f'{TESTED_WORKLOAD}-pod')) == 36
    assert len(oc._OC__get_short_uuid(workload=f'{TESTED_WORKLOAD}-pod')) == 8


@pytest.mark.skip(reason="Already verified in 'test_es_operations:test_verify_es_data_uploaded_stressng_pod' ")
def test_wait_for_pod_create_initialized_ready_completed_system_metrics_deleted():
    """
    This method tests wait for pod create, initialized, ready, completed, system-metrics, delete
    :return:
    """
    workload = f'{TESTED_WORKLOAD}-pod'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_pod.yaml'), pod_name=f'{workload}-workload')
    assert oc.wait_for_initialized(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    assert oc.wait_for_ready(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    assert oc.wait_for_pod_completed(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    # system-metrics
    assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
    assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
    assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
    assert oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_pod.yaml'), pod_name=f'{workload}-workload')


@pytest.mark.skip(reason="Disable kata")
def test_wait_for_kata_create_initialized_ready_completed_system_metrics_deleted():
    """
    This method tests wait for pod create, initialized, ready, completed, system-metrics, delete
    :return:
    """
    workload = f'{TESTED_WORKLOAD}-kata'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_kata.yaml'), pod_name=f'{workload}-workload')
    assert oc.wait_for_initialized(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    assert oc.wait_for_ready(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    assert oc.wait_for_pod_completed(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    # system-metrics
    assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
    assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
    assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
    assert oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_kata.yaml'), pod_name=f'{workload}-workload')

###################################################### VM Tests ##################################################


def test_create_sync_vm_timeout_error():
    """
    This method creates vm with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with pytest.raises(VMNotCreateTimeout) as err:
        oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_vm.yaml'), vm_name=f'{TESTED_WORKLOAD}-vm-workload', timeout=1)


@pytest.mark.skip(reason="Already verified in: test_vm_create_initialized_ready_completed_system_metrics_deleted ")
def test_oc_get_vm_name_and_is_vm_exist():
    """
    This method tests get_vm_name and is_vm_exist
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.create_async(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_vm.yaml'))
    # wait 60 sec till vm will be created
    time.sleep(60)
    assert oc._get_vm_name(vm_name=f'{TESTED_WORKLOAD}-vm-workload', namespace=test_environment_variable['namespace'])
    assert oc.vm_exists(vm_name=f'{TESTED_WORKLOAD}-vm-workload', namespace=test_environment_variable['namespace'])


@pytest.mark.skip(reason="Already verified in: test_vm_create_initialized_ready_completed_system_metrics_deleted ")
def test_wait_for_vm_created():
    """
    This method waits for vm to be created
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.create_async(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_vm.yaml'))
    assert oc.wait_for_vm_create(vm_name=f'{TESTED_WORKLOAD}-vm-workload')


def test_vm_create_initialized_ready_completed_system_metrics_deleted():
    """
    This method tests create, get_vm, initialize, ready, completed, system-metrics, deleted
    Must have running ElasticSearch server
    :return:
    """
    workload = f'{TESTED_WORKLOAD}-vm'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_vm.yaml'), vm_name=f'{workload}-workload')
    assert oc.get_vm()
    assert oc.wait_for_initialized(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    assert oc.wait_for_ready(label=f'app={TESTED_WORKLOAD}_workload', workload=workload)
    assert oc.wait_for_vm_completed(workload=workload)
    # system-metrics
    if test_environment_variable['system_metrics']:
        es = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''), es_port=test_environment_variable.get('elasticsearch_port', ''), es_user=test_environment_variable.get('elasticsearch_user', ''), es_password=test_environment_variable.get('elasticsearch_password', ''))
        assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
        assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
        assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
        assert es.verify_elasticsearch_data_uploaded(index='system-metrics-test', uuid=oc.get_long_uuid(workload=workload))
    if test_environment_variable['elasticsearch']:
        es = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''), es_port=test_environment_variable.get('elasticsearch_port', ''), es_user=test_environment_variable.get('elasticsearch_user', ''), es_password=test_environment_variable.get('elasticsearch_password', ''))
        assert es.verify_elasticsearch_data_uploaded(index=f'{TESTED_WORKLOAD}-vm-test-results', uuid=oc.get_long_uuid(workload=workload))
    assert oc.delete_vm_sync(yaml=os.path.join(f'{templates_path}', f'{TESTED_WORKLOAD}_vm.yaml'), vm_name=f'{workload}-workload')
