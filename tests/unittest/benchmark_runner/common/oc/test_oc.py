
import mock
import pytest
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import YAMLNotExist, LoginFailed, NodeNotReady


def test_bad_login():
    """
    This method tests that login fails with a guaranteed bad kubeadmin password
    :return:
    """
    oc = OC(kubeadmin_password='BAD-PASSWORD')
    with pytest.raises(LoginFailed) as err:
        assert not oc.login()


def test_empty_kubeadmin_password():
    """
    This method test empty kubeadmin password
    :return:
    """
    oc = OC(kubeadmin_password='')
    assert oc.login()


def test_create_async_pod_yaml_not_exist():
    """
    This method create pod from not exist yaml
    :return:
    """
    oc = OC()
    with pytest.raises(YAMLNotExist) as err:
        oc.create_async(yaml=f'stressng1.yaml')


def dummy_long_uuid(cls, *args, **kwargs):
    # Your custom testing override
    return 'bb2be20e-e4e8-57ed-a7c0-efde559b1ce2'


def test_short_uuid():
    """
    This method test parsing long uuid
    """

    with mock.patch.object(OC, 'get_long_uuid', new=dummy_long_uuid):
        oc = OC()
        assert oc._OC__get_short_uuid(workload='stressng_pod') == 'bb2be20e'


def test_check_node_status_ready():
    oc = OC()
    result = oc.check_node_status(nodes_list=['node-0 Ready', 'node-1 Ready', 'node-2 Ready'])
    assert result


def test_check_node_status_not_ready():
    oc = OC()
    with pytest.raises(NodeNotReady) as exc_info:
        oc.check_node_status(nodes_list=['node-0 Ready', 'node-1 NotReady', 'node-2 Ready'])
    # Check that the exception message is as expected
    assert str(exc_info.value) == "Node node-1 is not ready. Current status: NotReady"
