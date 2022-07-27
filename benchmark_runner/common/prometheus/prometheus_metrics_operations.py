import os
import yaml
import time
import datetime
import openshift
from prometheus_api_client import PrometheusConnect
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class PrometheusMetricsOperation(WorkloadsOperations):
    """
    This class Run prometheus queries
    """

    def __init__(self):
        super().__init__()
        self.__current_dir = os.path.dirname(os.path.abspath(__file__))
        self.__queries_file = os.path.join(self.__current_dir, 'metrics-default.yaml')
        self.__authorization = {'Authorization': self.__get_prometheus_token()}
        self.__prometheus = PrometheusConnect(url=self.__get_prometheus_default_url(), disable_ssl=True, headers=self.__authorization)
        self.__metrics_start_time = None
        self.__metrics_end_time = None
        self.__metric_results = {}

    @staticmethod
    def __get_prometheus_default_url():
        """
        This method return prometheus default url
        :return:
        """
        try:
            with openshift.project('openshift-monitoring'):
                return f"https://{openshift.selector(['route/prometheus-k8s']).objects()[0].as_dict()['spec']['host']}"
        except Exception as err:
            raise f'Unable to retrieve prometheus-k8s route: {err}'

    def __get_prometheus_token(self):
        """
        This method return prometheus token
        :return:
        """
        try:
            return f'Bearer {self.__get_prometheus_token_by_version()}'
        except Exception as err:
            raise f'Unable to retrieve prometheus-k8s token: {err}'

    @staticmethod
    def __get_prometheus_token_by_version():
        """
        This method return prometheus token
        :return:
        """
        with openshift.project('openshift-monitoring'):
            openshift_version = openshift.get_server_version().split('-')[0].split('.')
            if int(openshift_version[0]) > 4 or (int(openshift_version[0]) == 4 and int(openshift_version[1]) > 10):
                return openshift.invoke('sa', ['new-token', '-n', 'openshift-monitoring', 'prometheus-k8s']).out().strip()
            else:
                return openshift.get_serviceaccount_auth_token('prometheus-k8s')

    @staticmethod
    def get_prometheus_timestamp():
        """
        This method return prometheus time stamp
        :return:
        """
        retries = 5
        while retries > 0:
            retries = retries - 1
            try:
                with openshift.project('openshift-monitoring'):
                    result = openshift.selector('pod/prometheus-k8s-0').object().execute(['date', '+%s.%N'],
                                                                                         container_name='prometheus')
                    return datetime.datetime.utcfromtimestamp(float(result.out()))
            except Exception as err:
                if retries <= 0:
                    raise f'Unable to retrieve date: {err}'
                else:
                    time.sleep(5)

    def yaml_to_dict(self):
        """
        This method convert yaml file to dictionary
        :return:
        """
        with open(self.__queries_file) as metrics_yaml:
            queries = metrics_yaml.read()
            return yaml.safe_load(queries)

    def init_prometheus(self):
        """
        This method init prometheus time
        :return:
        """
        self.__metrics_start_time = self.get_prometheus_timestamp()
        logger.info(f'prometheus metric start: {self.__metrics_start_time}')
        return self.__metrics_start_time

    def finalize_prometheus(self):
        """
        This method init prometheus time
        :return:
        """
        self.__metrics_end_time = self.get_prometheus_timestamp()
        logger.info(f'prometheus metric end: {self.__metrics_end_time}')
        return self.__metrics_end_time

    def run_prometheus_query(self, query: str, instant: bool = False):
        """
        This method run one prometheus query and return dictionary result
        :param instant:
        :param query:
        :return:
        """
        if instant:
            metric_result = (self.__prometheus.custom_query(query=query))
        else:
            metric_result = self.__prometheus.custom_query_range(query=query, start_time=self.__metrics_start_time, end_time=self.__metrics_end_time, step='30')
        self.__metric_results['metrics_result'] = metric_result
        return self.__metric_results

    def run_prometheus_queries(self, query_yaml_file: str = None):
        """
        This method run several prometheus queries and return list of dictionaries result
        :param query_yaml_file:
        :return:
        """
        if query_yaml_file and os.path.isfile(query_yaml_file):
            self.__queries_file = query_yaml_file
        metrics = self.yaml_to_dict()
        for metric in metrics:
            if 'query' not in metric:
                continue
            try:
                if 'instant' not in metric or metric['instant'] is not True:
                    metric_result = self.__prometheus.custom_query_range(metric['query'], start_time=self.__metrics_start_time, end_time=self.__metrics_end_time, step='30')
                else:
                    metric_result = (self.__prometheus.custom_query(metric['query']))
                self.__metric_results[metric['metricName']] = metric_result
            except Exception as err:
                raise f"Query {metric['metricName']} ({metric['query']}) failed: {err}"
        return self.__metric_results

    #  @todo TBD: verify before uploading if it visualize correctly
    def upload_result_to_elastic(self):
        """
        This method upload result to ElasticSearch
        :return: 
        """
        pass
        # if self._es_host and self._es_port:
        #     for query, results in self.__metric_results.items():
        #         pass
        #         self._es_operations.upload_to_elasticsearch(index=query, data=results)
        # else:
        #     raise Exception('Missing ElasticSearch data')
        
