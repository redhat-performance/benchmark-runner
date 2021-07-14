
from benchmark_runner.main.environment_variables import *
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from benchmark_runner.main.environment_variables import environment_variables_dict, workloads_list

# logger
log_level = os.environ.get('log_level', 'INFO').upper()
logger.setLevel(level=log_level)


@logger_time_stamp
def main():
    """
    The main
    """
    workload_name = environment_variables_dict.get('workload')
    # workload name validation
    if workload_name not in workloads_list:
        logger.info(f'Enter valid workload name {workloads_list}')
        raise Exception(f'Not valid workload name: {workload_name} \n, choose one from the list: {workloads_list}')

    es_host = environment_variables_dict.get('elasticsearch')
    es_port = environment_variables_dict.get('elasticsearch_port')
    kubeadmin_password = environment_variables_dict.get('kubeadmin_password')
    benchmark_operator_workload = BenchmarkOperatorWorkloads(kubeadmin_password=kubeadmin_password, es_host=es_host, es_port=es_port)
    benchmark_operator_workload.run_workload(workload=workload_name)


main()
