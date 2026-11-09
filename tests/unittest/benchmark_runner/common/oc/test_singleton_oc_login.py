import pytest
from unittest.mock import MagicMock, call, patch
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import LoginFailed
from benchmark_runner.common.oc.singleton_oc_login import SingletonOCLogin  # Adjust import as necessary

WHOAMI_COMMAND = 'oc auth whoami -ojsonpath=\'{.status.userInfo.username}{"\\n"}\''


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


@pytest.fixture
def mock_sleep():
    '''Patch login retry delays so retry tests do not wait.'''
    with patch('benchmark_runner.common.oc.singleton_oc_login.time.sleep') as sleep:
        yield sleep


def test_login_success(mock_oc_instance):
    """Test successful login."""
    singleton_login = SingletonOCLogin(mock_oc_instance)

    # Mock the run method to simulate a successful login
    mock_oc_instance.run = MagicMock(return_value=True)

    assert singleton_login._login() is True
    mock_oc_instance.run.assert_called_once_with('oc login -u kubeadmin -p valid_password', is_check=True)


def test_login_failure(mock_oc_instance, mock_sleep):
    """Test login failure after all attempts."""
    singleton_login = SingletonOCLogin(mock_oc_instance)

    # Mock the run method to raise an exception
    mock_oc_instance.run = MagicMock(side_effect=Exception("Login error"))

    with pytest.raises(LoginFailed, match="Login failed after multiple attempts"):
        singleton_login._login()

    assert mock_oc_instance.run.call_count == mock_oc_instance.RETRIES


def test_login_partial_success(mock_oc_instance, mock_sleep):
    """Test login attempts with the first attempt failing and the second succeeding."""
    singleton_login = SingletonOCLogin(mock_oc_instance)

    # Simulate the first attempt failing and the second succeeding
    mock_oc_instance.run = MagicMock(side_effect=[Exception("Login error"), True])

    assert singleton_login._login() is True
    assert mock_oc_instance.run.call_count == 2


def test_login_with_no_password(mock_oc_instance, mock_sleep):
    """Test KUBECONFIG validation retries when kubeadmin_password is empty."""
    mock_oc_instance._kubeadmin_password = ''  # Set password to empty
    error = Exception('Invalid kubeconfig')
    mock_oc_instance.run.side_effect = error

    with pytest.raises(
        LoginFailed, match=('Empty KUBEADMIN_PASSWORD and '
                            'KUBECONFIG authentication failed.'),
    ) as failure:
        SingletonOCLogin(mock_oc_instance)  # Should raise LoginFailed

    assert failure.value.__cause__ is error
    assert SingletonOCLogin._instance is None
    assert mock_oc_instance.run.call_args_list == (
        [call(WHOAMI_COMMAND, is_check=True)] * mock_oc_instance.RETRIES
    )
    assert mock_sleep.call_args_list == (
        [call(mock_oc_instance.DELAY)] * (mock_oc_instance.RETRIES - 1)
    )


def test_login_with_whitespace_password(mock_oc_instance, mock_sleep):
    """Test KUBECONFIG validation retries when kubeadmin_password is whitespace."""
    mock_oc_instance._kubeadmin_password = '   '  # Set password to whitespace
    error = Exception('Invalid kubeconfig')
    mock_oc_instance.run.side_effect = error
    with pytest.raises(
        LoginFailed, match=('Empty KUBEADMIN_PASSWORD and '
                            'KUBECONFIG authentication failed.'),
    ) as failure:
        SingletonOCLogin(mock_oc_instance)

    assert failure.value.__cause__ is error
    assert SingletonOCLogin._instance is None
    assert mock_oc_instance.run.call_args_list == (
        [call(WHOAMI_COMMAND, is_check=True)] * mock_oc_instance.RETRIES
    )
    assert mock_sleep.call_args_list == (
        [call(mock_oc_instance.DELAY)] * (mock_oc_instance.RETRIES - 1)
    )


@pytest.mark.parametrize('password', ['', '   '])
@pytest.mark.parametrize('identity', ['kube:admin\n', b'system:admin\n'])
def test_context_retry_succeeds_during_initialization(
        mock_oc_instance, mock_sleep, password, identity):
    '''Retry a failed KUBECONFIG check within one initialization.'''
    mock_oc_instance._kubeadmin_password = password
    mock_oc_instance.run.side_effect = [
        RuntimeError('API server unavailable'), identity,
    ]

    login = SingletonOCLogin(mock_oc_instance)

    assert SingletonOCLogin._instance is login
    assert mock_oc_instance.run.call_args_list == (
        [call(WHOAMI_COMMAND, is_check=True)] * 2
    )
    mock_sleep.assert_called_once_with(mock_oc_instance.DELAY)


@pytest.mark.parametrize('password', [None, '', '   '])
@pytest.mark.parametrize('identity', [
    ' kube:admin\n', ' system:admin\n',
    b' kube:admin\n', b' system:admin\n',
])
def test_oc_reuses_authenticated_context(password, identity):
    with patch.dict(
        'benchmark_runner.common.oc.oc.environment_variables.'
        'environment_variables_dict', {'cli': 'oc', 'kubeadmin_password': ''},
    ), patch.object(OC, 'run', return_value=identity) as run:
        oc_instance = OC(kubeadmin_password=password)

    assert isinstance(oc_instance, OC)
    assert SingletonOCLogin._instance is not None
    run.assert_called_once_with(WHOAMI_COMMAND, is_check=True)


