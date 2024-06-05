
class PrometheusSnapshotError(Exception):
    """
    Base class for all Prometheus snapshot exceptions
    """
    pass


class PrometheusSnapshotAlreadyStarted(PrometheusSnapshotError):
    """Snapshot already started"""
    def __init__(self):
        self.message = f'Attempt to start Prometheus snapshot when it was already started'
        super(PrometheusSnapshotAlreadyStarted, self).__init__(self.message)


class PrometheusSnapshotNotStarted(PrometheusSnapshotError):
    """Snapshot not started"""
    def __init__(self):
        self.message = f'Attempt to retrieve Prometheus snapshot when it was not started'
        super(PrometheusSnapshotNotStarted, self).__init__(self.message)


class PrometheusSnapshotAlreadyRetrieved(PrometheusSnapshotError):
    """Snapshot was already retrieved"""
    def __init__(self):
        self.message = f'Attempt to retrieve Prometheus snapshot when it was already retrieved'
        super(PrometheusSnapshotAlreadyRetrieved, self).__init__(self.message)
