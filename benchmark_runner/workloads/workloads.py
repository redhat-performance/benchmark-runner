
import inspect
import importlib

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class Workloads(WorkloadsOperations):
    """
    This class create workload
    """
    def __init__(self):
        """
        All inherit from WorkloadsOperations
        """
        super().__init__()

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """
        self.initialize_workload()
        # kata use pod module - replace kata to pod
        workload = self._workload.replace('kata', 'pod')
        # extract workload module and class
        workload_module = importlib.import_module(f'benchmark_runner.workloads.{workload}')
        for cls in inspect.getmembers(workload_module, inspect.isclass):
            if workload.replace('_', '').lower() == cls[0].lower():
                cls[1]().run()
        self.finalize_workload()
