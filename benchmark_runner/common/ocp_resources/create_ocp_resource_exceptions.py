
class OCError(Exception):
    """ Base class for all OC error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class OCPResourceNotCreateTimeout(OCError):
    """This exception return resource create timeout error"""
    def __init__(self, resource):
        self.message = f'The {resource} resource was not created'
        super(OCPResourceNotCreateTimeout, self).__init__(self.message)


class KataInstallationFailed(OCError):
    """This exception returns failure to install sandboxed containers"""
    def __init__(self, reason):
        self.message = f'Installation of sandboxed containers failed: {reason}'
        super(KataInstallationFailed, self).__init__(self.message)


class ExecFailed(OCError):
    """exec command on pod failed"""
    def __init__(self, pod, command, reason):
        self.message = f'exec {command} on {pod} failed: {reason}'
        super(ExecFailed, self).__init__(self.message)


class PodFailed(OCError):
    """exec command on pod failed"""
    def __init__(self, pod):
        self.message = f'pod {pod} failed'
        super(PodFailed, self).__init__(self.message)
