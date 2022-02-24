
class BenchmarkRunnerError(Exception):
    """ Base class for all benchmark runner error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class ODFNonInstalled(BenchmarkRunnerError):
    """
    This class is error that ODF operator is not installed
    """
    def __init__(self):
        self.message = "ODF is not installed, set 'ODF_PVC' to False"
        super(ODFNonInstalled, self).__init__(self.message)
