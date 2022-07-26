
import os
import json

from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.clusterbuster.clusterbuster_exceptions import MissingResultReport, MissingElasticSearch
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class ClusterBusterWorkloads(WorkloadsOperations):
    """
    This class is responsible for all ClusterBuster workloads
    """

    def __init__(self):
        super().__init__()
        self.__clusterbuster_path = '/tmp/OpenShift4-tools/CI/./run-kata-perf-suite'
        # environment variables
        self.__namespace = self._environment_variables_dict.get('namespace', '')
        self.__result_report = '/tmp/clusterbuster-report.json'
        self.__artifactdir = os.path.join(self._run_artifacts_path, 'clusterbuster-ci')
        self.__clusterbuster_log = os.path.join(self._run_artifacts_path, 'clusterbuster.log')
        self.__ssh = SSH()

    @logger_time_stamp
    def upload_clusterbuster_result_to_elasticsearch(self):
        """
        This method upload to ElasticSearch the results
        :return:
        """
        result_report_json_file = open(self.__result_report)
        result_report_json_str = result_report_json_file.read()
        result_report_json_data = json.loads(result_report_json_str)
        for workload, clusterbuster_tests in result_report_json_data.items():
            if self._run_type == 'test_ci':
                index = f'clusterbuster-{workload}-test-ci-results'
            elif self._run_type == 'release':
                index = f'clusterbuster-{workload}-release-results'
            else:
                index = f'clusterbuster-{workload}-results'
            logger.info(f'upload index: {index}')
            if workload != 'metadata':
                for clusterbuster_test in clusterbuster_tests:
                    self._es_operations.upload_to_elasticsearch(index=index, data=clusterbuster_test)
            # metadata
            elif workload == 'metadata':
                # run artifacts data
                result_report_json_data['metadata']['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._es_operations.upload_to_elasticsearch(index=index, data=result_report_json_data['metadata'])
                self._es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=result_report_json_data['metadata']['uuid'])

    @logger_time_stamp
    def delete_all(self):
        """
        This method delete all resource that related to ClusterBuster resource
        :return:
        """
        self.__ssh.run(cmd=f'oc delete pod -A -l {self.__namespace}')

    def initialize_workload(self):
        """
        This method includes all the initialization of ClusterBuster workload
        :return:
        """
        self.delete_all()
        self.clear_nodes_cache()
        if self._enable_prometheus_snapshot:
            self.start_prometheus()

    def finalize_workload(self):
        """
        This method includes all the finalization of ClusterBuster workload
        :return:
        """
        # Result file exist and not empty
        if os.path.exists(os.path.join(self.__result_report)) and not os.stat(self.__result_report).st_size == 0:
            self.upload_clusterbuster_result_to_elasticsearch()

        if self._enable_prometheus_snapshot:
            self.end_prometheus()
        if self._endpoint_url:
            self.upload_run_artifacts_to_s3()
        if not self._save_artifacts_local:
            self.delete_local_artifacts()
        self.delete_all()

    @logger_time_stamp
    def run_workload(self):
        """
        This method run ClusterBuster workload
        :return:
        """
        self.__ssh.run(cmd=f'{self.__clusterbuster_path} --run_type={self._run_type} --client-pin-node={self._pin_node1} --server-pin-node={self._pin_node2} --sync-pin-node={self._pin_node2} --force-cleanup-i-know-this-is-dangerous=600 --basename={self.__namespace} --artifactdir={self.__artifactdir} --analyze={self.__result_report} > {self.__clusterbuster_log} 2>&1')
        # Check that Result file exist and not empty
        if os.path.exists(os.path.join(self.__result_report)) and not os.stat(self.__result_report).st_size == 0:
            self.__ssh.run(cmd=f'cp {self.__result_report} {self._run_artifacts_path}')
            return True
        else:
            result_report_json_data = {}
            result_report_json_data['result'] = 'Failed'
            result_report_json_data['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload, is_file=True)}-{self._time_stamp_format}.tar.gz')
            if self._run_type == 'test_ci':
                index = f'clusterbuster-metadata-test-ci-results'
            elif self._run_type == 'release':
                index = f'clusterbuster-metadata-release-results'
            else:
                index = f'clusterbuster-metadata-results'
            logger.info(f'upload index: {index}')
            self._es_operations.upload_to_elasticsearch(index=index, data=result_report_json_data)
            raise MissingResultReport()

    @logger_time_stamp
    def run(self):
        """
        This method run ClusterBuster workloads
        :return:
        """
        try:
            # initialize workload
            self.initialize_workload()
            # Run workload
            if self.run_workload():
                # finalize workload
                self.finalize_workload()
        # when error raised finalize workload
        except Exception:
            logger.info(f'{self._workload} workload raised an exception')
            # finalize workload
            self.finalize_workload()
            return False

        return True
