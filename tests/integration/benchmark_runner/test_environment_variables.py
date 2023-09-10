
import os
import datetime
from benchmark_runner.main.environment_variables import EnvironmentVariables


def __get_test_environment_variable():
    """
    This method generate environment variable for test
    """
    test_environment_variable = {}

    ##################################################################################################
    # dynamic parameters - configure for local run
    test_environment_variable['runner_path'] = EnvironmentVariables.get_env('RUNNER_PATH', '/tmp')
    test_environment_variable['kubeadmin_password'] = EnvironmentVariables.get_env('KUBEADMIN_PASSWORD', '')
    # Node Selector
    test_environment_variable['pin_node1'] = EnvironmentVariables.get_env('PIN_NODE1', '')
    # ElasticSearch
    test_environment_variable['elasticsearch'] = EnvironmentVariables.get_env('ELASTICSEARCH', '')
    test_environment_variable['elasticsearch_port'] = EnvironmentVariables.get_env('ELASTICSEARCH_PORT', '')
    test_environment_variable['elasticsearch_user'] = EnvironmentVariables.get_env('ELASTICSEARCH_USER', '')
    test_environment_variable['elasticsearch_password'] = EnvironmentVariables.get_env('ELASTICSEARCH_PASSWORD', '')
    test_environment_variable['timeout'] = int(EnvironmentVariables.get_env('TIMEOUT', '2000'))

    # Grafana
    test_environment_variable['grafana_url'] = EnvironmentVariables.get_env('GRAFANA_URL', '')
    test_environment_variable['grafana_api_key'] = EnvironmentVariables.get_env('GRAFANA_API_KEY', '')
    test_environment_variable['grafana_json_path'] = EnvironmentVariables.get_env('GRAFANA_JSON_PATH', '')
    test_environment_variable['grafana_json_path'] = EnvironmentVariables.get_env('GRAFANA_FOLDER_NAME', '')

    # end dynamic parameters - configure for local run
    ##################################################################################################

    # ** DO NOT CHANGE THE PARAMETERS BELOW **
    # Constant parameters

    test_environment_variable['namespace'] = EnvironmentVariables.get_env('NAMESPACE', 'benchmark-operator')
    # run Hammerdb workload with ocs pvc
    test_environment_variable['ocs_pvc'] = EnvironmentVariables.get_boolean_from_environment('OCS_PVC', True)
    test_environment_variable['system_metrics'] = EnvironmentVariables.get_boolean_from_environment('SYSTEM_METRICS', False)
    # Azure details
    test_environment_variable['azure_cluster_stop'] = EnvironmentVariables.get_env('AZURE_CLUSTER_STOP', '')
    test_environment_variable['azure_cluster_start'] = EnvironmentVariables.get_env('AZURE_CLUSTER_START', '')
    test_environment_variable['azure_clientid'] = EnvironmentVariables.get_env('AZURE_CLIENTID', '')
    test_environment_variable['azure_secret'] = EnvironmentVariables.get_env('AZURE_SECRET', '')
    test_environment_variable['azure_tenantid'] = EnvironmentVariables.get_env('AZURE_TENANTID', '')
    test_environment_variable['azure_subscriptionid'] = EnvironmentVariables.get_env('AZURE_SUBSCRIPTIONID', '')
    test_environment_variable['azure_resource_group_name'] = EnvironmentVariables.get_env('AZURE_RESOURCE_GROUP_NAME', '')
    test_environment_variable['azure_vm_name'] = EnvironmentVariables.get_env('AZURE_VM_NAME', '')

    # IBM details
    test_environment_variable['region_name'] = EnvironmentVariables.get_env('IBM_REGION_NAME', '')
    test_environment_variable['endpoint_url'] = EnvironmentVariables.get_env('IBM_ENDPOINT_URL', None)
    test_environment_variable['access_key_id'] = EnvironmentVariables.get_env('IBM_ACCESS_KEY_ID', '')
    test_environment_variable['secret_access_key'] = EnvironmentVariables.get_env('IBM_SECRET_ACCESS_KEY', '')
    test_environment_variable['bucket'] = EnvironmentVariables.get_env('IBM_BUCKET', '')
    test_environment_variable['key'] = EnvironmentVariables.get_env('IBM_KEY', '')
    # IBM S3
    test_environment_variable['key'] = EnvironmentVariables.get_env('KEY', 'run-artifacts')
    test_environment_variable['run_type'] = EnvironmentVariables.get_env('RUN_TYPE', 'test-ci')
    test_environment_variable['date_key'] = datetime.datetime.now().strftime("%Y/%m/%d")

    # update node_selector
    test_environment_variable['pin'] = bool(test_environment_variable['pin_node1'])

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
