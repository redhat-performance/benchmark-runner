
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations
from benchmark_runner.benchmark_operator.stressng_pod import StressngPod
from benchmark_runner.benchmark_operator.stressng_vm import StressngVM
from benchmark_runner.benchmark_operator.uperf_pod import UperfPod
from benchmark_runner.benchmark_operator.uperf_vm import UperfVM
from benchmark_runner.benchmark_operator.hammerdb_pod import HammerdbPod
from benchmark_runner.benchmark_operator.hammerdb_vm import HammerdbVM


class BenchmarkOperatorWorkloads(BenchmarkOperatorWorkloadsOperations):
    """
    This class contains all the custom_workloads
    """
    def __init__(self):
        super().__init__()
        self.__workload = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''

    @typechecked
    @logger_time_stamp
    def stressng_pod(self, name: str = ''):
        """
        This method run stressng workload
        :return:
        """
        if name == '':
            name = self.stressng_pod.__name__
        run = StressngPod()
        run.stressng_pod(name=name)

    @logger_time_stamp
    def stressng_kata(self):
        """
        This method run stressng kata workload
        :return:
        """
        self.stressng_pod(name=self.stressng_kata.__name__)

    @logger_time_stamp
    def stressng_vm(self):
        """
        This method run stressng vm workload
        :return:
        """
        run = StressngVM()
        run.stressng_vm()

    @typechecked
    @logger_time_stamp
    def uperf_pod(self, name: str = ''):
        """
        This method run uperf workload
        :return:
        """
        if name == '':
            name = self.uperf_pod.__name__
        run = UperfPod()
        run.uperf_pod(name=name)

    @logger_time_stamp
    def uperf_kata(self):
        """
        This method run uperf kata workload
        :return:
        """
        self.uperf_pod(name=self.uperf_kata.__name__)

    @logger_time_stamp
    def uperf_vm(self):
        """
        This method run uperf vm workload
        :return:
        """
        run = UperfVM()
        run.uperf_vm()

    @typechecked
    @logger_time_stamp
    def hammerdb_pod(self, database: str, name: str = ''):
        """
        This method run hammerdb pod workload
        :return:
        """
        if name == '':
            name = self.hammerdb_pod.__name__
        run = HammerdbPod()
        run.hammerdb_pod(database=database, name=name)

    @typechecked
    @logger_time_stamp
    def hammerdb_kata(self, database: str):
        """
        This method run hammerdb kata workload
        :return:
        """
        self.hammerdb_pod(database=database, name=self.hammerdb_kata.__name__)

    @typechecked
    @logger_time_stamp
    def hammerdb_vm(self, database: str):
        """
        This method run hammerdb vm workload
        :return:
        """
        run = HammerdbVM()
        run.hammerdb_vm(database=database)

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """
        self.initialize_workload()
        workload_name = self._workload.split('_')
        benchmark_operator_workloads = BenchmarkOperatorWorkloads()
        if 'hammerdb' in self._workload:
            class_method = getattr(benchmark_operator_workloads, f'{workload_name[0]}_{workload_name[1]}')
            class_method(database=workload_name[2])
        else:
            class_method = getattr(benchmark_operator_workloads, self._workload)
            class_method()
        self.finalize_workload()
