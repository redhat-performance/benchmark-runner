
class IBMError(Exception):
    """ Base class for all IBM error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class IBMMachineNotLoad(IBMError):
    """
    This class exception is for Subprocess
    """
    def __init__(self):
        self.message = 'The IBM machine did not load'
        super(IBMMachineNotLoad, self).__init__(self.message)
