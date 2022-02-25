
import subprocess
from benchmark_runner.common.logger.logger_time_stamp import logger
from benchmark_runner.common.ssh.ssh_exceptions import SSHSubprocessError
from benchmark_runner.main.environment_variables import environment_variables


class SSH:
    """
    This class run local SSH commands
    """
    def __init__(self):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.timeout = int(self.__environment_variables_dict.get('timeout', 300))

    def run(self, cmd: str, is_check: bool = False, background: bool = False):
        """
        This method run shell commands
        :param background: run ssh in background
        :param cmd:
        :param is_check:run check command
        :return:
        """
        try:
            if background:
                output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            elif is_check:
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
            logger.error(f'subprocess Status : FAIL: {err.returncode} {err.output}')
            raise SSHSubprocessError()
        except Exception as err:
             raise err
