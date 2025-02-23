# Tests that are not required benchmark-operator pod

import time
import tempfile
import tarfile
import mock
import pytest

from benchmark_runner.common.oc.oc import OC
from tests.integration.benchmark_runner.test_environment_variables import *
from benchmark_runner.common.prometheus.prometheus_snapshot import PrometheusSnapshot


def test_oc_get_ocp_server_version():
    """
    This method gets ocp server version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_ocp_server_version()


def test_get_ocp_major_version():
    """
    This method gets ocp major version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_ocp_major_version()


def test_get_ocp_minor_version():
    """
    This method gets ocp minor version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_ocp_minor_version()


@pytest.mark.skip(reason="Disable kata")
def test_oc_get_kata_operator_version():
    """
    This method gets the sandboxed containers (kata) operator version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_kata_operator_version()


@pytest.mark.skip(reason="Disable kata")
def test_oc_get_kata_rpm_version():
    """
    This method gets the sandboxed containers (kata) rpm version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_kata_rpm_version(node=test_environment_variable['pin_node1'])
    assert len(oc.get_kata_rpm_version(node=test_environment_variable['pin_node1']).split('.')) == 3


def test_oc_get_cnv_version():
    """
    This method get cnv version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_cnv_version()


@pytest.mark.skip(reason="Disable ODF")
def test_oc_get_odf_version():
    """
    This method get odf version
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_odf_version()


@pytest.mark.skip(reason="Disable ODF")
def test_oc_get_pv_disk_ids():
    """
    This method test get pv disk ids
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert len(oc.get_pv_disk_ids()) > 1
    assert oc.get_pv_disk_ids()


def mock_get_worker_disk_ids(*args, **kwargs):
    """
    This method mock method class get_worker_disk_ids
    """
    return ['scsi-3600062b33333333333333333333333333']


def test_oc_get_free_disk_id():
    """
    This method gets free_disk_id string
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with mock.patch.object(OC, 'get_worker_disk_ids', new=mock_get_worker_disk_ids):
        assert oc.get_free_disk_id(node=test_environment_variable['pin_node1'])


@pytest.mark.skip(reason="Disable ODF")
def test_oc_get_odf_disk_count():
    """
    This method gets odf disk count
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    odf_disk_count = oc.get_odf_disk_count()
    assert (odf_disk_count is None or odf_disk_count > 0)


def test_oc_get_master_nodes():
    """
    This method test get master nodes
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.get_master_nodes()


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
    assert oc.get_prom_token()


def test_is_cnv_installed():
    """
    This method check if cnv operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.is_cnv_installed()


@pytest.mark.skip(reason="Disable kata")
def test_is_kata_installed():
    """
    This method checks if the sandboxed containers (kata) operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.is_kata_installed()


@pytest.mark.skip(reason="Disable ODF")
def test_is_odf_installed():
    """
    This method check if odf operator is installed
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.is_odf_installed()


def test_oc_exec():
    """
    Test that oc exec works
    :return:
    """
    test_message = "I am here"
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    answer = oc.exec(pod_name="prometheus-k8s-0", namespace="openshift-monitoring", container='prometheus',
                     command=f'echo "{test_message}"')
    assert answer == test_message


def test_collect_prometheus():
    """
    Test that Prometheus data can be collected.  TBD test that data is valid.
    :return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    with tempfile.TemporaryDirectory() as dirname:
        snapshot = PrometheusSnapshot(oc=oc, artifacts_path=dirname, verbose=True)
        snapshot.prepare_for_snapshot(pre_wait_time=1)
        time.sleep(10)
        tarball = snapshot.retrieve_snapshot(post_wait_time=1)
        assert tarfile.is_tarfile(tarball)


def test_wait_for_nodes_ready():
    """
    This method waits till nodes are ready
    @return:
    """
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    assert oc.wait_for_node_ready()
