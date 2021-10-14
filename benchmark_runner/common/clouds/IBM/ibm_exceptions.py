
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


class MissingMasterNodes(IBMError):
    """
    This class exception is for missing master nodes
    """
    def __init__(self):
        self.message = 'There are no master nodes'
        super(MissingMasterNodes, self).__init__(self.message)


class MissingWorkerNodes(IBMError):
    """
    This class exception is for missing worker nodes
    """
    def __init__(self):
        self.message = 'There are no worker nodes'
        super(MissingWorkerNodes, self).__init__(self.message)