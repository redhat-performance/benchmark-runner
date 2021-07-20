
import subprocess
from benchmark_runner.common.logger.logger_time_stamp import logger
from benchmark_runner.common.ssh.ssh_exceptions import SSHSubprocessError


class SSH:
    """
    This class run local SSH commands
    """
    def __init__(self, timeout: int = 300):
        self.timeout = timeout

    def run(self, cmd: str, is_check: bool = False):
        """
        This method run shell commands
        :param cmd:
        :param is_check:run check command
        :return:
        """
        try:
            if is_check:
                output = subprocess.check_output(
                    cmd,
                    stderr=subprocess.STDOUT,
                    shell=True, timeout=self.timeout,
                    universal_newlines=False)
            # execute cmd
            else:
                output = subprocess.getoutput(cmd)
            return output
        except subprocess.CalledProcessError as err:
            logger.error("subprocess Status : FAIL", err.returncode, err.output)
            raise SSHSubprocessError()
        except Exception as err:
             raise err
