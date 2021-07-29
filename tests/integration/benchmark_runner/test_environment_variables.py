
import os


def __get_test_environment_variable():
    """
    This method generate environment variable for test
    """
    test_environment_variable = {}
    # hard coded parameters
    test_environment_variable['namespace'] = os.environ.get('namespace', 'benchmark-operator')
    # run Hammerdb workload with ocs pvc
    test_environment_variable['ocs_pvc'] = os.environ.get('ocs_pvc', 'true')
    #  TODO: CPU issue in functional environment, need to walk around only in Azure functional environment
    test_environment_variable['functional_resource_limit'] = os.environ.get('functional_resource_limit', 'true')

    ##################################################################################################
    # dynamic parameters - configure for local run
    test_environment_variable['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')
    # Node Selector
    test_environment_variable['pin_node1'] = os.environ.get('PIN_NODE1', '')
    # ElasticSearch
    test_environment_variable['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
    test_environment_variable['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')
    # This path is for benchmark-operator path
    test_environment_variable['runner_path'] = os.environ.get('RUNNER_PATH', '')
    # end dynamic parameters - configure for local run
    ##################################################################################################

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
