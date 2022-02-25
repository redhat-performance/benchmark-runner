
import time
import os
import re
from typeguard import typechecked
from benchmark_runner.common.prometheus.prometheus_snapshot_exceptions import PrometheusSnapshotAlreadyStarted, PrometheusSnapshotNotStarted, PrometheusSnapshotAlreadyRetrieved
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc import OC


class PrometheusSnapshot:
    """
    Extract a Prometheus snapshot into a specified directory.
    The directory is assumed to already exist
    """

    # Constants
    # Default snapshot date/time format, similar to ISO
    prometheus_snapshot_datetime_format = '%Y_%m_%dT%H_%M_%S%z'
    # Pattern to recognize valid date/time.  If we try to get a timestamp before
    # the prometheus pod is fully initialized, we'll get an error back; this is
    # to distinguish a valid date from an error.  If the datetime format is changed,
    # this pattern may have to be changed too.
    date_fast_recognition_pattern = r'^[0-9]{4}'
    # How many times to retry getting a valid date/time before we give up
    timestamp_retries = 12
    # How long to sleep between each attempt to get the date/time
    timestamp_sleep = 5
    # Default time to wait after the prometheus pod comes up before
    # we return to the caller, to allow collection of baseline
    # metrics
    default_prewait_time = 60
    # Default time to wait after we receive the request to provide a snapshot, to allow
    # metrics data to fully settle down
    default_postwait_time = 120

    def __init__(self, oc: OC, artifacts_path: str, verbose: bool=False):
        self.__oc = oc
        self.__artifacts_path = artifacts_path
        self.__start_timestamp = None
        self.__end_timestamp = None
        self.__verbose = verbose
        self.__pod_name = 'prometheus-k8s-0'
        self.__namespace = 'openshift-monitoring'
        self.__container = 'prometheus'
        self.__format = self.prometheus_snapshot_datetime_format

    @typechecked
    def __verbose_log(self, message: str):
        """
        Log message if verbosity is enabled
        :param message:
        """
        if self.__verbose:
            logger.info(message)

    @typechecked
    def __exec(self, command: str):
        """
        Run a command on the Prometheus pod (by default)
        :param command:
        """
        return self.__oc.exec(pod_name=self.__pod_name, namespace=self.__namespace, container=self.__container, command=command)

    def __prom_timestamp(self):
        """
        Retrieve a timestamp from the prometheus pod.
        We use a timestamp from the pod because timestamps within the metrics db
        will be based on the time (including timezone) within the pod, not that on the host.
        """
        valid_timestamp = False
        pattern = self.date_fast_recognition_pattern
        retries = self.timestamp_retries
        # The prometheus pod may show as ready before the prometheus container actually
        # is ready (ready does not appear to indicate that all containers are necessarily
        # started).  So retry for up to a minute before giving up.
        while not valid_timestamp:
            timestamp = self.__exec(f"date '+{self.prometheus_snapshot_datetime_format}'")
            if re.match(pattern, timestamp):
                return timestamp
            else:
                time.sleep(self.timestamp_sleep)
                if retries <= 0:
                    return timestamp
                retries = retries - 1

    @typechecked
    @logger_time_stamp
    def prepare_for_snapshot(self, pre_wait_time: int=default_prewait_time, clear_db: bool=True):
        """
        Prepare for a prometheus database snapshot.  Must be called prior to running
        the workload.
        :param pre_wait_time:
        :param clear_db:
        """
        if self.__start_timestamp or self.__end_timestamp:
            raise PrometheusSnapshotAlreadyStarted
        if clear_db:
            self.__verbose_log(f'Deleting existing {self.__pod_name} (Prometheus snapshot) pod')
            self.__oc.terminate_pod_sync(pod_name=self.__pod_name, namespace=self.__namespace)
        self.__verbose_log(f'Waiting for {self.__pod_name} pod to reappear')
        self.__oc.wait_for_pod_ready(pod_name=self.__pod_name, namespace=self.__namespace)
        self.__start_timestamp = self.__prom_timestamp()
        self.__verbose_log(f'Waiting {pre_wait_time} seconds for Prometheus snapshot to fully initialize')
        time.sleep(pre_wait_time)

    @typechecked
    def retrieve_snapshot(self, post_wait_time: int=default_postwait_time):
        """
        Retrieve the prometheus database snapshot after running the workload.
        The filename that the snapshot is placed in is returned.
        :param post_wait_time:
        """
        if not self.__start_timestamp:
            raise PrometheusSnapshotNotStarted
        if self.__end_timestamp:
            raise PrometheusSnapshotAlreadyRetrieved
        self.__verbose_log(f'Waiting {post_wait_time} seconds for Prometheus snapshot to complete')
        time.sleep(post_wait_time)
        self.__end_timestamp = self.__prom_timestamp()
        promdb_name = f'promdb_{self.__start_timestamp}_{self.__end_timestamp}'
        promdb_path = os.path.join(self.__artifacts_path, f'{promdb_name}.tar')
        xformcmd = f"--transform 's,^[.],./{promdb_name},'"
        self.__verbose_log(f'Saving prometheus snapshot to {promdb_path}')
        cmd = f'/bin/sh -c "tar -C /prometheus {xformcmd} -cf - .; true" > "{promdb_path}"'
        self.__exec(cmd)
        return promdb_path
