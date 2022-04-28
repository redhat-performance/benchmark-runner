
class BenchmarkOperatorError(Exception):
    """ Base class for all benchmark operator error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class ODFNonInstalled(BenchmarkOperatorError):
    """
    This class is error that ODF operator is not installed
    """
    def __init__(self):
        self.message = "ODF is not installed, set 'ODF_PVC' to False"
        super(ODFNonInstalled, self).__init__(self.message)


class PrometheusSnapshotFailed(BenchmarkOperatorError):
    """
    Prometheus snapshot failed
    """
    def __init__(self, err):
        self.message = f'Prometheus snapshot failed: {err}'
        super(PrometheusSnapshotFailed, self).__init__(self.message)
