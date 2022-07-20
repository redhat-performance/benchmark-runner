
import inspect
import importlib

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class BenchmarkOperatorWorkloads(BenchmarkOperatorWorkloadsOperations):
    """
    This class contains all the custom_workloads
    """
    def __init__(self):
        super().__init__()

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """

        # kata use pod module - replace kata to pod
        workload = self._workload.replace('kata', 'pod')
        # if hammerdb split the database
        workload = f"{workload.split('_')[0]}_{workload.split('_')[1]}"
        # extract workload module and class
        workload_module = importlib.import_module(f'benchmark_runner.benchmark_operator.{workload}')

        try:
            self.initialize_workload()
            success = True
            for cls in inspect.getmembers(workload_module, inspect.isclass):
                if workload.replace('_', '').lower() == cls[0].lower():
                    if cls[1]().run() == False:
                        success = False

            self.finalize_workload()

            return success
        except Exception as err:
            self.finalize_workload()
            raise err
