
class LoggerError(Exception):
    """ Base class for all logger error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class MethodError(LoggerError):
    """
    This class is fot method error
    """
    def __init__(self, method_name, exception):
        self.message = f'method error: {method_name}, exception: {exception}'
        super(MethodError, self).__init__(self.message)
