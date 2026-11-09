
import time
import threading

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc_exceptions import LoginFailed


class SingletonOCLogin:

    _instance = None
    _lock = threading.Lock()  # Create a class-level lock

    def __new__(cls, oc_instance):
        '''Return the singleton only after authentication succeeds.'''
        with cls._lock:  # Acquire the lock for instance creation
            if cls._instance is None:
                instance = super(SingletonOCLogin, cls).__new__(cls)
                instance.__init_instance(oc_instance)
                cls._instance = instance
            return cls._instance

    def __init_instance(self, oc_instance):
        self.__oc_instance = oc_instance  # Store reference to OC instance
        self._kubeconfig_path = oc_instance._kubeconfig_path  # Changed to protected
        self._kubeadmin_password = oc_instance._kubeadmin_password  # Changed to protected
        self._cli = oc_instance._cli  # Changed to protected
        # Inherit RETRIES and DELAY from OC instance
        self.RETRIES = oc_instance.RETRIES
        self.DELAY = oc_instance.DELAY

        # Attempt to log in during initialization
        self._login()

    @logger_time_stamp
    def _login(self):
        '''Validate an admin context or log in with a password and retries.'''
        for attempt in range(self.RETRIES):
            try:
                if self._kubeadmin_password and self._kubeadmin_password.strip():
                    self.__oc_instance.run(  # Use the run method from OC instance
                        f'{self._cli} login -u kubeadmin -p {self._kubeadmin_password}',
                        is_check=True
                    )
                    return True  # Success
                else:   # Empty or whitespace-only password.
                    try:
                        identity = self.__oc_instance.run(
                            f'{self._cli} auth whoami -ojsonpath=\'{{.status.userInfo.username}}{{"\\n"}}\'',
                            is_check=True,
                        )
                        if isinstance(identity, bytes):
                            identity = identity.decode('utf-8')
                        identity = identity.strip()
                    except Exception as error:
                        raise LoginFailed(
                            msg=('Empty KUBEADMIN_PASSWORD and KUBECONFIG authentication failed.'),
                        ) from error
                    if identity not in ('kube:admin', 'system:admin'):
                        raise LoginFailed(msg=(
                            'Empty KUBEADMIN_PASSWORD and KUBECONFIG identity is not `kube:admin` or `system:admin`.'
                        ))
                    return True
            except Exception as err:
                if (login_failed := isinstance(err, LoginFailed)) and (err.__cause__ is None):
                    raise   # Rejected KUBECONFIG identity, do not retry.
                logger.warning(f"Login attempt {attempt + 1} failed: {err}")
                if attempt < self.RETRIES - 1:
                    time.sleep(self.DELAY)
                elif login_failed:
                    raise
                else:
                    raise LoginFailed(msg="Login failed after multiple attempts") from err
