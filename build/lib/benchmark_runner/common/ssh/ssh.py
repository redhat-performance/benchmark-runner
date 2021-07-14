
import subprocess
from benchmark_runner.common.logger.logger_time_stamp import logger
from benchmark_runner.common.ssh.ssh_exceptions import SSHSubprocessError


class SSH:
    """
    This class run local SSH commands
    """
    def __init__(self, timeout: int = 300):
        self.timeout = timeout

    def run(self, cmd):
        """
        This method run shell commands
        :param cmd:
        :return:
        """
        try:
            output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                shell=True, timeout=self.timeout,
                universal_newlines=True)
            return output
        except subprocess.CalledProcessError as err:
            return ''
            #logger.error("subprocess Status : FAIL", err.returncode, err.output)
            #raise SSHSubprocessError()
        except Exception as err:
             raise err
