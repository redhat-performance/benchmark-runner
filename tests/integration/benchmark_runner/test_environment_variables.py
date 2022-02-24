
import os
import datetime


def __get_test_environment_variable():
    """
    This method generate environment variable for test
    """
    test_environment_variable = {}

    ##################################################################################################
    # dynamic parameters - configure for local run
    test_environment_variable['runner_path'] = os.environ.get('RUNNER_PATH', '/tmp')
    test_environment_variable['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')
    # Node Selector
    test_environment_variable['pin_node1'] = os.environ.get('PIN_NODE1', '')
    # ElasticSearch
    test_environment_variable['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
    test_environment_variable['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')
    test_environment_variable['elasticsearch_user'] = os.environ.get('ELASTICSEARCH_USER', '')
    test_environment_variable['elasticsearch_password'] = os.environ.get('ELASTICSEARCH_PASSWORD', '')
    test_environment_variable['timeout'] = int(os.environ.get('TIMEOUT', '2000'))

    # end dynamic parameters - configure for local run
    ##################################################################################################

    # ** DO NOT CHANGE THE PARAMETERS BELOW **
    # Constant parameters

    test_environment_variable['namespace'] = os.environ.get('NAMESPACE', 'benchmark-operator')
    # run Hammerdb workload with odf pvc
    test_environment_variable['odf_pvc'] = os.environ.get('ODF_PVC', 'True')
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

    # IBM details
    test_environment_variable['region_name'] = os.environ.get('IBM_REGION_NAME', '')
    test_environment_variable['endpoint_url'] = os.environ.get('IBM_ENDPOINT_URL', None)
    test_environment_variable['access_key_id'] = os.environ.get('IBM_ACCESS_KEY_ID', '')
    test_environment_variable['secret_access_key'] = os.environ.get('IBM_SECRET_ACCESS_KEY', '')
    test_environment_variable['bucket'] = os.environ.get('IBM_BUCKET', '')
    test_environment_variable['key'] = os.environ.get('IBM_KEY', '')
    # IBM S3
    test_environment_variable['key'] = os.environ.get('KEY', 'run-artifacts')
    test_environment_variable['run_type'] = os.environ.get('RUN_TYPE', 'test-ci')
    test_environment_variable['date_key'] = datetime.datetime.now().strftime("%Y/%m/%d")

    # update node_selector
    if test_environment_variable['pin_node1']:
        test_environment_variable['pin'] = 'true'
    else:
        test_environment_variable['pin'] = 'false'

    # ElasticSearch url
    if test_environment_variable.get('elasticsearch_password', ''):
        test_environment_variable['elasticsearch_url'] = f"http://{test_environment_variable.get('elasticsearch_user', '')}:{test_environment_variable.get('elasticsearch_password', '')}@{test_environment_variable.get('elasticsearch', '')}:{test_environment_variable.get('elasticsearch_port', '')}"
    else:
        if test_environment_variable['elasticsearch'] and test_environment_variable.get('elasticsearch_port', ''):
            test_environment_variable['elasticsearch_url'] = f"http://{test_environment_variable.get('elasticsearch', '')}:{test_environment_variable.get('elasticsearch_port', '')}"
        else:
            test_environment_variable['elasticsearch_url'] = ''
    return test_environment_variable


# Global path parameters
dir_path = os.path.dirname(os.path.realpath(__file__))
templates_path = os.path.join(dir_path, 'templates')
test_environment_variable = __get_test_environment_variable()
