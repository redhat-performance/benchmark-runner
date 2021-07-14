
import pytest
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import YAMLNotExist


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
    assert oc._get_pod_name(pod_name='###', namespace='my-ripsaw') == ''


def test_create_async_pod_yaml_not_exist():
    """
    This method create pod from not exist yaml
    :return:
    """
    oc = OC()
    with pytest.raises(YAMLNotExist) as err:
        oc._create_async(yaml=f'stressng1.yaml')




