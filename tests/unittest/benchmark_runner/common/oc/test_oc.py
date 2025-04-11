
import mock
import pytest
from unittest.mock import patch

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import YAMLNotExist, LoginFailed, NodeNotReady


@patch('benchmark_runner.common.oc.oc.SingletonOCLogin')  # patching login
def test_create_async_pod_yaml_not_exist(mock_login):
    oc = OC(kubeadmin_password="dummy-password")
    with patch("os.path.exists", return_value=False):
        with pytest.raises(YAMLNotExist):
            oc.create_async(yaml='stressng1.yaml')


# Dummy UUID for testing
def dummy_long_uuid(self, workload):
    return 'bb2be20e-e4e8-57ed-a7c0-efde559b1ce2'


@mock.patch('benchmark_runner.common.oc.oc.SingletonOCLogin')  # Prevent login
def test_short_uuid(mock_login):
    """
    This method tests parsing a long UUID into a short UUID
    """
    with mock.patch.object(OC, 'get_long_uuid', new=dummy_long_uuid):
        oc = OC(kubeadmin_password="dummy-password")  # Avoid LoginFailed
        short_uuid = oc._OC__get_short_uuid(workload='stressng_pod')
        assert short_uuid == 'bb2be20e'


@patch('benchmark_runner.common.oc.oc.SingletonOCLogin')  # patch login
def test_check_all_nodes_status_ready(mock_login):
    oc = OC(kubeadmin_password="dummy-password")  # prevent LoginFailed

    with patch.object(OC, 'get_node_status', return_value=['node-0 Ready', 'node-1 Ready', 'node-2 Ready']):
        result = oc.wait_for_node_ready()
        assert result


@patch('benchmark_runner.common.oc.oc.SingletonOCLogin')
def test_check_all_nodes_status_not_ready(mock_login):
    oc = OC(kubeadmin_password="dummy-password")
    with pytest.raises(NodeNotReady) as exc_info:
        with patch.object(OC, 'get_node_status', return_value=[
            'node-0 NotReady', 'node-1 NotReady', 'node-2 Ready'
        ]):
            oc.wait_for_node_ready(wait_time=1, timeout=1)  # fast exit
    assert str(exc_info.value) == "Node not ready: {'node-0': 'NotReady', 'node-1': 'NotReady'}"


@patch('benchmark_runner.common.oc.oc.SingletonOCLogin')
def test_check_not_ready_node_status_not_ready(mock_login):
    oc = OC(kubeadmin_password="dummy-password")
    with pytest.raises(NodeNotReady) as exc_info:
        with patch.object(OC, 'get_node_status', return_value=[
            'node-0 NotReady', 'node-1 NotReady', 'node-2 Ready'
        ]):
            oc.wait_for_node_ready(node='node-1', wait_time=1, timeout=1)
    assert str(exc_info.value) == "Node not ready: {'node-1': 'NotReady'}"


@patch('benchmark_runner.common.oc.oc.SingletonOCLogin')
def test_check_ready_node_status_not_ready(mock_login):
    oc = OC(kubeadmin_password="dummy-password")
    with patch.object(OC, 'get_node_status', return_value=[
        'node-0 NotReady', 'node-1 NotReady', 'node-2 Ready'
    ]):
        result = oc.wait_for_node_ready(node='node-2', wait_time=1, timeout=1)
        assert result
