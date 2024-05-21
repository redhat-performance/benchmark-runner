
import pytest
from benchmark_runner.common.clouds.Azure.azure_operations import AzureOperations
from tests.integration.benchmark_runner.test_environment_variables import *


#@pytest.mark.skip(reason="No Azure environment")
def test_get_vm_status():
    """
    This method tests fetch vm status from Azure cluster
    :return:
    """
    azure_operation = AzureOperations(azure_clientid=test_environment_variable.get('azure_clientid', ''),
                                      azure_secret=test_environment_variable.get('azure_secret', ''),
                                      azure_tenantid=test_environment_variable.get('azure_tenantid', ''),
                                      azure_subscriptionid=test_environment_variable.get('azure_subscriptionid', ''),
                                      azure_resource_group_name=test_environment_variable.get('azure_resource_group_name', ''),
                                      kubeadmin_password=test_environment_variable.get('kubeadmin_password', ''))
    # convert str list to list
    azure_vm_name = (test_environment_variable.get('azure_vm_name', ''))
    assert azure_operation.get_vm_status(vm_name=azure_vm_name)


@pytest.mark.skip(reason="Not run against test cluster")
def test_stop_azure_vm():
    """
    This method tests azure vm stop
    :return:
    """
    azure_operation = AzureOperations(azure_clientid=test_environment_variable.get('azure_clientid', ''),
                                      azure_secret=test_environment_variable.get('azure_secret', ''),
                                      azure_tenantid=test_environment_variable.get('azure_tenantid', ''),
                                      azure_subscriptionid=test_environment_variable.get('azure_subscriptionid', ''),
                                      azure_resource_group_name=test_environment_variable.get('azure_resource_group_name', ''),
                                      kubeadmin_password=test_environment_variable.get('kubeadmin_password', ''))
    # convert str list to list
    azure_vm_name = (test_environment_variable.get('azure_vm_name', ''))
    assert azure_operation.stop_vm(vm_name=azure_vm_name)


@pytest.mark.skip(reason="Not run against test cluster")
def test_start_azure_vm():
    """
    This method tests azure vm start
    :return:
    """
    azure_operation = AzureOperations(azure_clientid=test_environment_variable.get('azure_clientid', ''),
                                      azure_secret=test_environment_variable.get('azure_secret', ''),
                                      azure_tenantid=test_environment_variable.get('azure_tenantid', ''),
                                      azure_subscriptionid=test_environment_variable.get('azure_subscriptionid', ''),
                                      azure_resource_group_name=test_environment_variable.get('azure_resource_group_name', ''),
                                      kubeadmin_password=test_environment_variable.get('kubeadmin_password', ''))
    # convert str list to list
    azure_vm_name = (test_environment_variable.get('azure_vm_name', ''))
    assert azure_operation.start_vm(vm_name=azure_vm_name)


@pytest.mark.skip(reason="Not run against test cluster")
def test_start_cluster_with_verification():
    """
    This method tests azure cluster is up and running
    :return:
    """
    azure_operation = AzureOperations(azure_clientid=test_environment_variable.get('azure_clientid', ''),
                                      azure_secret=test_environment_variable.get('azure_secret', ''),
                                      azure_tenantid=test_environment_variable.get('azure_tenantid', ''),
                                      azure_subscriptionid=test_environment_variable.get('azure_subscriptionid', ''),
                                      azure_resource_group_name=test_environment_variable.get('azure_resource_group_name', ''),
                                      kubeadmin_password=test_environment_variable.get('kubeadmin_password', ''))
    # convert str list to list
    azure_vm_name = (test_environment_variable.get('azure_vm_name', ''))
    assert azure_operation.start_cluster_with_verification(vm_name=azure_vm_name)
