
import os


class EnvironmentVariables:
    """
    This class manage environment variable parameters
    """
    def __init__(self):
        self._environment_variables_dict = {}
        self._workloads_list = []
        self._workloads_list = ['hammerdb_pod_mariadb', 'hammerdb_pod_mssql', 'hammerdb_pod_postgres',
                          'hammerdb_vm_mariadb', 'hammerdb_vm_mssql', 'hammerdb_vm_postgres',
                          'stressng_pod', 'stressng_vm',
                          'uperf_pod', 'uperf_vm']

        self._environment_variables_dict['kubeconfig'] = os.environ.get('KUBECONFIG', '')
        self._environment_variables_dict['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')
        self._environment_variables_dict['workload'] = os.environ.get('WORKLOAD', '')
        self._environment_variables_dict['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
        self._environment_variables_dict['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')
        self._environment_variables_dict['pin_node1'] = os.environ.get('PIN_NODE1', '')
        self._environment_variables_dict['pin_node2'] = os.environ.get('PIN_NODE2', '')
        if self._environment_variables_dict['elasticsearch'] and self._environment_variables_dict['elasticsearch_port']:
            self._environment_variables_dict['elasticsearch_url'] = f"http://{self._environment_variables_dict['elasticsearch']}:{self._environment_variables_dict['elasticsearch_port']}"
        # in case no port
        elif self._environment_variables_dict['elasticsearch'] and not self._environment_variables_dict['elasticsearch_port']:
            self._environment_variables_dict['elasticsearch'] = self._environment_variables_dict['elasticsearch']
        else:
            self._environment_variables_dict['elasticsearch_url'] = ''

    @property
    def workloads_list(self):
        """
        This method is getter
        """
        return self._workloads_list

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