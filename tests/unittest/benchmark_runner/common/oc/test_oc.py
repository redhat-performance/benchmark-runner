
import mock
import pytest
from unittest.mock import patch

from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import YAMLNotExist, LoginFailed, NodeNotReady


def test_create_async_pod_yaml_not_exist():
    """
    This method create pod from not exist yaml
    :return:
    """
    oc = OC()
    with pytest.raises(YAMLNotExist):
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


def test_check_all_nodes_status_ready():
    oc = OC()
    with patch.object(OC, 'get_node_status', return_value=['node-0 Ready', 'node-1 Ready', 'node-2 Ready']):
        result = oc.wait_for_node_ready()
        assert result


def test_check_all_nodes_status_not_ready():
    oc = OC()
    with pytest.raises(NodeNotReady) as exc_info:
        with patch.object(OC, 'get_node_status', return_value=['node-0 NotReady', 'node-1 NotReady', 'node-2 Ready']):
            oc.wait_for_node_ready(wait_time=3, timeout=10)
    # Check that the exception message is as expected
    assert str(exc_info.value) == "Node not ready: {'node-0': 'NotReady', 'node-1': 'NotReady'}"


def test_check_not_ready_node_status_not_ready():
    oc = OC()
    with pytest.raises(NodeNotReady) as exc_info:
        with patch.object(OC, 'get_node_status', return_value=['node-0 NotReady', 'node-1 NotReady', 'node-2 Ready']):
            oc.wait_for_node_ready(node='node-1', wait_time=3, timeout=10)
    # Check that the exception message is as expected
    assert str(exc_info.value) == "Node not ready: {'node-1': 'NotReady'}"


def test_check_ready_node_status_not_ready():
    oc = OC()
    with patch.object(OC, 'get_node_status', return_value=['node-0 NotReady', 'node-1 NotReady', 'node-2 Ready']):
        result = oc.wait_for_node_ready(node='node-2', wait_time=3, timeout=10)
        assert result
