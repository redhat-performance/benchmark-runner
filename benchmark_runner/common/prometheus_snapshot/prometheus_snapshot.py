
import datetime
import time
import string
from benchmark_runner.common.prometheus_snapshot.prometheus_snapshot_exceptions import PrometheusSnapshotError, PrometheusSnapshotAlreadyStarted, PrometheusSnapshotNotStarted, PrometheusSnapshotAlreadyRetrieved

from typeguard import typechecked
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc import OC
import os
import re

prometheus_snapshot_datetime_format = '%Y_%m_%dT%H_%M_%S%z'

class PrometheusSnapshot:
    """
    Extract a Prometheus snapshot into a specified directory.
    The directory is assumed to already exist
    """
    def __init__(self, oc: OC, log_path: str, verbose: bool=False):
        self.__oc = oc
        self.__log_path = log_path
        self.__start_timestamp = None
        self.__end_timestamp = None
        self.__verbose = verbose
        self.__pod_name = 'prometheus-k8s-0'
        self.__namespace = 'openshift-monitoring'
        self.__container = 'prometheus'
        self.__format = prometheus_snapshot_datetime_format

    @typechecked
    def __verbose_log(self, message: str):
        if self.__verbose:
            logger.info(message)

    @typechecked
    def __exec(self, command: str):
        return self.__oc.exec(pod_name=self.__pod_name, namespace=self.__namespace, container=self.__container, command=command)

    def __prom_timestamp(self):
        valid_timestamp = False
        pattern = r'^[0-9]{4}'
        retries = 12
        while not valid_timestamp:
            timestamp = self.__exec(f"date '+{self.__format}'")
            if re.match(pattern, timestamp):
                return timestamp
            else:
                time.sleep(5)
                if retries <= 0:
                    return timestamp
                retries = retries - 1

    @typechecked
    @logger_time_stamp
    def prepare_for_snapshot(self, pre_wait_time: int=60, clear_db: bool=True):
        if self.__start_timestamp or self.__end_timestamp:
            raise PrometheusSnapshotAlreadyStarted
        if clear_db:
            self.__verbose_log(f'Deleting existing {self.__pod_name} pod')
            self.__oc.terminate_pod_sync(pod_name=self.__pod_name, namespace=self.__namespace)
        self.__verbose_log(f'Waiting for {self.__pod_name} pod to reappear')
        self.__oc.wait_for_pod_ready(pod_name=self.__pod_name, namespace=self.__namespace)
        self.__start_timestamp = self.__prom_timestamp()
        self.__verbose_log(f'Waiting {pre_wait_time} seconds for initial metrics collection to settle')
        time.sleep(pre_wait_time)

    @typechecked
    def retrieve_snapshot(self, post_wait_time: int=120):
        if not self.__start_timestamp:
            raise PrometheusSnapshotNotStarted
        if self.__end_timestamp:
            raise PrometheusSnapshotAlreadyRetrieved
        self.__verbose_log(f'Waiting {post_wait_time} seconds for metrics collection to complete')
        time.sleep(post_wait_time)
        self.__end_timestamp = self.__prom_timestamp()
        promdb_name = f'promdb_{self.__start_timestamp}_{self.__end_timestamp}'
        promdb_path = os.path.join(self.__log_path, f'{promdb_name}.tar')
        xformcmd = f"--transform 's,^[.],./{promdb_name},'"
        self.__verbose_log(f'Saving prometheus DB to {promdb_path}')
        cmd = f'/bin/sh -c "tar -C /prometheus {xformcmd} -cf - .; true" > "{promdb_path}"'
        self.__exec(cmd)
        return promdb_path
