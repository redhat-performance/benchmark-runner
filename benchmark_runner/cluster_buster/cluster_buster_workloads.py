
import os
import json

from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.cluster_buster.cluster_buster_exceptions import MissingResultReport


class ClusterBusterWorkloads:
    """
    This class responsible for all cluster buster workloads
    """

    def __init__(self):
        self.result_report = '/tmp/clusterbuster-report.json'
        self.__ssh = SSH()
        # environment variables
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self._run_type = self._environment_variables_dict.get('run_type', '')
        self._pin_node1 = self._environment_variables_dict.get('pin_node1', '')
        self._pin_node2 = self._environment_variables_dict.get('pin_node2', '')
        # ElasticSearch connection
        self._es_host = self._environment_variables_dict.get('elasticsearch', '')
        self._es_port = self._environment_variables_dict.get('elasticsearch_port', '')
        self._es_user = self._environment_variables_dict.get('elasticsearch_user', '')
        self._es_password = self._environment_variables_dict.get('elasticsearch_password', '')
        self._timeout = int(self._environment_variables_dict.get('timeout', ''))
        self._uuid = self._environment_variables_dict.get('uuid', '')
        self._es_url_protocol = self._environment_variables_dict['elasticsearch_url_protocol']
        self._ssh = SSH()
        # Elasticsearch connection
        if self._es_host and self._es_port:
            self.__es_operations = ElasticSearchOperations(es_host=self._es_host,
                                                           es_port=self._es_port,
                                                           es_user=self._es_user,
                                                           es_password=self._es_password,
                                                           es_url_protocol=self._es_url_protocol,
                                                           timeout=self._timeout)

    def upload_result_to_es(self):
        """
        This method upload to ElasticSearch the results
        :return:
        """
        result_report_json_file = open(self.result_report)
        result_report_json_str = result_report_json_file.read()
        result_report_json_data = json.loads(result_report_json_str)
        for workload, cluster_buster_tests in result_report_json_data.items():
            count = 0
            # skip metadata, not a workload
            if workload != 'metadata':
                for cluster_buster_test in cluster_buster_tests:
                    count += 1
                    print(workload, 'upload', str(count))
                    self.__es_operations.upload_to_elasticsearch(index=f'cluster-buster-{workload}-test5', data=cluster_buster_test)
            # metadata
            elif workload == 'metadata':
                #  result_report_json_data['metadata']['status'] = result_report_json_data['Status']
                self.__es_operations.upload_to_elasticsearch(index=f'cluster-buster-{workload}-test5', data=result_report_json_data['metadata'])

    def run(self):
        """
        This method run cluster buster
        :return:
        """
        self.__ssh.run(cmd=f'pushd /tmp/OpenShift4-tools/CI; ./run-kata-perf-suite --profile={self._run_type} --artifactdir=/tmp/clusterbuster-ci --analyze=/tmp/clusterbuster-report.json; popd')
        if os.path.exists(os.path.join(self.result_report)):
            self.upload_result_to_es()
            return True
        else:
            raise MissingResultReport()
