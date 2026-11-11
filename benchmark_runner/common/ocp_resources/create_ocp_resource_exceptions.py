
class OCPResourceError(Exception):
    """ Base class for all OCP resource error classes. """
    pass


class OCPResourceCreationTimeout(OCPResourceError):
    """This exception returns resource creation timeout error"""
    def __init__(self, resource):
        self.message = f'The {resource} resource was not created'
        super(OCPResourceCreationTimeout, self).__init__(self.message)


class KataInstallationFailed(OCPResourceError):
    """This exception returns failure to install sandboxed containers"""
    def __init__(self, reason):
        self.message = f'Installation of sandboxed containers failed: {reason}'
        super(KataInstallationFailed, self).__init__(self.message)


class ODFInstallationFailed(OCPResourceError):
    """This exception returns failure to install ODF"""
    def __init__(self):
        self.message = f'ODF installation failed'
        super(ODFInstallationFailed, self).__init__(self.message)


class UnknownOCPResource(OCPResourceError):
    """This exception returns error for an unsupported OCP resource name"""
    def __init__(self, resource, supported_resources):
        self.message = f'Unknown OCP resource {resource!r}: expected one of {supported_resources}'
        super(UnknownOCPResource, self).__init__(self.message)
