
class ClusterBusterError(Exception):
    """ Base class for all benchmark operator error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class MissingResultReport(ClusterBusterError):
    """
    This class is error for missing cluster buster report result
    """
    def __init__(self):
        self.message = "Missing cluster buster result report"
        super(MissingResultReport, self).__init__(self.message)


class MissingElasticSearch(ClusterBusterError):
    """
    This class is error for missing ElasticSearch details
    """
    def __init__(self):
        self.message = "Missing ElasticSearch details"
        super(MissingElasticSearch, self).__init__(self.message)