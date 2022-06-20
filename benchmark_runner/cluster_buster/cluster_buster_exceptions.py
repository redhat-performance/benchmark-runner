
class ClusterBusterError(Exception):
    """ Base class for all benchmark operator error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class MissingResultReport(ClusterBusterError):
    """
    This class is error that ODF operator is not installed
    """
    def __init__(self):
        self.message = "Missing cluster buster result report"
        super(MissingResultReport, self).__init__(self.message)


