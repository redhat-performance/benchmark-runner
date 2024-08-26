
class BareMetalError(Exception):
    """ Base class for all bare metal error classes.
    All exceptions raised by the Bare Metal library should inherit from this class. """
    pass


class MissingMasterNodes(BareMetalError):
    """
    This exception class is for missing master nodes
    """
    def __init__(self, missing_node: set):
        self.message = f'Missing master nodes: {missing_node}'
        super(MissingMasterNodes, self).__init__(self.message)


class MissingWorkerNodes(BareMetalError):
    """
    This exception class is for missing worker nodes.
    """
    def __init__(self, missing_node: set):
        self.message = f'Missing worker nodes: {missing_node}'
        super(MissingWorkerNodes, self).__init__(self.message)


class OCPInstallationFailed(BareMetalError):
    """
    This exception class indicates that the Bare-Metal OpenShift installation has failed
    """
    def __init__(self, logs: str):
        self.message = (f'Bare-metal OpenShift Container Platform (OCP) installation failed. '
                        f'OpenShift installer logs details: \n {logs}')
        super(OCPInstallationFailed, self).__init__(self.message)


class OCPUpgradeFailed(BareMetalError):
    """
    This exception class indicates that the Bare-Metal OpenShift upgrade has failed
    """
    def __init__(self, status: str):
        self.message = (f'Bare-metal OpenShift Container Platform (OCP) upgrade failed. '
                        f'Upgrade status: {status}')
        super(OCPUpgradeFailed, self).__init__(self.message)
