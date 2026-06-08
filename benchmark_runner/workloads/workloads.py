
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
        # Strip storage suffix (ephemeral/lso) and db type for module resolution
        module_workload = workload
        if workload.startswith('hammerdb_'):
            parts = workload.split('_')
            if len(parts) >= 3:
                module_workload = '_'.join(parts[:2])
        elif workload.endswith('_ephemeral') or workload.endswith('_lso') or workload.endswith('_scale'):
            module_workload = '_'.join(workload.split('_')[:-1])
        # load the workload module before doing anything else (in case it fails)
        workload_module = importlib.import_module(f'benchmark_runner.workloads.{module_workload}')

        try:
            if not self._verification_only:
                self.initialize_workload()
            success = True
            # extract workload module and class
            for cls in inspect.getmembers(workload_module, inspect.isclass):
                if module_workload.replace('_', '').lower() == cls[0].lower():
                    if cls[1]().run() == False:
                        success = False
            if not self._verification_only:
                self.finalize_workload()
            return success

        except Exception as err:
            self.finalize_workload()
            raise err
