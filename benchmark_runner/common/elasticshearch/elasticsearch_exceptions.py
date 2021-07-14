
class ElasticSearchError(Exception):
    """ Base class for all ElasticSearch error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class ElasticSearchDataNotUploaded(ElasticSearchError):
    """This exception return elastic search not uploaded error"""
    def __init__(self):
        self.message = f'Data did not upload to elastic search'
        super(ElasticSearchDataNotUploaded, self).__init__(self.message)

