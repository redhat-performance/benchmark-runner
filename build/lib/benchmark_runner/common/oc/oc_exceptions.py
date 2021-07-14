
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


class VMTerminateTimeout(OCError):
    """This exception return pod terminate timeout error"""
    def __init__(self, pod_name):
        self.message = f'VM name: {pod_name} is not terminated'
        super(VMTerminateTimeout, self).__init__(self.message)


class VMNameNotExist(OCError):
    """This exception return pod name does not exist"""
    def __init__(self, pod_name):
        self.message = f'VM name: {pod_name} does not exist'
        super(VMNameNotExist, self).__init__(self.message)


class YAMLNotExist(OCError):
    """This exception return pod name does not exist"""
    def __init__(self, yaml):
        self.message = f'YAML file: {yaml} does not exist'
        super(YAMLNotExist, self).__init__(self.message)




