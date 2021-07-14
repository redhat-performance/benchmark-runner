
class SSHError(Exception):
    """ Base class for all SSH error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class SSHSubprocessError(SSHError):
    """
    This class exception is for Subprocess
    """
    def __init__(self):
        self.message = 'Subprocess is end with errors'
        super(SSHSubprocessError, self).__init__(self.message)
