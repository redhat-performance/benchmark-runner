
import os
import json

from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.clusterbuster.clusterbuster_exceptions import MissingResultReport, MissingElasticSearch
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp


class ClusterBusterWorkloads:
    """
    This class is responsible for all ClusterBuster workloads
    """

    def __init__(self):
        self.result_report = '/tmp/clusterbuster-report.json'
        self.__ssh = SSH()
        # environment variables
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__namespace = self.__environment_variables_dict.get('namespace', '')
        self.__run_type = self.__environment_variables_dict.get('run_type', '')
        self.__pin_node1 = self.__environment_variables_dict.get('pin_node1', '')
        self.__pin_node2 = self.__environment_variables_dict.get('pin_node2', '')
        # ElasticSearch connection
        self.__es_host = self.__environment_variables_dict.get('elasticsearch', '')
        self.__es_port = self.__environment_variables_dict.get('elasticsearch_port', '')
        self.__es_user = self.__environment_variables_dict.get('elasticsearch_user', '')
        self.__es_password = self.__environment_variables_dict.get('elasticsearch_password', '')
        self.__timeout = int(self.__environment_variables_dict.get('timeout', ''))
        self.__uuid = self.__environment_variables_dict.get('uuid', '')
        self.__es_url_protocol = self.__environment_variables_dict['elasticsearch_url_protocol']
        self._ssh = SSH()
        # ElasticSearch connection
        if self.__es_host and self.__es_port:
            self.__es_operations = ElasticSearchOperations(es_host=self.__es_host,
                                                           es_port=self.__es_port,
                                                           es_user=self.__es_user,
                                                           es_password=self.__es_password,
                                                           es_url_protocol=self.__es_url_protocol,
                                                           timeout=self.__timeout)
        else:
            raise MissingElasticSearch()

    @logger_time_stamp
    def upload_clusterbuster_result_to_elasticsearch(self):
        """
        This method upload to ElasticSearch the results
        :return:
        """
        result_report_json_file = open(self.result_report)
        result_report_json_str = result_report_json_file.read()
        result_report_json_data = json.loads(result_report_json_str)
        for workload, clusterbuster_tests in result_report_json_data.items():
            if self.__run_type == 'test_ci':
                index = f'clusterbuster-{workload}-test-ci-results'
            else:
                index = f'clusterbuster-{workload}-results'
            print(index)
            if workload != 'metadata':
                for clusterbuster_test in clusterbuster_tests:
                    self.__es_operations.upload_to_elasticsearch(index=index, data=clusterbuster_test)
            # metadata
            elif workload == 'metadata':
                self.__es_operations.upload_to_elasticsearch(index=index, data=result_report_json_data['metadata'])
                self.__es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=result_report_json_data['metadata']['uuid'])

    @logger_time_stamp
    def run(self):
        """
        This method run clusterbuster workloads
        :return:
        """
        self.__ssh.run(cmd=f'cd /tmp/OpenShift4-tools/CI; ./run-kata-perf-suite --run_type={self.__run_type} --client-pin-node={self.__pin_node1} --server-pin-node={self.__pin_node2} --sync-pin-node={self.__pin_node2} --basename={self.__namespace} --artifactdir=/tmp/clusterbuster-ci --analyze=/tmp/clusterbuster-report.json')
        if os.path.exists(os.path.join(self.result_report)):
            self.upload_clusterbuster_result_to_elasticsearch()
            return True
        else:
            raise MissingResultReport()
