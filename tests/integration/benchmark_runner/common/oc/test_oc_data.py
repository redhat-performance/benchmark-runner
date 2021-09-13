
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
