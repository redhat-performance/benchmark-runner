
class BenchmarkRunnerError(Exception):
    """ Base class for all benchmark runner error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class CNVNotInstalled(BenchmarkRunnerError):
    """
    This class raises an error that CNV operator is not installed
    """
    def __init__(self, workload):
        self.message = f"{workload} requires CNV to be installed"
        super(CNVNotInstalled, self).__init__(self.message)


class KataNotInstalled(BenchmarkRunnerError):
    """
    This class raises an error that Kata operator is not installed
    """
    def __init__(self, workload):
        self.message = f"{workload} requires Kata to be installed"
        super(KataNotInstalled, self).__init__(self.message)


class ODFNotInstalled(BenchmarkRunnerError):
    """
    This class raises an error that ODF operator is not installed
    """
    def __init__(self, workload):
        self.message = f"{workload} requires ODF to be installed, set 'ODF_PVC' to False to run with Ephemeral"
        super(ODFNotInstalled, self).__init__(self.message)


class MissingScaleNodes(BenchmarkRunnerError):
    """
    This class raises an error for missing scale nodes
    """
    def __init__(self):
        self.message = "Missing scale nodes"
        super(MissingScaleNodes, self).__init__(self.message)


class MissingRedis(BenchmarkRunnerError):
    """
    This class raises an error for missing redis for scale synchronization
    """
    def __init__(self):
        self.message = "Missing redis"
        super(MissingRedis, self).__init__(self.message)


class MissingVMs(BenchmarkRunnerError):
    """
    This class raises an error for missing VMs
    """
    def __init__(self):
        self.message = "Missing running VMs"
        super(MissingVMs, self).__init__(self.message)
