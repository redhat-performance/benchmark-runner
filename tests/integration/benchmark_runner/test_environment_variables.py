
import os


def __get_test_environment_variable():
    """
    This method generate environment variable for test
    """
    test_environment_variable = {}
    # hard coded parameters
    test_environment_variable['namespace'] = os.environ.get('namespace', 'benchmark-operator')
    # Dynamic parameters
    test_environment_variable['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')
    test_environment_variable['workload'] = os.environ.get('WORKLOAD', '')
    test_environment_variable['pin_node1'] = os.environ.get('PIN_NODE1', '')
    # This path is for benchmark-operator path
    test_environment_variable['runner_path'] = os.environ.get('RUNNER_PATH', '')
    test_environment_variable['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
    test_environment_variable['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')
    if test_environment_variable['elasticsearch'] and test_environment_variable['elasticsearch_port']:
        test_environment_variable[
            'elasticsearch_url'] = f"http://{test_environment_variable['elasticsearch']}:{test_environment_variable['elasticsearch_port']}"
    else:
        test_environment_variable['elasticsearch_url'] = ''
    return test_environment_variable


# Global path parameters
dir_path = os.path.dirname(os.path.realpath(__file__))
templates_path = os.path.join(dir_path, 'templates')
test_environment_variable = __get_test_environment_variable()
