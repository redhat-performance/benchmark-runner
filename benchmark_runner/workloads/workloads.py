
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations
from benchmark_runner.workloads.vdbench_pod import VdbenchPod
from benchmark_runner.workloads.vdbench_vm import VdbenchVM


class Workloads(WorkloadsOperations):
    """
    This class create workload
    """
    def __init__(self):
        """
        All inherit from WorkloadsOperations
        """
        super().__init__()

    @typechecked
    @logger_time_stamp
    def vdbench_pod(self, name: str = ''):
        """
        This method run vdbench pod workload
        :return:
        """
        if name == '':
            name = self.vdbench_pod.__name__
        run = VdbenchPod()
        run.vdbench_pod(name=name)

    @logger_time_stamp
    def vdbench_kata(self):
        """
        This method run vdbench kata workload
        :return:
        """
        self.vdbench_pod(name=self.vdbench_kata.__name__)

    @logger_time_stamp
    def vdbench_vm(self):
        """
        This method run vdbench vm workload
        :return:
        """
        run = VdbenchVM()
        run.vdbench_vm()

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """
        self.initialize_workload()
        workloads = Workloads()
        class_method = getattr(workloads, self._workload)
        class_method()
        self.finalize_workload()



