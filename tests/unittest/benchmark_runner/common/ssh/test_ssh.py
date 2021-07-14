
from benchmark_runner.common.ssh.ssh import SSH


def test_run_cmd():
    """
    This method test run ssh cmd
    :return:
    """
    ssh = SSH()
    assert ssh.run(cmd='ls')




