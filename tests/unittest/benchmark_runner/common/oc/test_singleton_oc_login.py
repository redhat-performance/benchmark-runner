import pytest
from unittest.mock import MagicMock, patch
from benchmark_runner.common.oc.oc_exceptions import LoginFailed
from benchmark_runner.common.oc.singleton_oc_login import SingletonOCLogin  # Adjust import as necessary


@pytest.fixture
def mock_oc_instance():
    """Fixture to create a mocked OC instance."""
    oc_instance = MagicMock()
    oc_instance._kubeconfig_path = 'path/to/kubeconfig.yaml'
    oc_instance._kubeadmin_password = 'valid_password'
    oc_instance._cli = 'oc'
    oc_instance.RETRIES = 3
    oc_instance.DELAY = 1
    return oc_instance


@pytest.fixture(autouse=True)
def reset_singleton():
    """Fixture to reset SingletonOCLogin before each test."""
    with SingletonOCLogin._lock:
        SingletonOCLogin._instance = None


def test_login_success(mock_oc_instance):
    """Test successful login."""
    singleton_login = SingletonOCLogin(mock_oc_instance)

    # Mock the run method to simulate a successful login
    mock_oc_instance.run = MagicMock(return_value=True)

    assert singleton_login._login() is True
    mock_oc_instance.run.assert_called_once_with('oc login -u kubeadmin -p valid_password', is_check=True)


def test_login_failure(mock_oc_instance):
    """Test login failure after all attempts."""
    singleton_login = SingletonOCLogin(mock_oc_instance)

    # Mock the run method to raise an exception
    mock_oc_instance.run = MagicMock(side_effect=Exception("Login error"))

    with pytest.raises(LoginFailed, match="Login failed after multiple attempts"):
        singleton_login._login()

    assert mock_oc_instance.run.call_count == mock_oc_instance.RETRIES


def test_login_partial_success(mock_oc_instance):
    """Test login attempts with the first attempt failing and the second succeeding."""
    singleton_login = SingletonOCLogin(mock_oc_instance)

    # Simulate the first attempt failing and the second succeeding
    mock_oc_instance.run = MagicMock(side_effect=[Exception("Login error"), True])

    assert singleton_login._login() is True
    assert mock_oc_instance.run.call_count == 2


def test_login_with_no_password(mock_oc_instance):
    """Test login when kubeadmin_password is empty."""
    mock_oc_instance._kubeadmin_password = ''  # Set password to empty

    with pytest.raises(LoginFailed, match="Empty password"):
        SingletonOCLogin(mock_oc_instance)  # Should raise LoginFailed


def test_login_with_whitespace_password(mock_oc_instance):
    """Test login when kubeadmin_password is whitespace."""
    mock_oc_instance._kubeadmin_password = '   '  # Set password to whitespace
    with pytest.raises(LoginFailed, match="Empty password"):
        singleton_login = SingletonOCLogin(mock_oc_instance)

    assert mock_oc_instance.run.call_count == 0  # Ensure run was never called
