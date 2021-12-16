
class BenchmarkOperatorError(Exception):
    """ Base class for all benchmark operator error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class OCSNonInstalled(BenchmarkOperatorError):
    """
    This class is error that OCS operator is not installed
    """
    def __init__(self):
        self.message = "OCS is not installed, set 'OCS_PVC' to False"
        super(OCSNonInstalled, self).__init__(self.message)


class SystemMetricsRequiredElasticSearch(BenchmarkOperatorError):
    """
    This class for raise error when running system metrics without ElasticSearch
    """
    def __init__(self):
        self.message = "System metrics is required ElasticSearch, set 'SYSTEM_METRICS' to False"
        super(SystemMetricsRequiredElasticSearch, self).__init__(self.message)


class PrometheusSnapshotFailed(BenchmarkOperatorError):
    """
    Prometheus snapshot failed
    """
    def __init__(self, err):
        self.message = f'Prometheus snapshot failed: {err}'
        super(PrometheusSnapshotFailed, self).__init__(self.message)
