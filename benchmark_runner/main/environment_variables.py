
import os
import time
import datetime
from uuid import uuid4


class EnvironmentVariables:
    """
    This class manage environment variable parameters
    """
    def __init__(self):

        self._environment_variables_dict = {}

        # env files override true ENV. Not best order, but easier to write :/
        # .env.generated can be auto-generated (by an external tool) based on the local cluster's configuration.

        for env in ".env", ".env.generated":
            try:
                with open(env) as f:
                    for line in f.readlines():
                        key, found , value = line.strip().partition("=")
                        if not found:
                            print("ERROR: invalid line in {env}: {line.strip()}")
                            continue
                        if key in os.environ: continue # prefer env to env file
                        os.environ[key] = value

            except FileNotFoundError: pass # ignore

        ##################################################################################################
        # dynamic parameters - configure for local run
        # parameters for running workload

        # This path is github actions runner path (benchmark-operator should be cloned here)
        self._environment_variables_dict['runner_path'] = os.environ.get('RUNNER_PATH', '/tmp')
        # This path is for vm/pod/prometheus run artifacts
        self._environment_variables_dict['run_artifacts'] = os.environ.get('RUN_ARTIFACTS', os.path.join(self._environment_variables_dict['runner_path'], 'benchmark-runner-run-artifacts'))
        # cluster: 'openshift'(Default)/ 'kubernetes'
        self._environment_variables_dict['cluster'] = os.environ.get('CLUSTER', 'openshift')

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
        self._environment_variables_dict['elasticsearch_user'] = os.environ.get('ELASTICSEARCH_USER', '')
        self._environment_variables_dict['elasticsearch_password'] = os.environ.get('ELASTICSEARCH_PASSWORD', '')
        # 'http'(Default) / 'https' to use SSL to connect ElasticSearch
        self._environment_variables_dict['elasticsearch_url_protocol'] = os.environ.get('ELASTICSEARCH_URL_PROTOCOL', 'http')

        # Workaround for Kata CPU offline problem in 4.9/4.10
        # Set to True to
        self._environment_variables_dict['kata_cpuoffline_workaround'] = os.environ.get('KATA_CPUOFFLINE_WORKAROUND', '')

        # Scale in each node
        self._environment_variables_dict['scale'] = os.environ.get('SCALE', '')
        # list of nodes per pod/vm, scale number per node, e.g: [ 'master-1', 'master-2' ] - run 1 pod/vm in each node
        self._environment_variables_dict['scale_nodes'] = os.environ.get('SCALE_NODES', "")
        self._environment_variables_dict['redis'] = os.environ.get('REDIS', '')

        # default parameter - change only if needed
        # Parameters below related to 'run_workload()'
        self._environment_variables_dict['workloads'] = ['stressng_pod', 'stressng_vm', 'stressng_kata',
                                                         'uperf_pod', 'uperf_vm', 'uperf_kata',
                                                         'hammerdb_pod_mariadb', 'hammerdb_vm_mariadb', 'hammerdb_kata_mariadb',
                                                         'hammerdb_pod_postgres', 'hammerdb_vm_postgres', 'hammerdb_kata_postgres',
                                                         'hammerdb_pod_mssql', 'hammerdb_vm_mssql', 'hammerdb_kata_mssql',
                                                         'vdbench_pod', 'vdbench_kata', 'vdbench_vm',
                                                         'clusterbuster']
        # Workloads namespaces
        self._environment_variables_dict['workload_namespaces'] = {
            'stressng': 'benchmark-operator',
            'hammerdb': 'benchmark-operator',
            'uperf': 'benchmark-operator',
            'vdbench': 'benchmark-runner',
            'clusterbuster': 'clusterbuster',
        }

        # Update namespace
        base_workload = self._environment_variables_dict['workload'].split('_')[0]
        if os.environ.get('NAMESPACE'):
            self._environment_variables_dict['namespace'] = os.environ.get('NAMESPACE')
        elif base_workload in self._environment_variables_dict['workload_namespaces']:
            default_namespace = self._environment_variables_dict['workload_namespaces'][base_workload]
            self._environment_variables_dict['namespace'] = os.environ.get('NAMESPACE', default_namespace)
        else:
            # TBD if this is not set
            self._environment_variables_dict['namespace'] = 'benchmark-operator'

        # run workload with odf pvc True/False. True=ODF, False=Ephemeral
        self._environment_variables_dict['odf_pvc'] = os.environ.get('ODF_PVC', 'True')
        # Workloads that required ODF
        self._environment_variables_dict['workloads_odf_pvc'] = ['vdbench', 'hammerdb']
        # This parameter get from Test_CI.yml file
        self._environment_variables_dict['build_version'] = os.environ.get('BUILD_VERSION', '1.0.0')
        # collect system metrics True/False - required by benchmark-operator
        if self._environment_variables_dict['elasticsearch']:
            self._environment_variables_dict['system_metrics'] = os.environ.get('SYSTEM_METRICS', 'True')
        else:
            self._environment_variables_dict['system_metrics'] = os.environ.get('SYSTEM_METRICS', 'False')
        # CI status update once at the end of CI pass/failed
        self._environment_variables_dict['ci_status'] = os.environ.get('CI_STATUS', '')
        # Valid run types
        self._environment_variables_dict['run_types'] = ['test_ci', 'func_ci', 'perf_ci']
        # Run type test_ci/func_ci/perf_ci, default test_ci same environment as func_ci
        self._environment_variables_dict['run_type'] = os.environ.get('RUN_TYPE', 'test_ci')
        self._environment_variables_dict['runner_type'] = os.environ.get('RUNNER_TYPE')
        self._environment_variables_dict['config_from_args'] = os.environ.get('CONFIG_FROM_ARGS')
        self._environment_variables_dict['template_in_workload_dir'] = os.environ.get('TEMPLATE_IN_WORKLOAD_DIR')

        # Run uuid
        self._environment_variables_dict['uuid'] = os.environ.get('UUID', str(uuid4()))
        self._environment_variables_dict['trunc_uuid'] = self._environment_variables_dict['uuid'].split('-')[0]
        # Benchmark runner IBM Cloud Object Storage run artifacts hierarchy, not part of a POSIX path ('/' a key seperator, '-' file name convenstion )
        self._environment_variables_dict['date_key'] = datetime.datetime.now().strftime("%Y/%m/%d")
        self._environment_variables_dict['time_stamp_format'] = os.path.join(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))
        # Benchmark runner local run artifacts path with time stamp format

        self._environment_variables_dict['run_artifacts_path'] = os.environ.get('RUN_ARTIFACTS_PATH')
        if not self._environment_variables_dict['run_artifacts_path']:
            self._environment_variables_dict['run_artifacts_path'] = os.path.join(self._environment_variables_dict['run_artifacts'], f"{self._environment_variables_dict['workload'].replace('_', '-')}-{self._environment_variables_dict['time_stamp_format']}")

        # True/False: default False
        self._environment_variables_dict['save_artifacts_local'] = os.environ.get('SAVE_ARTIFACTS_LOCAL', 'False')
        # True/False: default False
        self._environment_variables_dict['enable_prometheus_snapshot'] = os.environ.get('ENABLE_PROMETHEUS_SNAPSHOT', 'False')
        # end dynamic parameters - configure for local run
        ##################################################################################################

        # ** DO NOT CHANGE THE PARAMETERS BELOW **
        # Constant parameters

        # Parameters below related to 'azure_cluster_start_stop()'
        # Azure details
        self._environment_variables_dict['azure_cluster_stop'] = os.environ.get('AZURE_CLUSTER_STOP', '')
        self._environment_variables_dict['azure_cluster_start'] = os.environ.get('AZURE_CLUSTER_START', '')
        self._environment_variables_dict['azure_clientid'] = os.environ.get('AZURE_CLIENTID', '')
        self._environment_variables_dict['azure_secret'] = os.environ.get('AZURE_SECRET', '')
        self._environment_variables_dict['azure_tenantid'] = os.environ.get('AZURE_TENANTID', '')
        self._environment_variables_dict['azure_subscriptionid'] = os.environ.get('AZURE_SUBSCRIPTIONID', '')
        self._environment_variables_dict['azure_resource_group_name'] = os.environ.get('AZURE_RESOURCE_GROUP_NAME', '')
        self._environment_variables_dict['azure_vm_name'] = os.environ.get('AZURE_VM_NAME', '')

        # IBM details
        self._environment_variables_dict['region_name'] = os.environ.get('IBM_REGION_NAME', '')
        # None(default) - must for unittest
        self._environment_variables_dict['endpoint_url'] = os.environ.get('IBM_ENDPOINT_URL', None)
        self._environment_variables_dict['access_key_id'] = os.environ.get('IBM_ACCESS_KEY_ID', '')
        self._environment_variables_dict['secret_access_key'] = os.environ.get('IBM_SECRET_ACCESS_KEY', '')
        self._environment_variables_dict['bucket'] = os.environ.get('IBM_BUCKET', '')
        self._environment_variables_dict['key'] = os.environ.get('IBM_KEY', '')

        # Parameters below related to 'install_ocp()'
        # MANDATORY for OCP install: install ocp version - insert version to install i.e. 'latest-4.8' : https://mirror.openshift.com/pub/openshift-v4/clients/ocp
        self._environment_variables_dict['install_ocp_version'] = os.environ.get('INSTALL_OCP_VERSION', '')
        # There are 2 steps run_ibm_ocp_ipi_installer/verify_install_complete
        self._environment_variables_dict['install_step'] = os.environ.get('INSTALL_STEP', '')
        # dev or ga (/ocp-dev-preview/ or /ocp/ )
        self._environment_variables_dict['ocp_version_build'] = os.environ.get('OCP_VERSION_BUILD', '')
        # github repository
        self._environment_variables_dict['github_repository_short'] = os.environ.get('GITHUB_REPOSITORY_SHORT', '')

        # Parameters below related to 'install_resource()'
        # MANDATORY for OCP resource install: 'True' for install resources
        self._environment_variables_dict['install_ocp_resources'] = os.environ.get('INSTALL_OCP_RESOURCES', '')
        # cnv version
        self._environment_variables_dict['cnv_version'] = os.environ.get('CNV_VERSION', '')
        # QUAY_USERNAME for nightly build
        self._environment_variables_dict['quay_username'] = os.environ.get('QUAY_USERNAME', '')
        # QUAY_PASSWORD for nightly build
        self._environment_variables_dict['quay_password'] = os.environ.get('QUAY_PASSWORD', '')
        # odf version
        self._environment_variables_dict['odf_version'] = os.environ.get('ODF_VERSION', '')
        # number fo odf disk from ['sdb', 'sdc', 'sdd', 'sde']
        self._environment_variables_dict['num_odf_disk'] = os.environ.get('NUM_ODF_DISK', 1)
        # install resources list
        self._environment_variables_dict['install_resources_list'] = os.environ.get('INSTALL_RESOURCES_LIST', '')

        # Parameters below related to 'install_ocp()' and 'install_resource()'
        # Mandatory: OCP environment flavor PERF or FUNC
        self._environment_variables_dict['ocp_env_flavor'] = os.environ.get('OCP_ENV_FLAVOR', 'FUNC')
        # IBM details
        self._environment_variables_dict['ibm_api_key'] = os.environ.get('IBM_API_KEY', '')
        # github token
        self._environment_variables_dict['github_token'] = os.environ.get('GITHUB_TOKEN', '')
        self.__ocp_env_flavor = self._environment_variables_dict['ocp_env_flavor']
        self._environment_variables_dict['worker_ids'] = os.environ.get(f'{self.__ocp_env_flavor}_WORKER_IDS',  "")
        self._environment_variables_dict['provision_ip'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_IP', '')
        # Placed on secret only
        self._environment_variables_dict['provision_private_key'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_PRIVATE_KEY', '')
        # For internal private key path
        self._environment_variables_dict['provision_private_key_path'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_PRIVATE_KEY_PATH', '')
        self._environment_variables_dict['container_private_key_path'] = os.environ.get('CONTAINER_PRIVATE_KEY_PATH', '')
        self._environment_variables_dict['provision_user'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_USER', '')
        self._environment_variables_dict['provision_oc_user'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_OC_USER', '')
        self._environment_variables_dict['provision_port'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_PORT', '')
        self._environment_variables_dict['provision_kubeadmin_password_path'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_KUBEADMIN_PASSWORD_PATH', '')
        self._environment_variables_dict['provision_kubeconfig_path'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_KUBECONFIG_PATH', '')
        self._environment_variables_dict['container_kubeconfig_path'] = os.environ.get('CONTAINER_KUBECONFIG_PATH', '')
        self._environment_variables_dict['provision_installer_path'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_INSTALLER_PATH', '')
        self._environment_variables_dict['provision_installer_cmd'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_INSTALLER_CMD', '')
        self._environment_variables_dict['provision_installer_log'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_INSTALLER_LOG', '')
        # remote ssh timeout - 3 hours for installation time
        self._environment_variables_dict['provision_timeout'] = os.environ.get(f'{self.__ocp_env_flavor}_PROVISION_TIMEOUT', '10800')
        # General timeout - 1.5 hours wait for pod/vm/upload data to elasticsearch
        self._environment_variables_dict['timeout'] = os.environ.get(f'{self.__ocp_env_flavor}_TIMEOUT', '3600')

        # Benchmark runner run artifacts url
        self._environment_variables_dict['run_artifacts_url'] = os.environ.get(f'{self.__ocp_env_flavor}_RUN_ARTIFACTS_URL', '')

        # Parameters below related to 'update_ci_status()' - No need to configure update auto by ci
        # CI run time
        self._environment_variables_dict['ci_minutes_time'] = os.environ.get('CI_MINUTES_TIME', 0)
        # Get this parameter from install resource process
        self._environment_variables_dict['ocp_resource_install_minutes_time'] = os.environ.get('OCP_RESOURCE_INSTALL_MINUTES_TIME', 0)
        # benchmark-operator last commit id
        self._environment_variables_dict['benchmark_operator_id'] = os.environ.get('BENCHMARK_OPERATOR_ID', '')
        # benchmark-wrapper last commit id
        self._environment_variables_dict['benchmark_wrapper_id'] = os.environ.get('BENCHMARK_WRAPPER_ID', '')

        # Node Selector functionality
        if self._environment_variables_dict['pin_node1']:
            self._environment_variables_dict['pin'] = 'true'
        else:
            self._environment_variables_dict['pin'] = 'false'
        # if pin_node2 not exist, get pin_node1 value
        if self._environment_variables_dict['pin_node1'] and not self._environment_variables_dict['pin_node2']:
            self._environment_variables_dict['pin_node2'] = self._environment_variables_dict['pin_node1']

        # ElasticSearch url
        if self._environment_variables_dict.get('elasticsearch_password', ''):
            self._environment_variables_dict['elasticsearch_url'] = f"{self._environment_variables_dict['elasticsearch_url_protocol']}://{self._environment_variables_dict.get('elasticsearch_user', '')}:{self._environment_variables_dict.get('elasticsearch_password', '')}@{self._environment_variables_dict.get('elasticsearch', '')}:{self._environment_variables_dict.get('elasticsearch_port', '')}"
        else:
            if self._environment_variables_dict['elasticsearch'] and self._environment_variables_dict.get('elasticsearch_port', ''):
                self._environment_variables_dict['elasticsearch_url'] = f"{self._environment_variables_dict['elasticsearch_url_protocol']}://{self._environment_variables_dict.get('elasticsearch', '')}:{self._environment_variables_dict.get('elasticsearch_port', '')}"
            else:
                self._environment_variables_dict['elasticsearch_url'] = ''

        # OpenShift or kubernetes support, OpenShift: oc, kubectl || kubernetes: kubectl
        if self._environment_variables_dict['cluster'] == 'kubernetes':
            self._environment_variables_dict['cli'] = 'kubectl'
            self._environment_variables_dict['odf_pvc'] = 'False'
            self._environment_variables_dict['enable_prometheus_snapshot'] = None
        else:
            self._environment_variables_dict['cli'] = os.environ.get('CLI', 'oc')

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

    @property
    def run_types_list(self):
        """
        This method is getter
        """
        return self._environment_variables_dict['run_types']

    @environment_variables_dict.setter
    def environment_variables_dict(self, value: dict):
        """
        This method is setter
        """
        self._environment_variables_dict = value

    def get_workload_namespace(self, workload: str):
        """
        Return the workload namespace for a given workload
        """
        if workload in self._environment_variables_dict['workloads'] and workload.split('_')[0] in self._environment_variables_dict['workload_namespaces']:
            return self._environment_variables_dict['workload_namespaces'][workload.split('_')[0]]
        else:
            return None


environment_variables = EnvironmentVariables()
