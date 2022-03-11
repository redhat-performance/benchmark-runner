
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

        # kata use pod module - replace kata to pod
        workload = self._workload.replace('kata', 'pod')
        # load the workload module before doing anything else (in case it fails)
        workload_module = importlib.import_module(f'benchmark_runner.workloads.{workload}')

        try:
            _initialize_workload = getattr(workload_module, "initialize_workload")
            initialize_workload = lambda: _initialize_workload(self)
        except AttributeError:
            logger.info(f"{workload} module has no initialize_workload method. Using the default one.")
            initialize_workload = self.initialize_workload

        try:
            _finalize_workload = getattr(workload_module, "finalize_workload")
            finalize_workload = lambda: _finalize_workload(self)
        except AttributeError:
            logger.info(f"{workload} module has no finalize_workload method. Using the default one.")
            finalize_workload = self.finalize_workload

        try:
            initialize_workload()
            success = True
            # extract workload module and class
            for cls in inspect.getmembers(workload_module, inspect.isclass):
                if workload.replace('_', '').lower() == cls[0].lower():
                    if cls[1]().run() == False:
                        success = False

            finalize_workload()

            return success
        except Exception as err:
            finalize_workload()
            raise err
