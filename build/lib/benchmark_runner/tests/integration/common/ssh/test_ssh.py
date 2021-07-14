
import pytest
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.common.ssh.ssh_exceptions import SSHSubprocessError


def test_run_cmd():
    """
    This method test run ssh cmd
    :return:
    """
    ssh = SSH()
    assert ssh.run(cmd='ls')




