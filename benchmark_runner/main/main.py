
from benchmark_runner.main.environment_variables import *
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.benchmark_operator.benchmark_operator_workloads import BenchmarkOperatorWorkloads
from benchmark_runner.main.environment_variables import environment_variables

# logger
log_level = os.environ.get('log_level', 'INFO').upper()
logger.setLevel(level=log_level)


@logger_time_stamp
def main():
    """
    The main
    """
    environment_variables_dict = environment_variables.environment_variables_dict
    workload = environment_variables_dict.get('workload')
    # workload name validation
    if workload not in environment_variables.workloads_list:
        logger.info(f'Enter valid workload name {environment_variables.workloads_list}')
        raise Exception(f'Not valid workload name: {workload} \n, choose one from the list: {environment_variables.workloads_list}')

    es_host = environment_variables_dict.get('elasticsearch')
    es_port = environment_variables_dict.get('elasticsearch_port')
    kubeadmin_password = environment_variables_dict.get('kubeadmin_password')
    benchmark_operator_workload = BenchmarkOperatorWorkloads(kubeadmin_password=kubeadmin_password, es_host=es_host, es_port=es_port, workload=workload)
    benchmark_operator_workload.run_workload()


main()
