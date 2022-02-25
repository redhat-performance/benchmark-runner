
# Tests that are not required benchmark-operator pod

import time
import tempfile
import tarfile
from benchmark_runner.common.oc.oc import OC
from tests.integration.benchmark_runner.test_environment_variables import *
from benchmark_runner.common.prometheus.prometheus_snapshot import PrometheusSnapshot


def test_oc_get_ocp_server_version():
    """
    This method get ocp server version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    print(oc.get_ocp_server_version())


def test_oc_get_kata_version():
    """
    This method gets the sandboxed containers (kata) version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_kata_version()


def test_oc_get_cnv_version():
    """
    This method get cnv version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.get_cnv_version()


def test_oc_get_odf_version():
    """
    This method get odf version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    oc.get_odf_version()


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


def test_is_kata_installed():
    """
    This method checks if the sandboxed containers (kata) operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.is_kata_installed()


def test_is_odf_installed():
    """
    This method check if odf operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.is_odf_installed()


def test_is_kata_installed():
    """
    This method check if kata operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    assert oc.is_kata_installed()


def test_oc_exec():
    """
    Test that oc exec works
    :return:
    """
    test_message = "I am here"
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    answer = oc.exec(pod_name="prometheus-k8s-0", namespace="openshift-monitoring", container='prometheus', command=f'echo "{test_message}"')
    assert answer == test_message


def test_collect_prometheus():
    """
    Test that Prometheus data can be collected.  TBD test that data is valid.
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    oc.login()
    with tempfile.TemporaryDirectory() as dirname:
        snapshot = PrometheusSnapshot(oc=oc, artifacts_path=dirname, verbose=True)
        snapshot.prepare_for_snapshot(pre_wait_time=1)
        time.sleep(10)
        tarball = snapshot.retrieve_snapshot(post_wait_time=1)
        assert tarfile.is_tarfile(tarball)
