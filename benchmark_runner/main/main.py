
import time

from benchmark_runner.main.environment_variables import *
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.clouds.Azure.azure_operations import AzureOperations

# logger
log_level = os.environ.get('log_level', 'INFO').upper()
logger.setLevel(level=log_level)

# venv
# python -m venv venv
# . venv/bin/activate


@logger_time_stamp
def main():
    """
    The main of benchmark-runner handle Azure operations or Workload runs
    """
    environment_variables_dict = environment_variables.environment_variables_dict
    azure_cluster_stop = environment_variables_dict.get('azure_cluster_stop', '')
    azure_cluster_start = environment_variables_dict.get('azure_cluster_start', '')
    # Azure operations
    if azure_cluster_stop or azure_cluster_start:
        azure_operation = AzureOperations(azure_clientid=environment_variables_dict.get('azure_clientid', ''),
                                          azure_secret=environment_variables_dict.get('azure_secret', ''),
                                          azure_tenantid=environment_variables_dict.get('azure_tenantid', ''),
                                          azure_subscriptionid=environment_variables_dict.get('azure_subscriptionid', ''),
                                          azure_resource_group_name=environment_variables_dict.get('azure_resource_group_name', ''))
        azure_vm_name = (environment_variables_dict.get('azure_vm_name', ''))
        if azure_cluster_start:
            print(azure_operation.start_vm(vm_name=azure_vm_name))
        elif azure_cluster_stop:
            print(azure_operation.stop_vm(vm_name=azure_vm_name))
    # Workloads
    else:
        workload = environment_variables_dict.get('workload', '')
        # workload name validation
        if workload not in environment_variables.workloads_list:
            logger.info(f'Enter valid workload name {environment_variables.workloads_list}')
            raise Exception(f'Not valid workload name: {workload} \n, choose one from the list: {environment_variables.workloads_list}')

        es_host = environment_variables_dict.get('elasticsearch', '')
        es_port = environment_variables_dict.get('elasticsearch_port', '')
        kubeadmin_password = environment_variables_dict.get('kubeadmin_password', '')
        benchmark_operator_workload = BenchmarkOperatorWorkloads(kubeadmin_password=kubeadmin_password, es_host=es_host, es_port=es_port)
        # benchmark-operator node selector
        if environment_variables_dict.get('pin_node_benchmark_operator'):
            benchmark_operator_workload.update_node_selector(runner_path=environment_variables_dict.get('runner_path', ''),
                                                             yaml_path='benchmark-operator/config/manager/manager.yaml',
                                                             pin_node='pin_node_benchmark_operator')
        benchmark_operator_workload.run_workload(workload=workload)


main()

