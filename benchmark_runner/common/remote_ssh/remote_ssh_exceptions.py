
# Custom exceptions must NOT expose data including hostnames, pathnames, IP addresses, etc. (security risk)
class SshError(Exception):
    """ Base class for all SSH error classes.
        All exceptions raised by the DSS library should inherit from this class. """
    pass


class RunCommandError(SshError):
    """
    This class for run command error
    """
    def __init__(self, err):
        self.message = f'Cannot run shell command: {err}'
        super(RunCommandError, self).__init__(self.message)


class SshConnectionError(SshError):
    """
    This class for connection error
    """
    def __init__(self):
        self.message = f'Missing connection credentials'
        super(SshConnectionError, self).__init__(self.message)


class SshConnectionTimedOut(SshError):
    """
    This class for connection timeout
    """
    def __init__(self, err):
        self.message = f'Timed Out : {err}'
        super(SshConnectionTimedOut, self).__init__(self.message)


class SshConnectionFailure(SshError):
    """
    This class for connection failure
    """
    def __init__(self, err):
        self.message = f'Server connection failure: {err}'
        super(SshConnectionFailure, self).__init__(self.message)


class PathNotExist(SshError):
    """
    This class error for folder that not exist
    """
    def __init__(self, err):
        self.message = f'{err}'
        super(PathNotExist, self).__init__(self.message)


class FileNotExist(SshError):
    """
    This class error for file that not exist
    """
    def __init__(self, err):
        self.message = f'{err}'
        super(PathNotExist, self).__init__(self.message)


class SFTPException(SshError):
    """
    This class through sftp exception
    """
    def __init__(self, err):
        self.message = {err}
        super(PathNotExist, self).__init__(self.message)


class IllegalFilename(SshError):
    """
    This class through Illegal file name error
    """
    def __init__(self, err):
        self.message = {err}
        super(PathNotExist, self).__init__(self.message)
