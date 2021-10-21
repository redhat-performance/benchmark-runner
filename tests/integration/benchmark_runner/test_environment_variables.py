
import os


def __get_test_environment_variable():
    """
    This method generate environment variable for test
    """
    test_environment_variable = {}

    ##################################################################################################
    # dynamic parameters - configure for local run
    test_environment_variable['runner_path'] = os.environ.get('RUNNER_PATH', '/')
    test_environment_variable['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')
    # Node Selector
    test_environment_variable['pin_node1'] = os.environ.get('PIN_NODE1', '')
    # ElasticSearch
    test_environment_variable['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
    test_environment_variable['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')

    # end dynamic parameters - configure for local run
    ##################################################################################################

    # ** DO NOT CHANGE THE PARAMETERS BELOW **
    # Constant parameters
    test_environment_variable['namespace'] = os.environ.get('NAMESPACE', 'benchmark-operator')
    # run Hammerdb workload with ocs pvc
    test_environment_variable['ocs_pvc'] = os.environ.get('OCS_PVC', 'True')
    test_environment_variable['system_metrics'] = os.environ.get('SYSTEM_METRICS', 'True')

    # Azure details
    test_environment_variable['azure_cluster_stop'] = os.environ.get('AZURE_CLUSTER_STOP', '')
    test_environment_variable['azure_cluster_start'] = os.environ.get('AZURE_CLUSTER_START', '')
    test_environment_variable['azure_clientid'] = os.environ.get('AZURE_CLIENTID', '')
    test_environment_variable['azure_secret'] = os.environ.get('AZURE_SECRET', '')
    test_environment_variable['azure_tenantid'] = os.environ.get('AZURE_TENANTID', '')
    test_environment_variable['azure_subscriptionid'] = os.environ.get('AZURE_SUBSCRIPTIONID', '')
    test_environment_variable['azure_resource_group_name'] = os.environ.get('AZURE_RESOURCE_GROUP_NAME', '')
    test_environment_variable['azure_vm_name'] = os.environ.get('AZURE_VM_NAME', '')

    # update node_selector
    if test_environment_variable['pin_node1']:
        test_environment_variable['pin'] = 'true'
    else:
        test_environment_variable['pin'] = 'false'

    # ElasticSearch functionality
    if test_environment_variable['elasticsearch'] and test_environment_variable['elasticsearch_port']:
        test_environment_variable[
            'elasticsearch_url'] = f"{test_environment_variable['elasticsearch']}:{test_environment_variable['elasticsearch_port']}"
    else:
        test_environment_variable['elasticsearch_url'] = ''
    return test_environment_variable


# Global path parameters
dir_path = os.path.dirname(os.path.realpath(__file__))
templates_path = os.path.join(dir_path, 'templates')
test_environment_variable = __get_test_environment_variable()
