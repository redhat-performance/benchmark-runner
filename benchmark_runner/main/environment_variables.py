
import os


class EnvironmentVariables:
    """
    This class manage environment variable parameters
    """
    def __init__(self):
        self._environment_variables_dict = {}
        # hard coded parameters
        self._environment_variables_dict['workloads'] = ['stressng_pod', 'stressng_vm', 'uperf_pod', 'uperf_vm', 'hammerdb_pod_mariadb', 'hammerdb_vm_mariadb',  'hammerdb_pod_postgres', 'hammerdb_vm_postgres', 'hammerdb_pod_mssql', 'hammerdb_vm_mssql']
        self._environment_variables_dict['namespace'] = os.environ.get('namespace', 'benchmark-operator')

        # dynamic parameters
        self._environment_variables_dict['workload'] = os.environ.get('WORKLOAD', '')
        self._environment_variables_dict['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')
        self._environment_variables_dict['pin_node_benchmark_operator'] = os.environ.get('PIN_NODE_BENCHMARK_OPERATOR', '')
        self._environment_variables_dict['pin_node1'] = os.environ.get('PIN_NODE1', '')
        self._environment_variables_dict['pin_node2'] = os.environ.get('PIN_NODE2', '')
        # This path is for benchmark-operator path
        self._environment_variables_dict['runner_path'] = os.environ.get('RUNNER_PATH', '')
        self._environment_variables_dict['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
        self._environment_variables_dict['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')
        if self._environment_variables_dict['elasticsearch'] and self._environment_variables_dict['elasticsearch_port']:
            self._environment_variables_dict['elasticsearch_url'] = f"{self._environment_variables_dict['elasticsearch']}:{self._environment_variables_dict['elasticsearch_port']}"
        else:
            self._environment_variables_dict['elasticsearch_url'] = ''

    @property
    def workloads_list(self):
        """
        This method is getter
        """
        return self._environment_variables_dict['workloads']

    @property
    def environment_variables_dict(self):
        """
        This method is getter
        """
        return self._environment_variables_dict

    @environment_variables_dict.setter
    def environment_variables_dict(self, value: dict):
        """
        This method is setter
        """
        self._environment_variables_dict = value


environment_variables = EnvironmentVariables()
