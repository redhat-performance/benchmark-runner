
class EnvironmentVariablesExceptions(Exception):
    """ Base class for all environment variables error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class ParseFailed(EnvironmentVariablesExceptions):
    """Unparseable environment variable"""
    def __init__(self, message):
        self.message = message
        super(ParseFailed, self).__init__(self.message)
