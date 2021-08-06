
import os


class EnvironmentVariables:
    """
    This class manage environment variable parameters
    """
    def __init__(self):

        self._environment_variables_dict = {}

        # hard coded parameters
        self._environment_variables_dict['workloads'] = ['stressng_pod', 'stressng_vm', 'uperf_pod', 'uperf_vm', 'hammerdb_pod_mariadb', 'hammerdb_vm_mariadb',  'hammerdb_pod_postgres', 'hammerdb_vm_postgres', 'hammerdb_pod_mssql', 'hammerdb_vm_mssql']
        self._environment_variables_dict['namespace'] = os.environ.get('NAMESPACE', 'benchmark-operator')
        # run Hammerdb workload with ocs pvc
        self._environment_variables_dict['ocs_pvc'] = os.environ.get('OCS_PVC', 'true')
        # This parameter get from CI.yml file
        self._environment_variables_dict['build_version'] = os.environ.get('BUILD_VERSION', '1.0.0')
        # collect system metrics
        self._environment_variables_dict['system_metrics'] = os.environ.get('SYSTEM_METRICS', 'true')

        # This path is for benchmark-operator path
        self._environment_variables_dict['runner_path'] = os.environ.get('RUNNER_PATH', '/')
        ##################################################################################################

        # Azure details for start/stop Azure mechanism only
        self._environment_variables_dict['azure_cluster_stop'] = os.environ.get('AZURE_CLUSTER_STOP', '')
        self._environment_variables_dict['azure_cluster_start'] = os.environ.get('AZURE_CLUSTER_START', '')
        self._environment_variables_dict['azure_clientid'] = os.environ.get('AZURE_CLIENTID', '')
        self._environment_variables_dict['azure_secret'] = os.environ.get('AZURE_SECRET', '')
        self._environment_variables_dict['azure_tenantid'] = os.environ.get('AZURE_TENANTID', '')
        self._environment_variables_dict['azure_subscriptionid'] = os.environ.get('AZURE_SUBSCRIPTIONID', '')
        self._environment_variables_dict['azure_resource_group_name'] = os.environ.get('AZURE_RESOURCE_GROUP_NAME', '')
        self._environment_variables_dict['azure_vm_name'] = os.environ.get('AZURE_VM_NAME', '')

        # dynamic parameters - configure for local run
        self._environment_variables_dict['workload'] = os.environ.get('WORKLOAD', '')
        self._environment_variables_dict['kubeadmin_password'] = os.environ.get('KUBEADMIN_PASSWORD', '')

        # PIN=node selector
        self._environment_variables_dict['pin_node_benchmark_operator'] = os.environ.get('PIN_NODE_BENCHMARK_OPERATOR', '')
        self._environment_variables_dict['pin_node1'] = os.environ.get('PIN_NODE1', '')
        self._environment_variables_dict['pin_node2'] = os.environ.get('PIN_NODE2', '')

        # ElasticSearch
        self._environment_variables_dict['elasticsearch'] = os.environ.get('ELASTICSEARCH', '')
        self._environment_variables_dict['elasticsearch_port'] = os.environ.get('ELASTICSEARCH_PORT', '')

        # Prometheus token: $ oc -n openshift-monitoring sa get-token prometheus-k8s
        self._environment_variables_dict['prom_token'] = os.environ.get('PROM_TOKEN', '')
        # end dynamic parameters - configure for local run
        ##################################################################################################

        # Node Selector functionality
        if self._environment_variables_dict['pin_node1']:
            self._environment_variables_dict['pin'] = 'true'
        else:
            self._environment_variables_dict['pin'] = 'false'
        # if pin_node2 not exist, get pin_node1 value
        if self._environment_variables_dict['pin_node1'] and not self._environment_variables_dict['pin_node2']:
            self._environment_variables_dict['pin_node2'] = self._environment_variables_dict['pin_node1']

        # ElasticSearch functionality
        if self._environment_variables_dict['elasticsearch'] and self._environment_variables_dict['elasticsearch_port']:
            self._environment_variables_dict['elasticsearch_url'] = f"http://{self._environment_variables_dict['elasticsearch']}:{self._environment_variables_dict['elasticsearch_port']}"
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
