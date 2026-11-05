import pytest
from unittest.mock import MagicMock, patch
from benchmark_runner.common.oc.oc import OC
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
    yield
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
    mock_oc_instance.run.side_effect = Exception('Invalid kubeconfig')

    with pytest.raises(
        LoginFailed, match=('Empty KUBEADMIN_PASSWORD and '
                            'KUBECONFIG authentication failed.'),
    ):
        SingletonOCLogin(mock_oc_instance)  # Should raise LoginFailed


def test_login_with_whitespace_password(mock_oc_instance):
    """Test login when kubeadmin_password is whitespace."""
    mock_oc_instance._kubeadmin_password = '   '  # Set password to whitespace
    mock_oc_instance.run.side_effect = Exception('Invalid kubeconfig')
    with pytest.raises(
        LoginFailed, match=('Empty KUBEADMIN_PASSWORD and '
                            'KUBECONFIG authentication failed.'),
    ):
        singleton_login = SingletonOCLogin(mock_oc_instance)

    mock_oc_instance.run.assert_called_once_with('oc whoami', is_check=True)


@pytest.mark.parametrize('password', [None, '', '   '])
@pytest.mark.parametrize('identity', [
    ' kube:admin\n', ' system:admin\n',
    b' kube:admin\n', b' system:admin\n',
])
def test_oc_reuses_authenticated_context(password, identity):
    with patch.dict(
        'benchmark_runner.common.oc.oc.environment_variables.'
        'environment_variables_dict', {'kubeadmin_password': ''},
    ), patch.object(OC, 'run', return_value=identity) as run:
        oc_instance = OC(kubeadmin_password=password)

    assert isinstance(oc_instance, OC)
    assert SingletonOCLogin._instance is not None
    run.assert_called_once_with('oc whoami', is_check=True)


@pytest.mark.parametrize('response', [
    Exception('Invalid kubeconfig'), RuntimeError('CLI failed'), None,
    b'', b'\n', b'system:anonymous\n', 'system:anonymous\n',
    'test-user\n', b'test-user\n', 'kubeadmin', b'admin',
    'kube:admin-extra', b'system:admin-extra',
    'prefix-kube:admin', b'prefix-system:admin',
    'Kube:admin', b'System:admin',
    'kube:admin\nother-user', b'system:admin\nother-user',
])
def test_oc_rejects_unauthenticated_context(response):
    '''Reject invalid contexts while preserving command-error causes.'''
    with patch.dict(
        'benchmark_runner.common.oc.oc.environment_variables.'
        'environment_variables_dict', {'kubeadmin_password': ''},
    ), patch.object(OC, 'run') as run:
        if isinstance(response, Exception):
            run.side_effect = response
        else:
            run.return_value = response
        if isinstance(response, Exception) or response is None:
            message = ('Empty KUBEADMIN_PASSWORD and '
                       'KUBECONFIG authentication failed.')
        else:
            message = ('Empty KUBEADMIN_PASSWORD and KUBECONFIG identity '
                       'is not `kube:admin` or `system:admin`.')
        with pytest.raises(LoginFailed, match=message) as failure:
            OC()

    if isinstance(response, Exception):
        assert failure.value.__cause__ is response
    elif response is None:
        assert isinstance(failure.value.__cause__, AttributeError)
    else:
        assert failure.value.__cause__ is None
        assert failure.value.__context__ is None
    assert SingletonOCLogin._instance is None
    run.assert_called_once_with('oc whoami', is_check=True)


def test_oc_explicit_password_keeps_login_behavior():
    with patch.object(OC, 'run', return_value=b'Login successful') as run:
        oc_instance = OC(kubeadmin_password='explicit-password')

    assert isinstance(oc_instance, OC)
    run.assert_called_once_with(
        'oc login -u kubeadmin -p explicit-password', is_check=True,
    )


def test_failed_password_does_not_reuse_context(mock_oc_instance):
    '''Retry password login without caching failed initialization.'''
    mock_oc_instance.run.side_effect = Exception('Login error')
    with patch('benchmark_runner.common.oc.singleton_oc_login.time.sleep'):
        with pytest.raises(
            LoginFailed, match='Login failed after multiple attempts',
        ):
            SingletonOCLogin(mock_oc_instance)

    assert SingletonOCLogin._instance is None
    assert mock_oc_instance.run.call_count == mock_oc_instance.RETRIES
    for call in mock_oc_instance.run.call_args_list:
        assert call.args == ('oc login -u kubeadmin -p valid_password',)
        assert call.kwargs == {'is_check': True}


def test_failed_context_is_revalidated(mock_oc_instance):
    mock_oc_instance._kubeadmin_password = ''
    mock_oc_instance.run.side_effect = [
        RuntimeError('Invalid kubeconfig'), b'system:admin\n',
    ]
    with pytest.raises(LoginFailed):
        SingletonOCLogin(mock_oc_instance)

    login = SingletonOCLogin(mock_oc_instance)
    assert SingletonOCLogin._instance is login
    assert mock_oc_instance.run.call_count == 2
    mock_oc_instance.run.assert_called_with('oc whoami', is_check=True)
