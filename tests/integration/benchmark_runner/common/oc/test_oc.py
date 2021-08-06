
import time
import pytest

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import PodNotCreateTimeout, PodTerminateTimeout, VMNotCreateTimeout, YAMLNotExist
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.main.update_data_template_yaml_with_environment_variables import delete_generate_file, update_environment_variable
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from tests.integration.benchmark_runner.test_environment_variables import *


def __generate_pod_yamls():
    """
    This method create pod yaml from template and inject environment variable inside
    :return:
    """
    update_environment_variable(dir_path=templates_path, yaml_file='stressng_pod_template.yaml', environment_variable_dict=test_environment_variable)


def __generate_vm_yamls():
    """
    This method create vm yaml from template and inject environment variable inside
    :return:
    """
    update_environment_variable(dir_path=templates_path, yaml_file='stressng_vm_template.yaml', environment_variable_dict=test_environment_variable)


def __delete_pod_yamls():
    """
    This method delete pod yamls if exist
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    if oc._is_pod_exist(pod_name='stressng-pod-workload', namespace=test_environment_variable['namespace']):
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    delete_generate_file(full_path_yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'))


def __delete_vm_yamls():
    """
    This method delete vm yamls if exist
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    if oc._is_vmi_exist(vm_name='stressng-vm-workload', namespace=test_environment_variable['namespace']):
        oc.delete_vm_sync(yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'), vm_name='stressng-vm-workload')
    delete_generate_file(full_path_yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'))


@pytest.fixture(scope="session", autouse=True)
def before_after_all_tests_fixture():
    """
    This method is create benchmark operator pod once for ALL tests
    :return:
    """
    print('Install benchmark-operator pod')
    benchmark_operator = BenchmarkOperatorWorkloads(kubeadmin_password=test_environment_variable['kubeadmin_password'],
                                                    es_host=test_environment_variable['elasticsearch'],
                                                    es_port=test_environment_variable['elasticsearch_port'])
    benchmark_operator.make_undeploy_benchmark_controller_manager_if_exist(runner_path=test_environment_variable['runner_path'])
    benchmark_operator.make_deploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])
    yield
    print('Delete benchmark-operator pod')
    benchmark_operator.make_undeploy_benchmark_controller_manager(runner_path=test_environment_variable['runner_path'])


@pytest.fixture(autouse=True)
def before_after_each_test_fixture():
    """
    This method is clearing yaml before and after EACH test
    :return:
    """
    # before all test: setup
    __generate_pod_yamls()
    __generate_vm_yamls()
    yield
    # After all tests
    __delete_pod_yamls()
    __delete_vm_yamls()
    print('Test End')


def test_login():
    """
    This method test login
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    # byte to string
    result = oc.login().decode("utf-8")
    assert 'Login successful' in result


###################################################### POD Tests ##################################################


def test_oc_get_pods():
    """
    This method test get pods
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_pods()


def test_oc_get_pods():
    """
    This test run oc get pods
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_pods()


def test_oc_get_pod_name():
    """
    This test run oc get pod by name
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc._get_pod_name(pod_name='wcwcwcwc', namespace=test_environment_variable['namespace']) == ''


def test_oc_get_pod_name_and_is_pod_exist():
    """
    This method test get_pod_name and is_pod_exist
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc._get_pod_name(pod_name='benchmark-controller-manager', namespace=test_environment_variable['namespace'])
    assert oc._is_pod_exist(pod_name='benchmark-controller-manager', namespace=test_environment_variable['namespace'])


def test_yaml_file_not_exist_error():
    """
    This method create pod with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    with pytest.raises(YAMLNotExist) as err:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng1.yaml'), pod_name='stressng-pod-workload', timeout=0)


def test_create_sync_pod_timeout_error():
    """
    This method create pod with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    with pytest.raises(PodNotCreateTimeout) as err:
        oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload', timeout=0)


def test_delete_sync_pod_timeout_error():
    """
    This method delete pod with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    with pytest.raises(PodTerminateTimeout) as err:
        oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload', timeout=0)


def test_get_long_short_uuid():
    """
    This method test short and long uuid
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    assert len(oc.get_long_uuid(workload='stressng-pod')) == 36
    assert len(oc._OC__get_short_uuid(workload='stressng-pod')) == 8


def test_wait_for_pod_create_initialized_ready_completed_system_metrics_deleted():
    """
    This method test wait for pod create, initialized, ready, completed, system-metrics, delete
    :return:
    """
    workload = 'stressng-pod'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.create_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')
    assert oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
    assert oc.wait_for_ready(label='app=stressng_workload', workload=workload)
    assert oc.wait_for_pod_completed(label='app=stressng_workload', workload=workload)
    time.sleep(30)
    # system-metrics
    assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
    assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
    assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
    assert oc.delete_pod_sync(yaml=os.path.join(f'{templates_path}', 'stressng_pod.yaml'), pod_name='stressng-pod-workload')


###################################################### VM Tests ##################################################


def test_create_sync_vm_timeout_error():
    """
    This method create vm with timeout error
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    with pytest.raises(VMNotCreateTimeout) as err:
        oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'), vm_name='stressng-vm-workload', timeout=0)


def test_oc_get_vmi_name_and_is_vmi_exist():
    """
    This method test get_vmi_name and is_vmi_exist
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    oc._create_async(yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'))
    # wait 120 sec till vm will be created
    time.sleep(120)
    assert oc._get_vmi_name(vm_name='stressng-vm-workload', namespace=test_environment_variable['namespace'])
    assert oc._is_vmi_exist(vm_name='stressng-vm-workload', namespace=test_environment_variable['namespace'])


def test_wait_for_vm_created():
    """
    This method wait for vm to be created
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    oc._create_async(yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'))
    assert oc.wait_for_vm_create(vm_name='stressng-vm-workload')


def test_vm_create_initialized_ready_completed_system_metrics_deleted():
    """
    This method test create, get_vmi, initialize, ready, completed, system-metrics, deleted
    Must have running ElasticSearch server
    :return:
    """
    workload = 'stressng-vm'
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.create_vm_sync(yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'), vm_name='stressng-vm-workload')
    assert oc.get_vmi()
    assert oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
    assert oc.wait_for_ready(label='app=stressng_workload', workload=workload)
    assert oc.wait_for_vm_completed(workload=workload)
    time.sleep(30)
    # system-metrics
    assert oc.wait_for_pod_create(pod_name='system-metrics-collector')
    assert oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
    assert oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
    if test_environment_variable['elasticsearch']:
        es = ESOperations(es_host=test_environment_variable['elasticsearch'],
                           es_port=test_environment_variable['elasticsearch_port'])
        assert es.verify_es_data_uploaded(index='stressng-vm-results', uuid=oc.get_long_uuid(workload=workload))
        assert es.verify_es_data_uploaded(index='system-metrics', uuid=oc.get_long_uuid(workload=workload))
    else:
        print('There is no elastic search to verify VM completed status')
    assert oc.delete_vm_sync(yaml=os.path.join(f'{templates_path}', 'stressng_vm.yaml'),
                             vm_name='stressng-vm-workload')
