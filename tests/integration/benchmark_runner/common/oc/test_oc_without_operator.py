
# Tests that are not required benchmark-operator pod

from benchmark_runner.common.oc.oc import OC
from tests.integration.benchmark_runner.test_environment_variables import *


def test_oc_get_ocp_server_version():
    """
    This method get ocp server version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_ocp_server_version()


def test_oc_get_cnv_version():
    """
    This method get cnv version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_cnv_version()


def test_oc_get_ocs_version():
    """
    This method get ocs version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_ocs_version()


def test_oc_get_master_nodes():
    """
    This method test get master nodes
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_master_nodes()


def test_login():
    """
    This method test login
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.login()


def test_oc_get_pod_name():
    """
    This test run oc get pod by name
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc._get_pod_name(pod_name='erererer', namespace=test_environment_variable['namespace']) == ''


def test_oc_get_pods():
    """
    This test run oc get pods
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_pods()


def test_get_prom_token():
    """
    This method return prom token from cluster
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_prom_token()


def test_is_cnv_installed():
    """
    This method check if cnv operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.is_cnv_installed()


def test_is_ocs_installed():
    """
    This method check if ocs operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.is_ocs_installed()


def test_is_kata_installed():
    """
    This method check if kata operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.is_kata_installed()