
import ast  # convert str list to list
from benchmark_runner.common.clouds.Azure.azure_operations import AzureOperations
from tests.integration.benchmark_runner.test_environment_variables import *


def test_get_vm_status():
    """
    This method test fetch vm status from Azure cluster
    :return:
    """
    azure_operation = AzureOperations(azure_clientid=test_environment_variable.get('azure_clientid', ''),
                                      azure_secret=test_environment_variable.get('azure_secret', ''),
                                      azure_tenantid=test_environment_variable.get('azure_tenantid', ''),
                                      azure_subscriptionid=test_environment_variable.get('azure_subscriptionid', ''),
                                      azure_resource_group_name=test_environment_variable.get(
                                          'azure_resource_group_name', ''))
    # convert str list to list
    azure_vm_name = (test_environment_variable.get('azure_vm_name', ''))
    assert azure_operation.get_vm_status(vm_name=azure_vm_name)

