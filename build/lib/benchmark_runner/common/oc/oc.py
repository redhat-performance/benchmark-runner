
import os
import time
from typeguard import typechecked
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.common.oc.oc_exceptions import PodNotCreateTimeout, PodTerminateTimeout, PodNameNotExist, LoginFailed, VMNotCreateTimeout, VMTerminateTimeout, YAMLNotExist
from benchmark_runner.common.ssh.ssh import SSH


class OC(SSH):
    """
    This class run OC commands
    """

    def __init__(self, kubeadmin_password: str = ''):
        super().__init__()
        self.__kubeadmin_password = kubeadmin_password

    def __get_uuid(self):
        """
        This method return uuid
        :return:
        """
        long_uuid = self.run("~/./oc -n my-ripsaw get benchmarks -o jsonpath='{.items[0].status.uuid}'")
        return long_uuid.split('-')[0]

    @typechecked
    def _create_async(self, yaml: str):
        """
        This method create yaml in async
        :param yaml:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'~/./oc create -f {yaml}')
        else:
            raise YAMLNotExist(yaml)

    @typechecked
    def _delete_async(self, yaml: str):
        """
        This method delete yaml in async
        :param yaml:
        :return:
        """
        if os.path.isfile(yaml):
            return self.run(f'~/./oc delete -f {yaml}')
        else:
            raise YAMLNotExist(yaml)

    @typechecked
    def _get_pod_name(self, pod_name: str, namespace: str):
        """
        This method return pod name if exist or empty string
        :param pod_name:
        :param namespace:
        :return:
        """
        try:
            return self.run(f'~/./oc get -n {namespace} pods -o name | grep {pod_name}')
        except Exception as err:
            raise PodNameNotExist

    @typechecked
    def _get_vmi_name(self, vm_name: str, namespace: str):
        """
        This method return pod name if exist or empty string
        :return:
        """
        try:
            return self.run(f'~/./oc get -n {namespace} vmi -o name | grep {vm_name}')
        except Exception as err:
            raise PodNameNotExist

    @logger_time_stamp
    def get_long_uuid(self):
        """
        This method return uuid
        :return:
        """
        long_uuid = self.run("~/./oc -n my-ripsaw get benchmarks -o jsonpath='{.items[0].status.uuid}'")
        return long_uuid

    @logger_time_stamp
    def login(self):
        """
        This method login to the cluster
        :return:
        """

        try:
            if self.__kubeadmin_password:
                return self.run(f'~/./oc login -u kubeadmin -p {self.__kubeadmin_password}')
            else:
                raise LoginFailed
        except Exception as err:
            raise LoginFailed

    @logger_time_stamp
    def get_pods(self):
        """
        This method get pods
        :return:
        """
        return self.run('~/./oc get pods')

    @logger_time_stamp
    def get_vmi(self):
        """
        This method get vmi
        :return:
        """
        return self.run('~/./oc get vmi')

    @typechecked
    @logger_time_stamp
    def wait_for_pod_create(self, pod_name: str, namespace: str = "my-ripsaw", timeout: int = 300, sleep_time: int = 10):
        """
        This method is wait till pod name is creating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param sleep_time:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self._get_pod_name(pod_name, namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise PodNotCreateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_create(self, vm_name: str, namespace: str = "my-ripsaw", timeout: int = 300, sleep_time: int = 10):
        """
        This method is wait till vm name is creating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param sleep_time:
        :param timeout:
        :return: True if getting pod name or raise PodNameError
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if self._get_vmi_name(vm_name, namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise VMNotCreateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def wait_for_pod_terminate(self, pod_name: str, namespace: str = "my-ripsaw", timeout: int = 300, sleep_time: int = 10):
        """
        This method is wait till pod name is terminating or throw exception after timeout
        :param namespace:
        :param pod_name:
        :param sleep_time:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if not self._get_pod_name(pod_name, namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise PodTerminateTimeout(pod_name)

    @typechecked
    @logger_time_stamp
    def wait_for_vm_terminate(self, vm_name: str, namespace: str = "my-ripsaw", timeout: int = 300, sleep_time: int = 10):
        """
        This method is wait till vm name is terminating or throw exception after timeout
        :param vm_name:
        :param namespace:
        :param sleep_time:
        :param timeout:
        :return: True if pod name terminated or raise
        """
        current_wait_time = 0
        while current_wait_time <= timeout:
            if not self._get_vmi_name(vm_name, namespace):
                return True
            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise VMTerminateTimeout(vm_name)

    @typechecked
    @logger_time_stamp
    def create_pod_sync(self, yaml: str, pod_name: str, namespace: str = 'my-ripsaw', timeout: int = 300):
        """
        This method create pod yaml in async
        :param namespace:
        :param timeout:
        :param pod_name:
        :param yaml:
        :return:
        """
        self._create_async(yaml)
        return self.wait_for_pod_create(pod_name=pod_name, namespace=namespace, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def create_vm_sync(self, yaml: str, vm_name: str, timeout: int = 300):
        """
        This method create vm yaml in async
        :param timeout:
        :param vm_name:
        :param yaml:
        :return:
        """
        self._create_async(yaml)
        return self.wait_for_vm_create(vm_name=vm_name, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def delete_pod_sync(self, yaml: str, pod_name: str, namespace: str = 'my-ripsaw', timeout: int = 300):
        """
        This method delete pod yaml in async, only if exist
        :param namespace:
        :param timeout:
        :param pod_name:
        :param yaml:
        :return:
        """
        if self._get_pod_name(pod_name, namespace):
            self._delete_async(yaml)
            return self.wait_for_pod_terminate(pod_name=pod_name, namespace=namespace, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def delete_vm_sync(self, yaml: str, vm_name: str, namespace: str = 'my-ripsaw', timeout: int = 300):
        """
        This method delete vm yaml in async, only if exist
        :param namespace:
        :param timeout:
        :param vm_name:
        :param yaml:
        :return:
        """
        if self._get_vmi_name(vm_name, namespace):
            self._delete_async(yaml)
            return self.wait_for_vm_terminate(vm_name=vm_name, namespace=namespace, timeout=timeout)

    @typechecked
    @logger_time_stamp
    def wait_for_initialized(self, label: str, status: str = 'Initialized', label_uuid: bool = True, namespace: str = 'my-ripsaw', timeout: int = 300):
        """
        This method wait to pod to be initialized
        :param namespace:
        :param label:
        :param status:
        :param label_uuid: The label include uuid
        :param timeout:
        :return:
        """
        if label_uuid:
            return self.run(
                f"~/./oc --namespace {namespace} wait --for=condition={status} pod -l {label}-{self.__get_uuid()} --timeout={timeout}s")
        else:
            return self.run(
                f"~/./oc --namespace {namespace} wait --for=condition={status} pod -l {label} --timeout={timeout}s")

    @typechecked
    @logger_time_stamp
    def wait_for_ready(self, label: str, status: str = 'ready', label_uuid: bool = True, namespace: str = 'my-ripsaw', timeout: int = 300):
        """
        This method wait to pod to be ready
        :param namespace:
        :param label:
        :param status:
        :param label_uuid:  The label include uuid
        :param timeout:
        :return:
        """
        if label_uuid:
            return self.run(
                f"~/./oc --namespace {namespace} wait --for=condition={status} pod -l {label}-{self.__get_uuid()} --timeout={timeout}s")
        else:
            return self.run(
                f"~/./oc --namespace {namespace} wait --for=condition={status} pod -l {label} --timeout={timeout}s")
    @typechecked
    @logger_time_stamp
    def wait_for_completed(self, label: str, namespace: str = 'my-ripsaw', timeout: int = 500):
        """
        This method wait to pod to be completed
        :param namespace:
        :param label:
        :param timeout:
        :return:
        """
        return self.run(
            f"~/./oc --namespace {namespace} wait --for=condition=complete -l {label}-{self.__get_uuid()} jobs --timeout={timeout}s")
