
import ast
import os
import time
import datetime
import tarfile
import shutil
from csv import DictReader

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.workloads.workloads_exceptions import ODFNotInstalled, CNVNotInstalled, KataNotInstalled, MissingScaleNodes, MissingRedis
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.virtctl.virtctl import Virtctl
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.clouds.shared.s3.s3_operations import S3Operations
from benchmark_runner.common.prometheus.prometheus_snapshot import PrometheusSnapshot
from benchmark_runner.common.prometheus.prometheus_snapshot_exceptions import PrometheusSnapshotError
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from benchmark_runner.common.clouds.IBM.ibm_operations import IBMOperations
from benchmark_runner.common.prometheus.prometheus_metrics_operations import PrometheusMetricsOperation
from benchmark_runner.common.google_drive.google_drive_operations import GoogleDriveOperations


class WorkloadsOperations:
    oc = None
    MILLISECONDS = 1000
    REPEAT_TIMES = 3
    SLEEP_TIME = 3
    """
    This class contains workloads operations
    """
    def __init__(self):
        # environment variables
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self._workload = self._environment_variables_dict.get('workload', '')
        self._build_version = self._environment_variables_dict.get('build_version', '')
        self._workloads_odf_pvc = list(self._environment_variables_dict.get('workloads_odf_pvc', ''))
        self._odf_pvc = self._environment_variables_dict.get('odf_pvc', True)
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
        self._enable_prometheus_snapshot = self._environment_variables_dict.get('enable_prometheus_snapshot', False)
        self._run_artifacts_url = self._environment_variables_dict.get('run_artifacts_url', '')
        self._pin_node1 = self._environment_variables_dict.get('pin_node1', '')
        self._pin_node2 = self._environment_variables_dict.get('pin_node2', '')
        self._es_host = self._environment_variables_dict.get('elasticsearch', '')
        self._es_port = self._environment_variables_dict.get('elasticsearch_port', '')
        self._es_user = self._environment_variables_dict.get('elasticsearch_user', '')
        self._es_password = self._environment_variables_dict.get('elasticsearch_password', '')
        self._es_url_protocol = self._environment_variables_dict['elasticsearch_url_protocol']
        self._scale = self._environment_variables_dict.get('scale', '')
        self._redis = self._environment_variables_dict.get('redis', '')
        self._threads_limit = self._environment_variables_dict.get('threads_limit', '')
        self._kata_thread_pool_size = self._environment_variables_dict.get('kata_thread_pool_size', '')
        self._cnv_version = self._environment_variables_dict.get('cnv_version', '')
        self._odf_version = self._environment_variables_dict.get('odf_version', '')
        if self._scale:
            self._scale = int(self._scale)
            self._scale_nodes = self._environment_variables_dict.get('scale_nodes', '')
            self._redis = self._environment_variables_dict.get('redis', '')
            if not self._scale_nodes:
                raise MissingScaleNodes()
            if not self._redis and 'vdbench' in self._workload:
                raise MissingRedis()
            self._scale_node_list = ast.literal_eval(self._scale_nodes)
            if self._threads_limit:
                self._threads_limit = int(self._threads_limit)
            else:
                self._threads_limit = self._scale * len(self._scale_node_list)
            self._bulk_sleep_time = int(self._environment_variables_dict.get('bulk_sleep_time', ''))
        else:
            self._scale_node_list = []
        self._timeout = int(self._environment_variables_dict.get('timeout', ''))
        # Elasticsearch connection
        if self._es_host and self._es_port:
            self._es_operations = ElasticSearchOperations(es_host=self._es_host,
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
        self._virtctl = Virtctl()

        # Prometheus Snapshot
        if self._enable_prometheus_snapshot:
            self._snapshot = PrometheusSnapshot(oc=self._oc, artifacts_path=self._run_artifacts_path, verbose=True)
        self._prometheus_snap_interval = self._environment_variables_dict.get('prometheus_snap_interval', '')
        self._prometheus_metrics_operation = PrometheusMetricsOperation()
        self._windows_url = self._environment_variables_dict.get('windows_url', '')
        self._delete_all = self._environment_variables_dict.get('delete_all', '')
        self._verification_only = self._environment_variables_dict.get('verification_only', '')
        self._wait_for_upgrade_version = self._environment_variables_dict.get('wait_for_upgrade_version', '')
        if self._windows_url:
            file_name = os.path.basename(self._windows_url)
            self._windows_os = os.path.splitext(file_name)[0]
        # google drive
        self._google_drive_path = self._environment_variables_dict.get('google_drive_path', '')
        self._google_drive_credentials = self._environment_variables_dict.get('google_drive_credentials', '')
        self._google_drive_token = self._environment_variables_dict.get('google_drive_token', '')
        self._google_drive_shared_drive_id = self._environment_variables_dict.get('google_drive_shared_drive_id', '')
        if self._google_drive_path:
            self._google_drive_operation = GoogleDriveOperations(google_drive_path=self._google_drive_path,
                                                                 google_drive_credentials=self._google_drive_credentials,
                                                                 google_drive_token=self._google_drive_token,
                                                                 google_drive_shared_drive_id=self._google_drive_shared_drive_id)
        self._upgrade_ocp_version = self._environment_variables_dict.get('upgrade_ocp_version', '')
        self._run_strategy = self._environment_variables_dict.get('run_strategy', '')

    def _get_workload_file_name(self, workload):
        """
        This method returns workload name
        :return:
        """
        if self._scale:
            return f'{workload}-scale-{self._time_stamp_format}'
        else:
            return f'{workload}-{self._time_stamp_format}'

    def set_login(self, kubeadmin_password: str = ''):
        """
        This method sets login
        :param kubeadmin_password:
        :return: oc instance
        """
        self._oc = OC(kubeadmin_password=kubeadmin_password)
        self._oc.login()
        return self._oc

    @logger_time_stamp
    def delete_all(self):
        """
        This method deletes all resources in namespace
        :return:
        """
        self._oc.delete_namespace()

    @logger_time_stamp
    def start_prometheus(self):
        """
        This method starts collection of Prometheus snapshot
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
        This method retrieves the Prometheus snapshot
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
    def odf_workload_verification(self):
        """
        This method verifies whether the ODF operator is installed for ODF workloads and raises an error if it is missing.
        :return:
        """
        workload_name = self._workload.split('_')
        if workload_name[0] in self._workloads_odf_pvc:
            if not self._oc.is_odf_installed():
                raise ODFNotInstalled(workload=self._workload)

    def _create_vm_log(self, labels: list) -> str:
        """
        This method sets vm log per workload
        :param labels: list of labels
        :return: vm_name
        """
        vm_name = ''
        for label in labels:
            vm_name = self._oc.get_vm(label=label)
            self._virtctl.save_vm_log(vm_name=vm_name)
        return vm_name

    def _create_pod_log(self, pod: str = '', log_type: str = ''):
        """
        This method creates pod log per workload
        :param pod: pod name
        :return: save_pod_log file
        """
        pod_name = self._oc.get_pod(label=pod)
        return self._oc.save_pod_log(pod_name=pod_name, log_type=log_type)

    def _get_run_artifacts_hierarchy(self, workload_name: str = '', is_file: bool = False):
        """
        This method returns log hierarchy
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
        This method checks if value is float
        :param value: The value to check
        :return: True if the value is a float, False when cannot be converted to a float
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _create_scale_logs(self):
        """
        The method creates scale logs
        :return:
        """
        self._create_pod_log(pod='state-signals-exporter', log_type='.log')
        self._create_pod_log(pod='redis-master', log_type='.log')

    def _create_pod_run_artifacts(self, pod_name: str, log_type: str):
        """
        This method creates pod run artifacts
        :param pod_name: pod name
        :param log_type: log type extension
        :return: run results list of dicts
        """
        result_list = []
        pod_log_file = self._create_pod_log(pod=pod_name, log_type=log_type)
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
            workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
            line_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')
            result_list.append(dict(line_dict))
        return result_list

    def _create_vm_run_artifacts(self, vm_name: str, start_stamp: str, end_stamp: str, log_type: str):
        """
        This method creates vm run artifacts
        :param vm_name: vm name
        :param start_stamp: start stamp
        :param end_stamp: end stamp
        :param log_type: log type extension
        :return: run results dict
        """
        result_list = []
        results_list = self._oc.extract_vm_results(vm_name=vm_name, start_stamp=start_stamp, end_stamp=end_stamp)
        workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
        # save scale pod log
        if self._scale:
            self._create_pod_log(pod='state-signals-exporter', log_type='.log')
            self._create_pod_log(pod='redis-master', log_type='.log')
        # insert results to csv
        csv_result_file = os.path.join(self._run_artifacts_path, f'{vm_name}{log_type}')
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
            workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
            line_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')
            result_list.append(dict(line_dict))
        return result_list

    def __make_run_artifacts_tarfile(self, workload: str):
        """
        This method compresses the log file and returns the compressed path
        :return:
        """
        tar_run_artifacts_path = f"{self._run_artifacts_path}.tar.gz"
        with tarfile.open(tar_run_artifacts_path, mode='w:gz') as archive:
            workload_file_name = self._get_workload_file_name(workload)
            archive.add(self._run_artifacts_path, arcname=workload_file_name, recursive=True)
        return tar_run_artifacts_path

    @logger_time_stamp
    def delete_local_artifacts(self):
        """
        This method deletes local artifacts
        :return:
        """
        workload = self._workload.replace('_', '-')
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        # remove local run artifacts workload folder
        # verify that its not empty path
        if len(self._run_artifacts_path) > 3 and self._run_artifacts_path != '/' and self._run_artifacts_path and tar_run_artifacts_path and os.path.isfile(tar_run_artifacts_path):
            # remove run_artifacts_path
            shutil.rmtree(path=self._run_artifacts_path)
            # remove tar.gz file
            os.remove(path=tar_run_artifacts_path)

    @logger_time_stamp
    def upload_run_artifacts_to_s3(self):
        """
        This method uploads log to s3
        :return:
        """
        workload = self._workload.replace('_', '-')
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        run_artifacts_hierarchy = self._get_run_artifacts_hierarchy(workload_name=workload)
        # Upload when endpoint_url is not None
        s3operations = S3Operations()
        # change workload to key convention
        workload_file_name = self._get_workload_file_name(workload)
        upload_file = f"{workload_file_name}.tar.gz"
        s3operations.upload_file(file_name_path=tar_run_artifacts_path,
                                 bucket=self._environment_variables_dict.get('bucket', ''),
                                 key=str(run_artifacts_hierarchy),
                                 upload_file=upload_file)

    def get_run_artifacts_google_drive(self):
        """
        This method returns google drive run artifacts folder path
        :return:
        """
        workload = self._workload.replace('_', '-')
        run_artifacts_hierarchy = self._get_run_artifacts_hierarchy(workload_name=workload)
        return self._google_drive_operation.get_drive_folder_url(folder_path=run_artifacts_hierarchy, parent_folder_id=self._google_drive_shared_drive_id)

    @logger_time_stamp
    def upload_run_artifacts_to_google_drive(self):
        """
        This method uploads log to google drive
        :return:
        """
        workload = self._workload.replace('_', '-')
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        run_artifacts_hierarchy = self._get_run_artifacts_hierarchy(workload_name=workload)

        # change workload to key convention
        workload_file_name = self._get_workload_file_name(workload)
        upload_file = f"{workload_file_name}.tar.gz"
        self._google_drive_operation.upload_file_to_folder(file_path=tar_run_artifacts_path,
                                                           folder_path=str(run_artifacts_hierarchy),
                                                           parent_folder_id=self._google_drive_shared_drive_id)

    def __get_metadata(self, kind: str = None, status: str = None, result: dict = None) -> dict:
        """
        This method returns metadata for a run, optionally updates by runtime kind
        @param kind: optionally: pod, vm, or kata
        @param status:
        @param result:
        :return:
        """
        date_format = '%Y_%m_%d'
        metadata = {'ocp_version': self._oc.get_ocp_server_version(),
                    'previous_ocp_version': self._oc.get_previous_ocp_version() if self._upgrade_ocp_version else '',
                    'cnv_version': self._oc.get_cnv_version(),
                    'kata_version': self._oc.get_kata_operator_version(),
                    'kata_rpm_version': self._oc.get_kata_rpm_version(node=self._pin_node1),
                    'odf_version': self._oc.get_odf_version(),
                    'runner_version': self._build_version,
                    'version': int(self._build_version.split('.')[-1]),
                    'vm_os_version': 'centos-stream8',
                    'ci_date': datetime.datetime.now().strftime(date_format),
                    'uuid': self._uuid,
                    'pin_node1': self._pin_node1,
                    'pin_node2': self._pin_node2,
                    # display -1 when 0,1 for avoiding conflict with 0/1 status code
                    'odf_disk_count': -1 if self._oc.get_odf_disk_count() in {0, 1} else self._oc.get_odf_disk_count()
}
        if kind:
            metadata.update({'kind': kind})
        if status:
            metadata.update({'run_status': status})
        if self._scale:
            metadata.update({'scale': int(self._scale)*len(self._scale_node_list)})
        if 'bootstorm' in self._workload:
            metadata.update({'vm_os_version': 'fedora37'})
        if 'windows' in self._workload:
            metadata.update({'vm_os_version': self._windows_os})
        if result:
            metadata.update(result)

        return metadata

    def _upload_to_elasticsearch(self, index: str, kind: str, status: str, result: dict = None):
        """
        This method uploads results to elasticsearch
        :param index:
        :param kind:
        :param status:
        :param result:
        :return:
        """
        self._es_operations.upload_to_elasticsearch(index=index, data=self.__get_metadata(kind=kind, status=status, result=result))

    def _verify_elasticsearch_data_uploaded(self, index: str, uuid: str):
        """
        This method verifies that elasticsearch data was uploaded
        :param index:
        :param uuid:
        :return:
        """
        self._es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=uuid)

    @logger_time_stamp
    def update_ci_status(self, status: str, ci_minutes_time: int, benchmark_runner_id: str, benchmark_operator_id: str, benchmark_wrapper_id: str, ocp_install_minutes_time: int = 0, ocp_resource_install_minutes_time: int = 0):
        """
        This method updates ci status Pass/Failed
        :param status: Pass/Failed
        :param ci_minutes_time: ci time in minutes
        :param benchmark_runner_id: benchmark_runner last repository commit id
        :param benchmark_operator_id: benchmark_operator last repository commit id
        :param benchmark_wrapper_id: benchmark_wrapper last repository commit id
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
        metadata.update({'status': status, 'status#': status_dict[status], 'ci_minutes_time': ci_minutes_time, 'benchmark_runner_id': benchmark_runner_id, 'benchmark_operator_id': benchmark_operator_id, 'benchmark_wrapper_id': benchmark_wrapper_id, 'ocp_install_minutes_time': ocp_install_minutes_time, 'ocp_resource_install_minutes_time': ocp_resource_install_minutes_time})
        self._es_operations.upload_to_elasticsearch(index=es_index, data=metadata)

    @logger_time_stamp
    def split_run_bulks(self, iterable: range, limit: int = 1):
        """
        This method splits run into bulk depends on threads limit
        @return: run bulks
        """
        length = len(iterable)
        for ndx in range(0, length, limit):
            yield iterable[ndx:min(ndx + limit, length)]

    @logger_time_stamp
    def clear_nodes_cache(self):
        """
        This method clears nodes cache
        """
        for i in range(self.REPEAT_TIMES-1):
            self._oc.clear_node_caches()
            time.sleep(self.SLEEP_TIME)
        self._oc.clear_node_caches()

    def initialize_workload(self):
        """
        This method includes all the initialization of workload
        :return:
        """
        # Verify that CNV operator in installed for CNV workloads
        if '_vm' in self._workload and not self._oc.is_cnv_installed():
            raise CNVNotInstalled(workload=self._workload)
        # Verify that Kata operator in installed for kata workloads
        if '_kata' in self._workload and not self._oc.is_kata_installed():
            raise KataNotInstalled(workload=self._workload)
        if self._delete_all:
            self.delete_all()
            self.clear_nodes_cache()
        if self._odf_pvc:
            self.odf_workload_verification()
        self._template.generate_yamls(scale=str(self._scale), scale_nodes=self._scale_node_list, redis=self._redis, thread_limit=self._threads_limit)
        if self._enable_prometheus_snapshot:
            self.start_prometheus()

    def finalize_workload(self):
        """
        This method includes all the finalization of workload
        :return:
        """
        self._oc.collect_events()
        if self._enable_prometheus_snapshot:
            self.end_prometheus()
        if self._endpoint_url:
            self.upload_run_artifacts_to_s3()
        if not self._save_artifacts_local:
            self.delete_local_artifacts()
        if self._delete_all:
            self.delete_all()
