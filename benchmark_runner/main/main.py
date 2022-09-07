
import ast  # change string list to list

from benchmark_runner.main.environment_variables import *
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from benchmark_runner.workloads.workloads import Workloads
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.clouds.Azure.azure_operations import AzureOperations
from benchmark_runner.common.clouds.IBM.ibm_operations import IBMOperations
from benchmark_runner.clusterbuster.clusterbuster_workloads import ClusterBusterWorkloads
from benchmark_runner.common.oc.oc import OC

# logger
log_level = os.environ.get('log_level', 'INFO').upper()
logger.setLevel(level=log_level)

# venv
# python -m venv venv
# . venv/bin/activate

SYSTEM_EXIT_BENCHMARK_FAILED = 1
SYSTEM_EXIT_UNKNOWN_EXECUTION_TYPE = 2


@logger_time_stamp
def main():
    """
    The main of benchmark-runner handle Azure operations or Workload runs
    """
    benchmark_operator_workload = None
    benchmark_runner_workload = None
    clusterbuster_workload = None
    environment_variables_dict = environment_variables.environment_variables_dict
    # environment variables data
    provision_user = environment_variables_dict.get('provision_user', '')
    workload = environment_variables_dict.get('workload', '')
    azure_cluster_stop = environment_variables_dict.get('azure_cluster_stop', '')
    azure_cluster_start = environment_variables_dict.get('azure_cluster_start', '')
    ci_status = environment_variables_dict.get('ci_status', '')
    install_ocp_version = environment_variables_dict.get('install_ocp_version', '')
    install_ocp_resources = environment_variables_dict.get('install_ocp_resources', False)
    run_type = environment_variables_dict.get('run_type', '')

    is_benchmark_operator_workload = 'benchmark-operator' in (environment_variables.get_workload_namespace(workload), environment_variables_dict.get("runner_type"))
    is_benchmark_runner_workload = 'benchmark-runner' in (environment_variables.get_workload_namespace(workload), environment_variables_dict.get("runner_type"))
    is_clusterbuster_workload = 'clusterbuster' in (environment_variables.get_workload_namespace(workload), environment_variables_dict.get("runner_type"))
    # workload name validation
    if workload and not ci_status:
        if workload not in environment_variables.workloads_list:
            logger.info(f'Enter valid workload name {environment_variables.workloads_list}')
            raise Exception(f'Not valid workload name: {workload} \n, choose one from the list: {environment_variables.workloads_list}')
        # run type validation
        if run_type not in environment_variables.run_types_list:
            logger.info(f'Enter valid run type {environment_variables.run_types_list}')
            raise Exception(f'Invalid run type: {run_type} \n, choose one from the list: {environment_variables.run_types_list}')
        if is_clusterbuster_workload:
            clusterbuster_workload = ClusterBusterWorkloads()
        elif is_benchmark_operator_workload:
            benchmark_operator_workload = BenchmarkOperatorWorkloads()
        elif is_benchmark_runner_workload:
            benchmark_runner_workload = Workloads()

    @logger_time_stamp
    def azure_cluster_start_stop():
        """
        This method start stop azure cluster
        :return:
        """
        azure_operation = AzureOperations(azure_clientid=environment_variables_dict.get('azure_clientid', ''),
                                          azure_secret=environment_variables_dict.get('azure_secret', ''),
                                          azure_tenantid=environment_variables_dict.get('azure_tenantid', ''),
                                          azure_subscriptionid=environment_variables_dict.get('azure_subscriptionid', ''),
                                          azure_resource_group_name=environment_variables_dict.get('azure_resource_group_name', ''))
        azure_vm_name = (environment_variables_dict.get('azure_vm_name', ''))
        if azure_cluster_start:
            logger.info(azure_operation.start_vm(vm_name=azure_vm_name))
        elif azure_cluster_stop:
            logger.info(azure_operation.stop_vm(vm_name=azure_vm_name))

    @logger_time_stamp
    def install_ocp(ibm_operations: IBMOperations, step: str):
        """
        This method install ocp version
        :return:
        """
        if step == 'run_ibm_ocp_installer':
            ibm_operations.update_ocp_version()
            ibm_operations.run_ibm_ocp_installer()
        elif step == 'verify_install_complete':
            complete = ibm_operations.verify_install_complete()
            if complete:
                logger.info(f'OCP {install_ocp_version} installation complete successfully')
                logger.info(f'restart pod ci')
                ibm_operations.restart_pod_ci()
                logger.info(f'Update GitHub OCP credentials')
                ibm_operations.update_ocp_github_credentials()
            else:
                logger.info(f'OCP {install_ocp_version} installation failed')
        ibm_operations.ibm_disconnect()

    @logger_time_stamp
    def install_resources():
        """
        This method install ocp resources
        :return:
        """
        ibm_operations = IBMOperations(user=provision_user)
        ibm_operations.ibm_connect()
        install_resources_list = environment_variables_dict.get('install_resources_list', '')
        resources = ast.literal_eval(install_resources_list)
        logger.info(f'Start IBM OCP resources installation')
        oc = ibm_operations.oc_login()
        ibm_operations.verify_cluster_is_up(oc)
        # ibm_blk_disk_name for odf install
        ibm_operations.install_ocp_resources(resources=resources, ibm_blk_disk_name=ibm_operations.get_ibm_disks_blk_name())
        ibm_operations.ibm_disconnect()
        logger.info(f'End IBM OCP resources installation')

    @logger_time_stamp
    def update_ci_status():
        """
        This method update ci status
        :return:
        """
        ci_minutes_time = environment_variables_dict.get('ci_minutes_time', '')
        benchmark_operator_id = environment_variables_dict.get('benchmark_operator_id', '')
        benchmark_wrapper_id = environment_variables_dict.get('benchmark_wrapper_id', '')
        benchmark_runner = Workloads()
        benchmark_runner.update_ci_status(status=ci_status, ci_minutes_time=int(ci_minutes_time), benchmark_operator_id=benchmark_operator_id, benchmark_wrapper_id=benchmark_wrapper_id)

    @logger_time_stamp
    def run_benchmark_operator_workload():
        """
        This method run benchmark-operator workload
        :return:
        """
        # benchmark-operator node selector
        if environment_variables_dict.get('pin_node_benchmark_operator'):
            benchmark_operator_workload.update_node_selector(runner_path=environment_variables_dict.get('runner_path', ''),
                                                             yaml_path='benchmark-operator/config/manager/manager.yaml',
                                                             pin_node='pin_node_benchmark_operator')
        return benchmark_operator_workload.run()

    @logger_time_stamp
    def run_benchmark_runner_workload():
        """
        This method run benchmark-runner workload
        :return:
        """
        # benchmark-runner node selector
        return benchmark_runner_workload.run()

    @logger_time_stamp
    def run_clusterbuster_workload():
        """
        This method run clusterbuster workload
        :return:
        """
        # benchmark-runner node selector
        return clusterbuster_workload.run()

    success = True
    # azure_cluster_start_stop
    if azure_cluster_stop or azure_cluster_start:
        azure_cluster_start_stop()
    # install_ocp_version
    elif install_ocp_version:
        ibm_operations = IBMOperations(user=provision_user)
        ibm_operations.ibm_connect()
        install_step = environment_variables_dict.get('install_step', '')
        if not ibm_operations.version_already_installed() and install_step == 'run_ibm_ocp_installer':
            install_ocp(ibm_operations=ibm_operations, step=install_step)
        elif install_step == 'verify_install_complete':
            install_ocp(ibm_operations=ibm_operations, step=install_step)
        else:
            logger.info(f'{ibm_operations.get_ocp_server_version().strip()} version already installed, skip OCP installation')
    # install_ocp_resource
    elif install_ocp_resources:
        install_resources()
    elif ci_status == 'pass' or ci_status == 'failed':
        update_ci_status()
    elif is_benchmark_operator_workload:
        success = run_benchmark_operator_workload()
    elif is_benchmark_runner_workload:
        success = run_benchmark_runner_workload()
    elif is_clusterbuster_workload:
        success = run_clusterbuster_workload()
    else:
        logger.error(f"empty workload, choose one from the list: {environment_variables.workloads_list}")
        raise SystemExit(SYSTEM_EXIT_UNKNOWN_EXECUTION_TYPE)

    if not success:
        logger.error("Benchmark failed.")
        raise SystemExit(SYSTEM_EXIT_BENCHMARK_FAILED)


main()
