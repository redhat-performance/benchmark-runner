
class BenchmarkOperatorError(Exception):
    """ Base class for all benchmark operator error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class CNVNotInstalled(BenchmarkOperatorError):
    """
    This class raises an error that CNV operator is not installed
    """
    def __init__(self, workload):
        self.message = f"{workload} requires CNV to be installed"
        super(CNVNotInstalled, self).__init__(self.message)


class KataNotInstalled(BenchmarkOperatorError):
    """
    This class raises an error that Kata operator is not installed
    """
    def __init__(self, workload):
        self.message = f"{workload} requires Kata to be installed"
        super(KataNotInstalled, self).__init__(self.message)


class ODFNotInstalled(BenchmarkOperatorError):
    """
    This class raises an error that ODF operator is not installed
    """
    def __init__(self, workload):
        self.message = f"{workload} requires ODF to be installed, set 'ODF_PVC' to False to run with Ephemeral"
        super(ODFNotInstalled, self).__init__(self.message)


class EmptyLSOPath(BenchmarkOperatorError):
    """
    This class raises an error that LSO path is empty
    """
    def __init__(self):
        self.message = "LSO path is empty"
        super(EmptyLSOPath, self).__init__(self.message)


class PrometheusSnapshotFailed(BenchmarkOperatorError):
    """
    This class raises an error when Prometheus snapshot failed
    """
    def __init__(self, err):
        self.message = f'Prometheus snapshot failed: {err}'
        super(PrometheusSnapshotFailed, self).__init__(self.message)
