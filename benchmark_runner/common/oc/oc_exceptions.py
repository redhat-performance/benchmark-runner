
class OCError(Exception):
    """ Base class for all OC error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class LoginFailed(OCError):
    """This exception return login failed error"""
    def __init__(self):
        self.message = f'Login error, check credentials'
        super(LoginFailed, self).__init__(self.message)


class PodNotCreateTimeout(OCError):
    """This exception return pod create timeout error"""
    def __init__(self, pod_name):
        self.message = f'Pod name: {pod_name} does not create'
        super(PodNotCreateTimeout, self).__init__(self.message)


class PodNotInitializedTimeout(OCError):
    """This exception return pod initialized timeout error"""
    def __init__(self, workload):
        self.message = f'Pod : {workload} does not ready'
        super(PodNotInitializedTimeout, self).__init__(self.message)


class PodNotReadyTimeout(OCError):
    """This exception return pod ready timeout error"""
    def __init__(self, workload):
        self.message = f'Pod : {workload} does not ready'
        super(PodNotReadyTimeout, self).__init__(self.message)


class PodNotCompletedTimeout(OCError):
    """This exception return pod completed timeout error"""
    def __init__(self, workload):
        self.message = f'Pod with label: {workload} does not completed'
        super(PodNotCompletedTimeout, self).__init__(self.message)


class PodTerminateTimeout(OCError):
    """This exception return pod terminate timeout error"""
    def __init__(self, pod_name):
        self.message = f'Pod name: {pod_name} does not terminate'
        super(PodTerminateTimeout, self).__init__(self.message)


class PodNameNotExist(OCError):
    """This exception return pod name does not exist"""
    def __init__(self, pod_name):
        self.message = f'Pod name: {pod_name} does not exist'
        super(PodNameNotExist, self).__init__(self.message)


class VMNotCreateTimeout(OCError):
    """This exception return pod create timeout error"""
    def __init__(self, pod_name):
        self.message = f'VM name: {pod_name} is not created'
        super(VMNotCreateTimeout, self).__init__(self.message)


class VMDeleteTimeout(OCError):
    """This exception return vm delete timeout error"""
    def __init__(self, vm_name):
        self.message = f'VM name: {vm_name} is not deleted'
        super(VMDeleteTimeout, self).__init__(self.message)


class VMNameNotExist(OCError):
    """This exception return pod name does not exist"""
    def __init__(self, vm_name):
        self.message = f'VM name: {vm_name} does not exist'
        super(VMNameNotExist, self).__init__(self.message)


class YAMLNotExist(OCError):
    """This exception return pod name does not exist"""
    def __init__(self, yaml):
        self.message = f'YAML file: {yaml} does not exist'
        super(YAMLNotExist, self).__init__(self.message)


class VMNotInitializedTimeout(OCError):
    """This exception return vm initialized timeout error"""
    def __init__(self, workload):
        self.message = f'VM {workload} does not ready'
        super(VMNotInitializedTimeout, self).__init__(self.message)


class VMNotReadyTimeout(OCError):
    """This exception return vm ready timeout error"""
    def __init__(self, workload):
        self.message = f'VM : {workload} does not ready'
        super(VMNotReadyTimeout, self).__init__(self.message)


class VMStateTimeout(OCError):
    """This exception indicates timeout for VM state """
    def __init__(self, vm_name, state):
        self.message = f'VM: {vm_name} does not reach to state: {state}'
        super(VMStateTimeout, self).__init__(self.message)


class VMNotCompletedTimeout(OCError):
    """This exception return vm completed error"""
    def __init__(self, workload):
        self.message = f'VM : {workload} does not completed'
        super(VMNotCompletedTimeout, self).__init__(self.message)


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


class DVStatusTimeout(OCError):
    """This exception return dv status timeout error"""
    def __init__(self, status):
        self.message = f'DV status {status} timeout'
        super(DVStatusTimeout, self).__init__(self.message)


class CSVNotCreateTimeout(OCError):
    """This exception return csv create timeout error"""
    def __init__(self, operator, namespace):
        self.message = f'{operator} CSV in namespace: {namespace} is not created'
        super(CSVNotCreateTimeout, self).__init__(self.message)


class UpgradeNotStartTimeout(OCError):
    """This exception return ocp upgrade timeout error"""
    def __init__(self, version):
        self.message = f"OCP upgrade to {version} didn't start"
        super(UpgradeNotStartTimeout, self).__init__(self.message)


class OperatorInstallationTimeout(OCError):
    """This exception return operator installation timeout error"""
    def __init__(self, operator, version, namespace):
        self.message = f"{operator} operator installation to: {version} in namespace: {namespace} didn't complete"
        super(OperatorInstallationTimeout, self).__init__(self.message)


class OperatorUpgradeTimeout(OCError):
    """This exception return operator upgrade timeout error"""
    def __init__(self, operator, version, namespace):
        self.message = f"{operator} operator upgrade to: {version} in namespace: {namespace} didn't complete"
        super(OperatorUpgradeTimeout, self).__init__(self.message)


class ODFHealthCheckTimeout(OCError):
    """This exception return odf healthcheck timeout error"""
    def __init__(self, message: str):
        self.message = message
        super(ODFHealthCheckTimeout, self).__init__(self.message)


class NodeNotReady(OCError):
    """This exception indicates a node not ready due to a timeout error"""
    def __init__(self, nodes_status: dict):
        self.message = f"Node not ready: {nodes_status}"
        super(NodeNotReady, self).__init__(self.message)
