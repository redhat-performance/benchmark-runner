
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.singleton_oc_login import SingletonOCLogin  # Adjust import as necessary
from tests.integration.benchmark_runner.test_environment_variables import *


def test_login_success():
    """Test successful login."""
    oc = OC(kubeadmin_password=test_environment_variable['kubeadmin_password'])
    singleton_login = SingletonOCLogin(oc)
    assert singleton_login._login() is True
