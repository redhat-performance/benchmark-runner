
import os
import time
import datetime
import argparse
from uuid import uuid4
from benchmark_runner.main.environment_variables_exceptions import ParseFailed


class EnvironmentVariables:
    """
    This class manage environment variable parameters
    """

    HAMMERDB_LSO_LEN = 4

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

            except FileNotFoundError:
                pass  # ignore

        ##################################################################################################
        # dynamic parameters - configure for local run
        # parameters for running workload

        # This path is github actions runner path (benchmark-operator should be cloned here)
        self._environment_variables_dict['runner_path'] = EnvironmentVariables.get_env('RUNNER_PATH', '/tmp')
        # This path is for vm/pod/prometheus run artifacts
        self._environment_variables_dict['run_artifacts'] = EnvironmentVariables.get_env('RUN_ARTIFACTS', os.path.join(self._environment_variables_dict['runner_path'], 'benchmark-runner-run-artifacts'))
        # cluster: 'openshift'(Default)/ 'kubernetes'
        self._environment_variables_dict['cluster'] = EnvironmentVariables.get_env('CLUSTER', 'openshift')

        # dynamic parameters - configure for local run
        self._environment_variables_dict['workload'] = EnvironmentVariables.get_env('WORKLOAD', '')
        self._environment_variables_dict['kubeadmin_password'] = EnvironmentVariables.get_env('KUBEADMIN_PASSWORD', '')

        # PIN=node selector
        self._environment_variables_dict['pin_node_benchmark_operator'] = EnvironmentVariables.get_env('PIN_NODE_BENCHMARK_OPERATOR', '')
        self._environment_variables_dict['pin_node1'] = EnvironmentVariables.get_env('PIN_NODE1', '')
        self._environment_variables_dict['pin_node2'] = EnvironmentVariables.get_env('PIN_NODE2', '')

        # ElasticSearch
        self._environment_variables_dict['elasticsearch'] = EnvironmentVariables.get_env('ELASTICSEARCH', '')
        self._environment_variables_dict['elasticsearch_port'] = EnvironmentVariables.get_env('ELASTICSEARCH_PORT', '')
        self._environment_variables_dict['elasticsearch_user'] = EnvironmentVariables.get_env('ELASTICSEARCH_USER', '')
        self._environment_variables_dict['elasticsearch_password'] = EnvironmentVariables.get_env('ELASTICSEARCH_PASSWORD', '')
        # 'http'(Default) / 'https' to use SSL to connect ElasticSearch
        self._environment_variables_dict['elasticsearch_url_protocol'] = EnvironmentVariables.get_env('ELASTICSEARCH_URL_PROTOCOL', 'http')

        # Workaround for Kata CPU offline problem in 4.9/4.10
        # Set to True to
        self._environment_variables_dict['kata_cpuoffline_workaround'] = EnvironmentVariables.get_boolean_from_environment('KATA_CPUOFFLINE_WORKAROUND', False)

        # Scale in each node
        self._environment_variables_dict['scale'] = EnvironmentVariables.get_env('SCALE', '')
        # list of nodes per pod/vm, scale number per node, e.g: [ 'master-1', 'master-2' ] - run 1 pod/vm in each node
        self._environment_variables_dict['scale_nodes'] = EnvironmentVariables.get_env('SCALE_NODES', "")
        self._environment_variables_dict['redis'] = EnvironmentVariables.get_env('REDIS', '')

        # default parameter - change only if needed
        # Parameters below related to 'run_workload()'
        self._environment_variables_dict['workloads'] = ['stressng_pod', 'stressng_vm', 'stressng_kata',
                                                         'uperf_pod', 'uperf_vm', 'uperf_kata',
                                                         'hammerdb_pod_mariadb', 'hammerdb_vm_mariadb', 'hammerdb_kata_mariadb',
                                                         'hammerdb_pod_mariadb_lso', 'hammerdb_vm_mariadb_lso', 'hammerdb_kata_mariadb_lso',
                                                         'hammerdb_pod_postgres', 'hammerdb_vm_postgres', 'hammerdb_kata_postgres',
                                                         'hammerdb_pod_postgres_lso', 'hammerdb_vm_postgres_lso', 'hammerdb_kata_postgres_lso',
                                                         'hammerdb_pod_mssql', 'hammerdb_vm_mssql', 'hammerdb_kata_mssql',
                                                         'hammerdb_pod_mssql_lso', 'hammerdb_vm_mssql_lso', 'hammerdb_kata_mssql_lso',
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
        if EnvironmentVariables.get_env('NAMESPACE'):
            self._environment_variables_dict['namespace'] = EnvironmentVariables.get_env('NAMESPACE')
        elif base_workload in self._environment_variables_dict['workload_namespaces']:
            default_namespace = self._environment_variables_dict['workload_namespaces'][base_workload]
            self._environment_variables_dict['namespace'] = EnvironmentVariables.get_env('NAMESPACE', default_namespace)
        else:
            # TBD if this is not set
            self._environment_variables_dict['namespace'] = 'benchmark-operator'

        # run workload with odf pvc True/False. True=ODF, False=Ephemeral
        self._environment_variables_dict['odf_pvc'] = EnvironmentVariables.get_boolean_from_environment('ODF_PVC', True)
        if base_workload == 'hammerdb':
            if len(self._environment_variables_dict['workload'].split('_')) == self.HAMMERDB_LSO_LEN:
                self._environment_variables_dict['storage_type'] = self._environment_variables_dict['workload'].split('_')[self.HAMMERDB_LSO_LEN-1]
            elif self._environment_variables_dict['odf_pvc']:
                self._environment_variables_dict['storage_type'] = 'odf'
            else:
                self._environment_variables_dict['storage_type'] = 'ephemeral'
        # LSO Disk path
        self._environment_variables_dict['lso_path'] = EnvironmentVariables.get_env('LSO_PATH', '')
        # Workloads that required ODF
        self._environment_variables_dict['workloads_odf_pvc'] = ['vdbench', 'hammerdb']
        # This parameter get from Test_CI.yml file
        self._environment_variables_dict['build_version'] = EnvironmentVariables.get_env('BUILD_VERSION', '1.0.0')
        # collect system metrics True/False - required by benchmark-operator
        self._environment_variables_dict['system_metrics'] = EnvironmentVariables.get_boolean_from_environment('SYSTEM_METRICS',
                                                                                                               bool(self.environment_variables_dict['elasticsearch']))
        # CI status update once at the end of CI pass/failed
        self._environment_variables_dict['ci_status'] = EnvironmentVariables.get_env('CI_STATUS', '')
        # Valid run types
        self._environment_variables_dict['run_types'] = ['test_ci', 'func_ci', 'perf_ci', 'release']
        # Run type test_ci/func_ci/perf_ci, default test_ci same environment as func_ci
        self._environment_variables_dict['run_type'] = EnvironmentVariables.get_env('RUN_TYPE', 'test_ci')
        self._environment_variables_dict['runner_type'] = EnvironmentVariables.get_env('RUNNER_TYPE')
        self._environment_variables_dict['config_from_args'] = EnvironmentVariables.get_boolean_from_environment('CONFIG_FROM_ARGS', False)
        self._environment_variables_dict['template_in_workload_dir'] = EnvironmentVariables.get_env('TEMPLATE_IN_WORKLOAD_DIR')

        # Run uuid
        self._environment_variables_dict['uuid'] = EnvironmentVariables.get_env('UUID', str(uuid4()))
        self._environment_variables_dict['trunc_uuid'] = self._environment_variables_dict['uuid'].split('-')[0]
        # Benchmark runner IBM Cloud Object Storage run artifacts hierarchy, not part of a POSIX path ('/' a key seperator, '-' file name convenstion )
        self._environment_variables_dict['date_key'] = datetime.datetime.now().strftime("%Y/%m/%d")
        self._environment_variables_dict['time_stamp_format'] = os.path.join(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))
        # Benchmark runner local run artifacts path with time stamp format

        self._environment_variables_dict['run_artifacts_path'] = EnvironmentVariables.get_env('RUN_ARTIFACTS_PATH')
        if not self._environment_variables_dict['run_artifacts_path']:
            self._environment_variables_dict['run_artifacts_path'] = os.path.join(self._environment_variables_dict['run_artifacts'], f"{self._environment_variables_dict['workload'].replace('_', '-')}-{self._environment_variables_dict['time_stamp_format']}")

        # True/False: default False
        self._environment_variables_dict['save_artifacts_local'] = EnvironmentVariables.get_boolean_from_environment('SAVE_ARTIFACTS_LOCAL', False)
        # True/False: default False
        self._environment_variables_dict['enable_prometheus_snapshot'] = EnvironmentVariables.get_boolean_from_environment('ENABLE_PROMETHEUS_SNAPSHOT', False)
        # end dynamic parameters - configure for local run
        ##################################################################################################

        # ** DO NOT CHANGE THE PARAMETERS BELOW **
        # Constant parameters

        # Parameters below related to 'azure_cluster_start_stop()'
        # Azure data
        self._environment_variables_dict['azure_cluster_stop'] = EnvironmentVariables.get_env('AZURE_CLUSTER_STOP', '')
        self._environment_variables_dict['azure_cluster_start'] = EnvironmentVariables.get_env('AZURE_CLUSTER_START', '')
        self._environment_variables_dict['azure_clientid'] = EnvironmentVariables.get_env('AZURE_CLIENTID', '')
        self._environment_variables_dict['azure_secret'] = EnvironmentVariables.get_env('AZURE_SECRET', '')
        self._environment_variables_dict['azure_tenantid'] = EnvironmentVariables.get_env('AZURE_TENANTID', '')
        self._environment_variables_dict['azure_subscriptionid'] = EnvironmentVariables.get_env('AZURE_SUBSCRIPTIONID', '')
        self._environment_variables_dict['azure_resource_group_name'] = EnvironmentVariables.get_env('AZURE_RESOURCE_GROUP_NAME', '')
        self._environment_variables_dict['azure_vm_name'] = EnvironmentVariables.get_env('AZURE_VM_NAME', '')

        # CLUSTRBUSTER data
        self._environment_variables_dict['clusterbuster_workload'] = EnvironmentVariables.get_env('CLUSTERBUSTER_WORKLOAD', '')
        self._environment_variables_dict['clusterbuster_uuid'] = EnvironmentVariables.get_env('CLUSTERBUSTER_UUID', '')

        # IBM data
        self._environment_variables_dict['region_name'] = EnvironmentVariables.get_env('IBM_REGION_NAME', '')
        # None(default) - must for unittest
        self._environment_variables_dict['endpoint_url'] = EnvironmentVariables.get_env('IBM_ENDPOINT_URL', None)
        self._environment_variables_dict['access_key_id'] = EnvironmentVariables.get_env('IBM_ACCESS_KEY_ID', '')
        self._environment_variables_dict['secret_access_key'] = EnvironmentVariables.get_env('IBM_SECRET_ACCESS_KEY', '')
        self._environment_variables_dict['bucket'] = EnvironmentVariables.get_env('IBM_BUCKET', '')
        self._environment_variables_dict['key'] = EnvironmentVariables.get_env('IBM_KEY', '')

        # Parameters below related to 'install_ocp()'
        # MANDATORY for OCP install: install ocp version - insert version to install i.e. 'latest-4.8' : https://mirror.openshift.com/pub/openshift-v4/clients/ocp
        self._environment_variables_dict['install_ocp_version'] = EnvironmentVariables.get_env('INSTALL_OCP_VERSION', '')
        # There are 2 steps run_ibm_ocp_ipi_installer/verify_install_complete
        self._environment_variables_dict['install_step'] = EnvironmentVariables.get_env('INSTALL_STEP', '')
        # github repository
        self._environment_variables_dict['github_repository_short'] = EnvironmentVariables.get_env('GITHUB_REPOSITORY_SHORT', '')

        # Parameters below related to 'install_resource()'
        # MANDATORY for OCP resource install: True for install resources
        self._environment_variables_dict['install_ocp_resources'] = EnvironmentVariables.get_boolean_from_environment('INSTALL_OCP_RESOURCES', False)
        # cnv version
        self._environment_variables_dict['cnv_version'] = EnvironmentVariables.get_env('CNV_VERSION', '')
        # QUAY_USERNAME for nightly build
        self._environment_variables_dict['quay_username'] = EnvironmentVariables.get_env('QUAY_USERNAME', '')
        # QUAY_PASSWORD for nightly build
        self._environment_variables_dict['quay_password'] = EnvironmentVariables.get_env('QUAY_PASSWORD', '')
        # odf version
        self._environment_variables_dict['odf_version'] = EnvironmentVariables.get_env('ODF_VERSION', '')
        # number fo odf disk from ['sdb', 'sdc', 'sdd', 'sde']
        self._environment_variables_dict['num_odf_disk'] = EnvironmentVariables.get_env('NUM_ODF_DISK', 1)
        # install resources list
        self._environment_variables_dict['install_resources_list'] = EnvironmentVariables.get_env('INSTALL_RESOURCES_LIST', '')

        # Parameters below related to 'install_ocp()' and 'install_resource()'

        # IBM data
        self._environment_variables_dict['ibm_api_key'] = EnvironmentVariables.get_env('IBM_API_KEY', '')
        # github token
        self._environment_variables_dict['github_token'] = EnvironmentVariables.get_env('GITHUB_TOKEN', '')
        self._environment_variables_dict['worker_ids'] = EnvironmentVariables.get_env(f'WORKER_IDS', "")
        self._environment_variables_dict['provision_ip'] = EnvironmentVariables.get_env(f'PROVISION_IP', '')
        # Placed on secret only
        self._environment_variables_dict['provision_private_key'] = EnvironmentVariables.get_env(f'PROVISION_PRIVATE_KEY', '')
        # For internal private key path
        self._environment_variables_dict['provision_private_key_path'] = EnvironmentVariables.get_env(f'PROVISION_PRIVATE_KEY_PATH', '')
        self._environment_variables_dict['container_private_key_path'] = EnvironmentVariables.get_env('CONTAINER_PRIVATE_KEY_PATH', '')
        self._environment_variables_dict['provision_user'] = EnvironmentVariables.get_env(f'PROVISION_USER', '')
        self._environment_variables_dict['provision_port'] = EnvironmentVariables.get_env(f'PROVISION_PORT', '')
        self._environment_variables_dict['provision_kubeadmin_password_path'] = EnvironmentVariables.get_env(f'PROVISION_KUBEADMIN_PASSWORD_PATH', '')
        self._environment_variables_dict['provision_kubeconfig_path'] = EnvironmentVariables.get_env(f'PROVISION_KUBECONFIG_PATH', '')
        self._environment_variables_dict['container_kubeconfig_path'] = EnvironmentVariables.get_env('CONTAINER_KUBECONFIG_PATH', '')
        self._environment_variables_dict['provision_installer_path'] = EnvironmentVariables.get_env(f'PROVISION_INSTALLER_PATH', '')
        self._environment_variables_dict['provision_installer_cmd'] = EnvironmentVariables.get_env(f'PROVISION_INSTALLER_CMD', '')
        self._environment_variables_dict['provision_installer_log'] = EnvironmentVariables.get_env(f'PROVISION_INSTALLER_LOG', '')
        # remote ssh timeout - 3 hours for installation time
        self._environment_variables_dict['provision_timeout'] = EnvironmentVariables.get_env(f'PROVISION_TIMEOUT', '10800')
        # General timeout - 1.5 hours wait for pod/vm/upload data to elasticsearch
        self._environment_variables_dict['timeout'] = EnvironmentVariables.get_env(f'TIMEOUT', '3600')

        # Benchmark runner run artifacts url
        self._environment_variables_dict['run_artifacts_url'] = EnvironmentVariables.get_env(f'RUN_ARTIFACTS_URL', '')

        # Parameters below related to 'update_ci_status()' - No need to configure update auto by ci
        # CI run time
        self._environment_variables_dict['ci_minutes_time'] = EnvironmentVariables.get_env('CI_MINUTES_TIME', 0)
        # Get this parameter from install resource process
        self._environment_variables_dict['ocp_resource_install_minutes_time'] = EnvironmentVariables.get_env('OCP_RESOURCE_INSTALL_MINUTES_TIME', 0)
        # benchmark-operator last commit id
        self._environment_variables_dict['benchmark_operator_id'] = EnvironmentVariables.get_env('BENCHMARK_OPERATOR_ID', '')
        # benchmark-wrapper last commit id
        self._environment_variables_dict['benchmark_wrapper_id'] = EnvironmentVariables.get_env('BENCHMARK_WRAPPER_ID', '')

        # Node Selector functionality
        self._environment_variables_dict['pin'] = bool(self._environment_variables_dict['pin_node1'])
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
            self._environment_variables_dict['odf_pvc'] = False
            self._environment_variables_dict['enable_prometheus_snapshot'] = None
        else:
            self._environment_variables_dict['cli'] = EnvironmentVariables.get_env('CLI', 'oc')

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

    @staticmethod
    def to_bool(arg, def_val: bool = None):
        if isinstance(arg, bool):
            return arg
        if isinstance(arg, (int, float)):
            return arg != 0
        if isinstance(arg, str):
            arg = arg.lower()
            if arg == 'true' or arg == 'yes':
                return True
            elif arg == 'false' or arg == 'no':
                return False
            try:
                arg1 = int(arg)
                return arg1 != 0
            except Exception:
                pass
        if def_val is not None:
            return def_val
        raise ParseFailed(f'Cannot parse {arg} as a boolean value')

    @staticmethod
    def get_env(var: str, defval=''):
        lcvar = var.lower()
        dashvar = lcvar.replace('_', '-')
        parser = argparse.ArgumentParser(description = 'Run BenchmarkRunner', allow_abbrev=False)
        if lcvar == dashvar:
            parser.add_argument(f"--{lcvar}", default=os.environ.get(var, defval), type=str, metavar='String', help=var)
        else:
            parser.add_argument(f"--{lcvar}", f"--{dashvar}", default=os.environ.get(var, defval), type=str, metavar='String', help=var)
        args, ignore = parser.parse_known_args()
        if hasattr(args, lcvar):
            return getattr(args, lcvar)
        else:
            return os.environ.get(var, defval)

    @staticmethod
    def get_boolean_from_environment(var: str, defval: bool):
        return EnvironmentVariables.to_bool(EnvironmentVariables.get_env(var), defval)


environment_variables = EnvironmentVariables()
