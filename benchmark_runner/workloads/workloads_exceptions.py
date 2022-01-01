
class BenchmarkRunnerError(Exception):
    """ Base class for all benchmark runner error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class OCSNonInstalled(BenchmarkRunnerError):
    """
    This class is error that OCS operator is not installed
    """
    def __init__(self):
        self.message = "OCS is not installed, set 'OCS_PVC' to False"
        super(OCSNonInstalled, self).__init__(self.message)