@pytest.mark.parametrize('password', ['', '   '])
@pytest.mark.parametrize('identity', [
    '', b'', '\n', b'\n', b'system:anonymous\n', 'system:anonymous\n',
    'test-user\n', b'test-user\n', 'kubeadmin', b'admin',
    'kube:admin-extra', b'system:admin-extra',
    'prefix-kube:admin', b'prefix-system:admin',
    'Kube:admin', b'System:admin',
    'kube:admin\nother-user', b'system:admin\nother-user',
])
def test_oc_rejects_unauthenticated_context(password, identity, mock_sleep):
    '''Reject a non-admin KUBECONFIG identity without retrying.'''
    with patch.dict(
        'benchmark_runner.common.oc.oc.environment_variables.'
        'environment_variables_dict', {'cli': 'oc', 'kubeadmin_password': ''},
    ), patch.object(OC, 'run', return_value=identity) as run:
        with pytest.raises(LoginFailed) as failure:
            OC(kubeadmin_password=password)

    normalized = (
        identity.decode('utf-8') if isinstance(identity, bytes) else identity
    ).strip()
    assert str(failure.value) == (
        f'Empty KUBEADMIN_PASSWORD and KUBECONFIG identity {normalized!r} '
        'is not `kube:admin` or `system:admin`.'
    )
    assert '\n' not in str(failure.value)
    assert failure.value.__cause__ is None
    assert failure.value.__context__ is None
    assert SingletonOCLogin._instance is None
    run.assert_called_once_with(WHOAMI_COMMAND, is_check=True)
    mock_sleep.assert_not_called()


@pytest.mark.parametrize('response', [
    Exception('Invalid kubeconfig'), RuntimeError('CLI failed'), None,
    b'\xff\n',
])
def test_oc_retries_failed_context_command(response, mock_sleep):
    '''Retry KUBECONFIG command errors while preserving the error cause.'''
    with patch.dict(
        'benchmark_runner.common.oc.oc.environment_variables.'
        'environment_variables_dict', {'cli': 'oc', 'kubeadmin_password': ''},
    ), patch.object(OC, 'run') as run:
        if isinstance(response, Exception):
            run.side_effect = response
        else:
            run.return_value = response
        with pytest.raises(
            LoginFailed, match=('Empty KUBEADMIN_PASSWORD and '
                                'KUBECONFIG authentication failed.'),
        ) as failure:
            OC()

    if response is None:
        assert isinstance(failure.value.__cause__, AttributeError)
    elif isinstance(response, bytes):
        assert isinstance(failure.value.__cause__, UnicodeDecodeError)
    else:
        assert failure.value.__cause__ is response
    assert SingletonOCLogin._instance is None
    assert run.call_args_list == (
        [call(WHOAMI_COMMAND, is_check=True)] * OC.RETRIES
    )
    assert mock_sleep.call_args_list == [call(OC.DELAY)] * (OC.RETRIES - 1)


def test_oc_explicit_password_keeps_login_behavior():
    with patch.dict(
        'benchmark_runner.common.oc.oc.environment_variables.'
        'environment_variables_dict', {'cli': 'oc'},
    ), patch.object(OC, 'run', return_value=b'Login successful') as run:
        oc_instance = OC(kubeadmin_password='explicit-password')

    assert isinstance(oc_instance, OC)
    run.assert_called_once_with(
        'oc login -u kubeadmin -p explicit-password', is_check=True,
    )


def test_failed_password_does_not_reuse_context(mock_oc_instance, mock_sleep):
    '''Retry password login without caching failed initialization.'''
    error = Exception('Login error')
    mock_oc_instance.run.side_effect = error
    with pytest.raises(
        LoginFailed, match='Login failed after multiple attempts',
    ) as failure:
        SingletonOCLogin(mock_oc_instance)

    assert failure.value.__cause__ is error
    assert SingletonOCLogin._instance is None
    assert mock_oc_instance.run.call_args_list == (
        [call('oc login -u kubeadmin -p valid_password', is_check=True)]
        * mock_oc_instance.RETRIES
    )
    assert mock_sleep.call_args_list == (
        [call(mock_oc_instance.DELAY)] * (mock_oc_instance.RETRIES - 1)
    )


def test_failed_context_is_revalidated(mock_oc_instance, mock_sleep):
    '''Revalidate KUBECONFIG after an exhausted initialization.'''
    mock_oc_instance._kubeadmin_password = ''
    mock_oc_instance.run.side_effect = (
        [RuntimeError('Invalid kubeconfig')] * mock_oc_instance.RETRIES
        + [b'system:admin\n']
    )
    with pytest.raises(
        LoginFailed, match=('Empty KUBEADMIN_PASSWORD and '
                            'KUBECONFIG authentication failed.'),
    ):
        SingletonOCLogin(mock_oc_instance)
    assert SingletonOCLogin._instance is None

    login = SingletonOCLogin(mock_oc_instance)
    assert SingletonOCLogin._instance is login
    assert SingletonOCLogin(mock_oc_instance) is login
    assert mock_oc_instance.run.call_args_list == (
        [call(WHOAMI_COMMAND, is_check=True)]
        * (mock_oc_instance.RETRIES + 1)
    )
    assert mock_sleep.call_args_list == (
        [call(mock_oc_instance.DELAY)] * (mock_oc_instance.RETRIES - 1)
    )
