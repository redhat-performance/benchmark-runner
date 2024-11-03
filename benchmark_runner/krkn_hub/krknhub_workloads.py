
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class KrknHubWorkloads(WorkloadsOperations):
    """
    This class is used to run Krkn Hub workloads.
    For more details, see the documentation: https://github.com/krkn-chaos/krkn-hub?tab=readme-ov-file#supported-chaos-scenarios.
    """

    def __init__(self):
        super().__init__()
        # environment variables
        self.__namespace = self._environment_variables_dict.get('namespace', '')
        self.__krknhub_workload = self._environment_variables_dict.get('krknhub_workload', '')
        self.__krknhub_environment_variables = self._environment_variables_dict.get('krknhub_environment_variables', '')
        self.__ssh = SSH()
        self.__krknhub_pod_name = 'bm'

    @logger_time_stamp
    def delete_all(self):
        """
        This method deletes Krkn Hub resources
        :return:
        """
        self.__ssh.run(cmd=f'podman rm -f {self.__krknhub_pod_name}')

    def initialize_workload(self):
        """
        This method includes all the initialization of Krkn Hub workload
        :return:
        """
        self.delete_all()
        if self._enable_prometheus_snapshot:
            self.start_prometheus()

    def finalize_workload(self):
        """
        This method includes all the finalization of Krkn Hub workload
        :return:
        """
        if self._enable_prometheus_snapshot:
            self.end_prometheus()
        self.delete_all()

    @logger_time_stamp
    def run_workload(self):
        """
        This method runs krkn hub workload
        :return:
        """
        logger.info(f'run krkn-hub: {self.__krknhub_workload}')
        pod_log_path = f'{self._run_artifacts_path}/{self.__krknhub_workload}_pod.log'
        workload_command = f'{self.__krknhub_environment_variables}; podman run --name={self.__krknhub_pod_name} --net=host --env-host=true -v /root/.kube/config:/home/krkn/.kube/config:Z quay.io/krkn-chaos/krkn-hub:{self.__krknhub_workload} > {pod_log_path}'
        logger.info(workload_command)
        self.__ssh.run(workload_command)

    @logger_time_stamp
    def run(self):
        """
        This method runs Krkn Hub workloads
        :return:
        """
        try:
            # initialize workload
            self.initialize_workload()
            # Run workload
            self.run_workload()
            # finalize workload
            self.finalize_workload()
        # when error raised finalize workload
        except Exception:
            logger.info(f'{self._workload} workload raised an exception')
            # finalize workload
            self.finalize_workload()
            return False

        return True
