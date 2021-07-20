
import mock
import pytest
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import YAMLNotExist, LoginFailed


def test_oc_get_pods():
    """
    This test run oc get pods
    :return:
    """
    oc = OC()
    assert oc.get_pods()


def test_oc_get_pod_name():
    """
    This test run oc get pod by name
    :return:
    """
    oc = OC()
    assert oc._get_pod_name(pod_name='wcwcwcwc', namespace='my-ripsaw') == ''


def test_incorrect_kubeadmin_password():
    """
    This method test incorrect kubeadmin password
    :return:
    """
    oc = OC(kubeadmin_password='')
    with pytest.raises(LoginFailed) as err:
        oc.login()


def test_create_async_pod_yaml_not_exist():
    """
    This method create pod from not exist yaml
    :return:
    """
    oc = OC()
    with pytest.raises(YAMLNotExist) as err:
        oc._create_async(yaml=f'stressng1.yaml')


def dummy_long_uuid(cls, *args, **kwargs):
    # Your custom testing override
    return 'bb2be20e-e4e8-57ed-a7c0-efde559b1ce2'


def test_short_uuid():
    """
    This method test parsing long uuid
    """

    with mock.patch.object(OC, 'get_long_uuid', new=dummy_long_uuid):
        oc = OC()
        assert oc._OC__get_short_uuid() == 'bb2be20e'