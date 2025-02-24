
import time
import threading

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc_exceptions import LoginFailed


class SingletonOCLogin:

    _instance = None
    _lock = threading.Lock()  # Create a class-level lock

    def __new__(cls, oc_instance):
        with cls._lock:  # Acquire the lock for instance creation
            if cls._instance is None:
                cls._instance = super(SingletonOCLogin, cls).__new__(cls)
                cls._instance.__init_instance(oc_instance)
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
        try:
            self._login()
        except RuntimeError as e:
            logger.error(f"Initialization failed: {e}")
            # Handle the exception as needed (e.g., re-raise, log, etc.)

    @logger_time_stamp
    def _login(self):
        # Check for empty or whitespace-only password
        if not self._kubeadmin_password or not self._kubeadmin_password.strip():
            raise LoginFailed(msg="Empty password")

        """Logs in to the cluster with retries, ensuring only a single login per execution."""
        for attempt in range(self.RETRIES):
            try:
                if self._kubeadmin_password and self._kubeadmin_password.strip():
                    self.__oc_instance.run(  # Use the run method from OC instance
                        f'{self._cli} login -u kubeadmin -p {self._kubeadmin_password}',
                        is_check=True
                    )
                    return True  # Success
            except Exception as err:
                logger.warning(f"Login attempt {attempt + 1} failed: {err}")
                if attempt < self.RETRIES - 1:
                    time.sleep(self.DELAY)
                else:
                    raise LoginFailed(msg="Login failed after multiple attempts")
