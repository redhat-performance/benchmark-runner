
import inspect
import importlib

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class Workloads(WorkloadsOperations):
    """
    This class run workload
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

        # kata use pod module - replace kata to pod
        workload = self._workload.replace('kata', 'pod')
        # load the workload module before doing anything else (in case it fails)
        workload_module = importlib.import_module(f'benchmark_runner.workloads.{workload}')

        try:
            if not self._verification_only:
                self.initialize_workload()
            success = True
            # extract workload module and class
            for cls in inspect.getmembers(workload_module, inspect.isclass):
                if workload.replace('_', '').lower() == cls[0].lower():
                    if cls[1]().run() == False:
                        success = False
            if not self._verification_only:
                self.finalize_workload()
            return success

        except Exception as err:
            self.finalize_workload()
            raise err
