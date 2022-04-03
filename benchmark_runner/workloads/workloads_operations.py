
import os
import datetime
import tarfile
import shutil
from csv import DictReader

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.workloads.workloads_exceptions import ODFNonInstalled
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.clouds.shared.s3.s3_operations import S3Operations
from benchmark_runner.common.prometheus.prometheus_snapshot import PrometheusSnapshot
from benchmark_runner.common.prometheus.prometheus_snapshot_exceptions import PrometheusSnapshotError
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from benchmark_runner.common.clouds.IBM.ibm_operations import IBMOperations


class WorkloadsOperations:
    oc = None
    """
    This class run workloads
    """
    def __init__(self):
        # environment variables
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self._workload = self._environment_variables_dict.get('workload', '')
        self._build_version = self._environment_variables_dict.get('build_version', '')
        self._workloads_odf_pvc = list(self._environment_variables_dict.get('workloads_odf_pvc', ''))
        self._odf_pvc = self._environment_variables_dict.get('odf_pvc', '')
        self._kubeadmin_password = self._environment_variables_dict.get('kubeadmin_password', '')
        self._run_type = self._environment_variables_dict.get('run_type', '')
        self._trunc_uuid = self._environment_variables_dict.get('trunc_uuid', '')
        self._uuid = self._environment_variables_dict.get('uuid', '')
        self._date_key = self._environment_variables_dict.get('date_key', '')
        self._key = self._environment_variables_dict.get('key', '')
        self._time_stamp_format = self._environment_variables_dict.get('time_stamp_format', '')
        self._endpoint_url = self._environment_variables_dict.get('endpoint_url', '')
        self._run_artifacts_path = self._environment_variables_dict.get('run_artifacts_path', '')
        self._save_artifacts_local = self._environment_variables_dict.get('save_artifacts_local', '')
        self._enable_prometheus_snapshot = self._environment_variables_dict.get('enable_prometheus_snapshot', '')
        self._run_artifacts_url = self._environment_variables_dict.get('run_artifacts_url', '')
        self._pin_node1 = self._environment_variables_dict.get('pin_node1', '')
        self._pin_node2 = self._environment_variables_dict.get('pin_node2', '')
        self._es_host = self._environment_variables_dict.get('elasticsearch', '')
        self._es_port = self._environment_variables_dict.get('elasticsearch_port', '')
        self._es_user = self._environment_variables_dict.get('elasticsearch_user', '')
        self._es_password = self._environment_variables_dict.get('elasticsearch_password', '')
        self._es_url_protocol = self._environment_variables_dict['elasticsearch_url_protocol']
        self._timeout = int(self._environment_variables_dict.get('timeout', ''))
        # Elasticsearch connection
        if self._es_host and self._es_port:
            self.__es_operations = ElasticSearchOperations(es_host=self._es_host,
                                                           es_port=self._es_port,
                                                           es_user=self._es_user,
                                                           es_password=self._es_password,
                                                           es_url_protocol=self._es_url_protocol,
                                                           timeout=self._timeout)
        # Generate templates class
        self._template = TemplateOperations(workload=self._workload)
        # set oc login

        if WorkloadsOperations.oc is None:
            WorkloadsOperations.oc = self.set_login(kubeadmin_password=self._kubeadmin_password)
        self._oc = WorkloadsOperations.oc

        # PrometheusSnapshot
        if self._enable_prometheus_snapshot:
            self._snapshot = PrometheusSnapshot(oc=self._oc, artifacts_path=self._run_artifacts_path, verbose=True)

    def set_login(self, kubeadmin_password: str = ''):
        """
        This method set oc login
        :param kubeadmin_password:
        :return: oc instance
        """
        self._oc = OC(kubeadmin_password=kubeadmin_password)
        self._oc.login()
        return self._oc

    @logger_time_stamp
    def delete_all(self):
        """
        This method delete all resources in namespace
        :return:
        """
        self._oc.delete_all_resources(resources=['vm', 'pods', 'pvc'])

    @logger_time_stamp
    def start_prometheus(self):
        """
        This method start collection of Prometheus snapshot
        :return:
        """
        if self._enable_prometheus_snapshot:
            try:
                self._snapshot.prepare_for_snapshot()
            except PrometheusSnapshotError as err:
                raise PrometheusSnapshotError(err)
            except Exception as err:
                raise err

    @logger_time_stamp
    def end_prometheus(self):
        """
        This method retrieve the Prometheus snapshot
        :return:
        """
        if self._enable_prometheus_snapshot:
            try:
                self._snapshot.retrieve_snapshot()
            except PrometheusSnapshotError as err:
                raise PrometheusSnapshotError(err)
            except Exception as err:
                raise err

    @logger_time_stamp
    def odf_pvc_verification(self):
        """
        This method verified if odf or pvc is required for workload, raise error in case of missing odf
        :return:
        """
        workload_name = self._workload.split('_')
        if self._odf_pvc == 'True' and workload_name[0] in self._workloads_odf_pvc:
            if not self._oc.is_odf_installed():
                raise ODFNonInstalled()

    def _create_vm_log(self, labels: list) -> str:
        """
        This method set vm log per workload
        :param labels: list of labels
        :return: vm_name
        """
        vm_name = ''
        for label in labels:
            vm_name = self._oc.get_vm(label=label)
            self._oc.save_vm_log(vm_name=vm_name)
        return vm_name

    def _create_pod_log(self, pod: str = ''):
        """
        This method create pod log per workload
        :param pod: pod name
        :return: save_pod_log file
        """
        pod_name = self._oc.get_pod(label=pod)
        return self._oc.save_pod_log(pod_name=pod_name)

    def _get_run_artifacts_hierarchy(self, workload_name: str = '', is_file: bool = False):
        """
        This method return log hierarchy
        :param workload_name: workload name
        :param is_file: is file name
        :return:
        """
        key = self._key
        run_type = self._run_type.replace('_', '-')
        date_key = self._date_key
        if workload_name:
            workload_key = workload_name.split('-')[0]
            if is_file:
                return os.path.join(key, run_type, date_key, workload_key, workload_name)
            else:
                return os.path.join(key, run_type, date_key, workload_key)
        return os.path.join(key, run_type, date_key)

    @staticmethod
    def __is_float(value) -> bool:
        """
        This method check if value is float
        :param value:
        :return:
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _create_pod_run_artifacts(self, pod_name: str):
        """
        This method create pod run artifacts
        :param pod_name: pod name
        :return: run results dict
        """
        result_list = []
        pod_log_file = self._create_pod_log(pod=pod_name)
        workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
        # csv to dictionary
        the_reader = DictReader(open(pod_log_file, 'r'))
        for line_dict in the_reader:
            for key, value in line_dict.items():
                if self.__is_float(value):
                    num = float(value)
                    line_dict[key] = round(num, 3)
                elif value == 'n/a':
                    line_dict[key] = 0.0
            line_dict['pod_name'] = pod_name
            line_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            result_list.append(dict(line_dict))
        return result_list

    def _create_vm_run_artifacts(self, vm_name: str, start_stamp: str, end_stamp: str):
        """
        This method create vm run artifacts
        :param vm_name: vm name
        :param start_stamp: start stamp
        :param end_stamp: end stamp
        :return: run results dict
        """
        result_list = []
        results_list = self._oc.extract_vm_results(vm_name=vm_name, start_stamp=start_stamp, end_stamp=end_stamp)
        workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
        # insert results to csv
        csv_result_file = os.path.join(self._run_artifacts_path, 'vdbench_vm_result.csv')
        with open(csv_result_file, 'w') as out:
            for row in results_list:
                if row:
                    out.write(f'{row[0].strip()}\n')
        # csv to dictionary
        the_reader = DictReader(open(csv_result_file, 'r'))
        for line_dict in the_reader:
            for key, value in line_dict.items():
                if self.__is_float(value):
                    num = float(value)
                    line_dict[key] = round(num, 3)
                elif value == 'n/a':
                    line_dict[key] = 0.0
            line_dict['vm_name'] = vm_name
            line_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
            result_list.append(dict(line_dict))
        return result_list

    def __make_run_artifacts_tarfile(self, workload: str):
        """
        This method tar.gz log path and return the tar.gz path
        :return:
        """
        tar_run_artifacts_path = f"{self._run_artifacts_path}.tar.gz"
        with tarfile.open(tar_run_artifacts_path, mode='w:gz') as archive:
            archive.add(self._run_artifacts_path, arcname=f'{workload}-{self._time_stamp_format}', recursive=True)
        return tar_run_artifacts_path

    @logger_time_stamp
    def upload_run_artifacts_to_s3(self):
        """
        This method uploads log to s3
        :param workload:
        :return:
        """
        workload = self._workload.replace('_', '-')
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        run_artifacts_hierarchy = self._get_run_artifacts_hierarchy(workload_name=workload)
        # Upload when endpoint_url is not None
        if self._endpoint_url:
            s3operations = S3Operations()
            # change workload to key convention
            upload_file = f"{workload}-{self._time_stamp_format}.tar.gz"
            s3operations.upload_file(file_name_path=tar_run_artifacts_path,
                                     bucket=self._environment_variables_dict.get('bucket', ''),
                                     key=run_artifacts_hierarchy,
                                     upload_file=upload_file)
        # remove local run artifacts workload folder
        # verify that its not empty path
        if len(self._run_artifacts_path) > 3 and self._run_artifacts_path != '/' and self._run_artifacts_path and tar_run_artifacts_path and os.path.isfile(tar_run_artifacts_path) and not self._save_artifacts_local:
            # remove run_artifacts_path
            shutil.rmtree(path=self._run_artifacts_path)
            # remove tar.gz file
            os.remove(path=tar_run_artifacts_path)

    def __get_metadata(self, kind: str = None, status: str = None, result: dict = None) -> dict:
        """
        This method return metadata kind and database argument are optional
        @param kind: optional: pod, vm, or kata
        @param status:
        @param result:
        :return:
        """
        date_format = '%Y_%m_%d'
        metadata = {'ocp_version': self._oc.get_ocp_server_version(),
                    'cnv_version': self._oc.get_cnv_version(),
                    'kata_version': self._oc.get_kata_version(),
                    'odf_version': self._oc.get_odf_version(),
                    'runner_version': self._build_version,
                    'version': int(self._build_version.split('.')[-1]),
                    'vm_os_version': 'centos-stream8',
                    'ci_date': datetime.datetime.now().strftime(date_format),
                    'uuid': self._uuid,
                    'pin_node1': self._pin_node1,
                    'pin_node2': self._pin_node2}
        if kind:
            metadata.update({'kind': kind})
        if status:
            metadata.update({'run_status': status})
        if result:
            metadata.update(result)

        return metadata

    def _upload_to_elasticsearch(self, index: str, kind: str, status: str, result: dict = None):
        """
        This method upload to elasticsearch
        :param index:
        :param kind:
        :param status:
        :param result:
        :return:
        """
        self.__es_operations.upload_to_elasticsearch(index=index, data=self.__get_metadata(kind=kind, status=status, result=result))

    def _verify_elasticsearch_data_uploaded(self, index: str, uuid: str):
        """
        This method verify that elasticsearch data uploaded
        :param index:
        :param uuid:
        :return:
        """
        self.__es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=uuid)

    @logger_time_stamp
    def update_ci_status(self, status: str, ci_minutes_time: int, benchmark_operator_id: str, benchmark_wrapper_id: str, ocp_install_minutes_time: int = 0, ocp_resource_install_minutes_time: int = 0):
        """
        This method update ci status Pass/Failed
        :param status: Pass/Failed
        :param ci_minutes_time: ci time in minutes
        :param benchmark_wrapper_id: benchmark_wrapper last repository commit id
        :param benchmark_operator_id: benchmark_operator last repository commit id
        :param ocp_install_minutes_time: ocp install minutes time, default 0 because ocp install run once a week
        :param ocp_resource_install_minutes_time: ocp install minutes time, default 0 because ocp install run once a week
        :return:
        """
        if self._run_type == 'test_ci':
            es_index = 'ci-status-test'
        else:
            es_index = 'ci-status'
        status_dict = {'failed': 0, 'pass': 1}
        metadata = self.__get_metadata()
        if ocp_resource_install_minutes_time != 0:
            ibm_operations = IBMOperations(user=self._environment_variables_dict.get('provision_user', ''))
            ibm_operations.ibm_connect()
            ocp_install_minutes_time = ibm_operations.get_ocp_install_time()
            ibm_operations.ibm_disconnect()
        metadata.update({'status': status, 'status#': status_dict[status], 'ci_minutes_time': ci_minutes_time, 'benchmark_operator_id': benchmark_operator_id, 'benchmark_wrapper_id': benchmark_wrapper_id, 'ocp_install_minutes_time': ocp_install_minutes_time, 'ocp_resource_install_minutes_time': ocp_resource_install_minutes_time})
        self.__es_operations.upload_to_elasticsearch(index=es_index, data=metadata)

    def initialize_workload(self):
        """
        This method includes all the initialization of workload
        :return:
        """
        self.delete_all()
        self.odf_pvc_verification()
        self._template.generate_yamls()
        self.start_prometheus()

    def finalize_workload(self):
        """
        This method includes all the finalization of workload
        :return:
        """
        self.end_prometheus()
        self.upload_run_artifacts_to_s3()
        self.delete_all()
