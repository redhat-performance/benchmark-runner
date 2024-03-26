
import os
import yaml
import datetime
import tarfile
import shutil
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.virtctl.virtctl import Virtctl
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.benchmark_operator.benchmark_operator_exceptions import ODFNotInstalled, CNVNotInstalled, KataNotInstalled, EmptyLSOPath
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.clouds.shared.s3.s3_operations import S3Operations
from benchmark_runner.common.prometheus.prometheus_snapshot import PrometheusSnapshot
from benchmark_runner.common.prometheus.prometheus_snapshot_exceptions import PrometheusSnapshotError
from benchmark_runner.common.prometheus.prometheus_metrics_operations import PrometheusMetricsOperation


class BenchmarkOperatorWorkloadsOperations:
    """
    This class contains benchmark-operator workload operations
    """
    def __init__(self):
        # environment variables
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self._workload = self._environment_variables_dict.get('workload', '')
        self._workload_name = self._workload.replace('_', '-')
        self._time_stamp_format = self._environment_variables_dict.get('time_stamp_format', '')
        self._runner_version = self._environment_variables_dict.get('build_version', '')
        self._run_type = self._environment_variables_dict.get('run_type', '')
        self._workloads_odf_pvc = list(self._environment_variables_dict.get('workloads_odf_pvc', ''))
        self._odf_pvc = self._environment_variables_dict.get('odf_pvc', '')
        self._storage_type = self._environment_variables_dict.get('storage_type', '')
        self._system_metrics = self._environment_variables_dict.get('system_metrics', '')
        self._elasticsearch = self._environment_variables_dict.get('elasticsearch', '')
        self._run_artifacts = self._environment_variables_dict.get('run_artifacts', '')
        self._run_artifacts_path = self._environment_variables_dict.get('run_artifacts_path', '')
        self._date_key = self._environment_variables_dict.get('date_key', '')
        self._key = self._environment_variables_dict.get('key', '')
        self._endpoint_url = self._environment_variables_dict.get('endpoint_url', '')
        self._save_artifacts_local = self._environment_variables_dict.get('save_artifacts_local', '')
        self._enable_prometheus_snapshot = self._environment_variables_dict.get('enable_prometheus_snapshot', False)
        self._kubeadmin_password = self._environment_variables_dict.get('kubeadmin_password', '')
        self._dir_path = f'{os.path.dirname(os.path.realpath(__file__))}'
        self._pin_node_benchmark_operator = self._environment_variables_dict.get('pin_node_benchmark_operator', '')
        self._pin_node1 = self._environment_variables_dict.get('pin_node1', '')
        self._pin_node2 = self._environment_variables_dict.get('pin_node2', '')
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
        # Generate template class
        self._template = TemplateOperations(workload=self._workload)
        # set oc login
        self._oc = self.set_login(kubeadmin_password=self._kubeadmin_password)
        self._virtctl = Virtctl()
        # PrometheusSnapshot
        if self._enable_prometheus_snapshot:
            self._snapshot = PrometheusSnapshot(oc=self._oc, artifacts_path=self._run_artifacts_path, verbose=True)
        self._prometheus_metrics_operation = PrometheusMetricsOperation()
        # Extract lso id for LSO workload
        if '_lso' in self._environment_variables_dict.get('workload'):
            # Update lso_disk_id only if both worker_disk_ids and a free disk exist
            if self._environment_variables_dict.get('worker_disk_ids', '') and self._oc.get_free_disk_id(
                    node=self._environment_variables_dict['lso_node']):
                self._lso_disk_id = self._oc.get_free_disk_id(node=self._environment_variables_dict['lso_node'])
                self._environment_variables_dict['lso_disk_id'] = self._lso_disk_id
            else:
                self._lso_disk_id = self._environment_variables_dict.get('lso_disk_id', '')
        else:
            self._lso_disk_id = None

    def set_login(self, kubeadmin_password: str = ''):
        """
        This method sets oc login
        :param kubeadmin_password:
        :return:
        """
        self._oc = OC(kubeadmin_password=kubeadmin_password)
        self._oc.login()
        return self._oc

    @logger_time_stamp
    def update_node_selector(self, runner_path: str = environment_variables.environment_variables_dict['runner_path'], yaml_path: str = '', pin_node: str = ''):
        """
        This method updates node selector in yaml
        @return:
        """
        data = []
        # Read YAML file and inject node selector in the right place
        with open(os.path.join(runner_path, yaml_path), 'r') as stream:
            try:
                documents = yaml.safe_load_all(stream)
                for doc in documents:
                    if doc.get('spec'):
                        doc['spec']['template']['spec']['nodeSelector'] = {
                            'kubernetes.io/hostname': f"{self._environment_variables_dict.get(pin_node, '')}"}
                    data.append(doc)
            except yaml.YAMLError as exc:
                logger.error(exc)

        # Write YAML file
        with open(os.path.join(self._environment_variables_dict.get('runner_path', ''),
                               'benchmark-operator/config/manager/manager.yaml'), 'w', encoding='utf8') as outfile:
            yaml.safe_dump_all(data, outfile, default_flow_style=False, allow_unicode=True)

    @typechecked()
    @logger_time_stamp
    def make_deploy_benchmark_controller_manager(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
        This method deploys the benchmark operator
        :return:
        """
        benchmark_operator_path = 'benchmark-operator'
        current_dir = os.getcwd()
        os.chdir(os.path.join(runner_path, benchmark_operator_path))
        # Patch for custom image: export IMG=quay.io/user/benchmark-operator:latest;
        self._ssh.run('make deploy')
        self._oc.wait_for_pod_create(pod_name='benchmark-controller-manager')
        self._oc.wait_for_initialized(label='control-plane=controller-manager', label_uuid=False)
        self._oc.wait_for_ready(label='control-plane=controller-manager', label_uuid=False)
        os.chdir(current_dir)

    @typechecked()
    @logger_time_stamp
    def make_undeploy_benchmark_controller_manager(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
       This method removes a benchmark-operator deployment
        :return:
        """
        benchmark_operator_path = 'benchmark-operator'
        current_dir = os.getcwd()
        os.chdir(os.path.join(runner_path, benchmark_operator_path))
        self._ssh.run('make undeploy')
        self._oc.wait_for_pod_terminate(pod_name='benchmark-controller-manager')
        os.chdir(current_dir)

    @logger_time_stamp
    def make_undeploy_benchmark_controller_manager_if_exist(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
        This method undeploys benchmark controller manager, if it exists
        @return:
        """
        # delete benchmark-operator pod if exist
        if self._oc.pod_exists(pod_name='benchmark-controller-manager'):
            logger.info('make undeploy benchmark operator running pod')
            self.make_undeploy_benchmark_controller_manager(runner_path=runner_path)

    @logger_time_stamp
    def login(self):
        """
        This method logs in to the cluster
        """
        self._oc.login()

    @logger_time_stamp
    def tear_down_pod_after_error(self, yaml: str, pod_name: str):
        """
        This method tears down pod in case of error
        @param yaml:
        @param pod_name:
        @return:
        """
        self._oc.delete_pod_sync(yaml=yaml, pod_name=pod_name)
        self.delete_all()
        self.make_undeploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

    @logger_time_stamp
    def tear_down_vm_after_error(self, yaml: str, vm_name: str):
        """
        This method tears down vm in case of error
        @param yaml:
        @param vm_name:
        """
        self._oc.delete_vm_sync(yaml=yaml, vm_name=vm_name)
        self.delete_all()
        self.make_undeploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

    @logger_time_stamp
    def system_metrics_collector(self, workload: str, es_fetch_min_time: int = None):
        """
        This method runs system metrics collector
        @param workload: the workload
        @param es_fetch_min_time:
        :return:
        """
        if self._run_type == 'test_ci':
            es_index = 'system-metrics-test-ci'
        else:
            es_index = 'system-metrics'
        self._oc.wait_for_pod_create(pod_name='system-metrics-collector')
        self._oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
        self._oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
        # verify that data upload to elastic search
        if self._es_host:
            # es_fetch_min_time: if we need to fetch more time
            if es_fetch_min_time:
                self._verify_elasticsearch_data_uploaded(index=es_index, uuid=self._oc.get_long_uuid(workload=workload), workload='system-metrics', fast_check=True, es_fetch_min_time=es_fetch_min_time)
            else:
                self._verify_elasticsearch_data_uploaded(index=es_index, uuid=self._oc.get_long_uuid(workload=workload), workload='system-metrics', fast_check=True)

    def __get_metadata(self, kind: str = None, database: str = None, status: str = None, run_artifacts_url: str = None, uuid: str = None, prometheus_result: dict = None) -> dict:
        """
        This method returns metadata for a run, optionally filtered by runtime kind and database
        @param kind: optionally: pod, vm, or kata
        @param database: optional:mssql, postgres or mariadb
        @param status:
        @param run_artifacts_url:
        :return:
        """
        date_format = '%Y_%m_%d'
        metadata = {'ocp_version': self._oc.get_ocp_server_version(),
                    'cnv_version': self._oc.get_cnv_version(),
                    'kata_version': self._oc.get_kata_operator_version(),
                    'kata_rpm_version': self._oc.get_kata_rpm_version(node=self._pin_node1),
                    'odf_version': self._oc.get_odf_version(),
                    'runner_version': self._runner_version,
                    'version': int(self._runner_version.split('.')[-1]),
                    'ci_date': datetime.datetime.now().strftime(date_format),
                    'pin_node_benchmark_operator': self._pin_node_benchmark_operator,
                    'pin_node1': self._pin_node1,
                    'pin_node2': self._pin_node2,
                    'storage_type': self._storage_type}
        if kind:
            metadata.update({'kind': kind})
        if status:
            metadata.update({'run_status': status})
        if run_artifacts_url:
            metadata.update({'run_artifacts_url': run_artifacts_url})
        if database:
            metadata.update({'vm_os_version': 'centos-stream8'})
        else:
            metadata.update({'vm_os_version': 'fedora34'})
        if uuid:
            metadata.update({'uuid': uuid})
        if prometheus_result:
            metadata.update(prometheus_result)
        # for hammerdb
        if database == 'mssql':
            metadata.update({'db_version': 2019})
        elif database == 'postgres':
            metadata.update({'db_version': 10})
        elif database == 'mariadb':
            metadata.update({'db_version': 10.3})
        return metadata

    @logger_time_stamp
    def _update_elasticsearch_index(self, index: str, id: str, kind: str, status: str, run_artifacts_url: str, database: str = '', prometheus_result: dict = None):
        """
        This method updates elasticsearch id
        :param index:
        :param id:
        :param kind:
        :param database:
        :param status:
        :param run_artifacts_url:
        :return:
        """
        self.__es_operations.update_elasticsearch_index(index=index, id=id, metadata=self.__get_metadata(kind=kind, database=database, status=status, run_artifacts_url=run_artifacts_url, prometheus_result=prometheus_result))

    def _upload_to_elasticsearch(self, index: str, kind: str, status: str, run_artifacts_url: str, database: str = '', uuid: str = ''):
        """
        This method uploads data to elasticsearch
        :param index:
        :param kind:
        :param status:
        :param run_artifacts_url:
        :param database:
        :return:
        """
        self.__es_operations.upload_to_elasticsearch(index=index, data=self.__get_metadata(kind=kind, database=database, status=status, run_artifacts_url=run_artifacts_url, uuid=uuid))

    def _verify_elasticsearch_data_uploaded(self, index: str, uuid: str, workload: str = '', fast_check: bool = False, timeout: int = None, es_fetch_min_time: int = None):
        """
        This method verifies that elasticsearch data uploaded
        :param index:
        :param uuid:
        :param workload:
        :param fast_check:
        :param timeout:
        :return: ids
        """
        if workload:
            return self.__es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=uuid, workload=workload, fast_check=fast_check, timeout=timeout, es_fetch_min_time=es_fetch_min_time)
        else:
            return self.__es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=uuid, workload=self._workload_name, fast_check=fast_check, timeout=timeout, es_fetch_min_time=es_fetch_min_time)

    def _upload_workload_to_elasticsearch(self, index: str, kind: str, status: str, result: dict = None):
        """
        This method uploads to elasticsearch
        :param index:
        :param kind:
        :param status:
        :param result:
        :return:
        """
        self.__es_operations.upload_to_elasticsearch(index=index, data=self.__get_metadata(kind=kind, status=status, result=result))

    def _verify_elasticsearch_workload_data_uploaded(self, index: str, uuid: str):
        """
        This method verifies that elasticsearch data was uploaded
        :param index:
        :param uuid:
        :return:
        """
        self.__es_operations.verify_elasticsearch_data_uploaded(index=index, uuid=uuid)

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

    def _create_pod_log(self, label: str = '', database: str = '') -> str:
        """
        This method creates pod log per workload
        :param label:pod label
        :param database:
        :return:
        """
        pod_name = self._oc.get_pod(label=label, database=database)
        if database:
            self._oc.save_pod_log(pod_name=pod_name, database=database)
        else:
            self._oc.save_pod_log(pod_name=pod_name)

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

    def _create_run_artifacts(self, workload: str = '', database: str = '', labels: list = [], pod: bool = True):
        """
        This method creates pod logs of benchmark-controller-manager, system-metrics and workload pod
        :param workload: workload name
        :param database: database name
        :param pod: False in case of vm
        :param labels: list of labels of pod names - using it when it different from workload name
        :return: run artifacts url
        """
        self._create_pod_log(label='benchmark-controller-manager')
        if environment_variables.environment_variables_dict['system_metrics']:
            self._create_pod_log(label='system-metrics')
        # for vm call to create_vm_log
        if pod:
            # workload that contains 2 pods
            if labels:
                for label in labels:
                    self._create_pod_log(label=label)
            else:
                self._create_pod_log(label=workload)
            if database:
                self._create_pod_log(database=database)
        workload_name = self._workload_name
        return os.path.join(self._environment_variables_dict.get('run_artifacts_url', ''), f'{self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')

    def __make_run_artifacts_tarfile(self, workload: str):
        """
        This method compresses the log file and returns the compressed path
        :return:
        """
        tar_run_artifacts_path = f"{self._run_artifacts_path}.tar.gz"
        with tarfile.open(tar_run_artifacts_path, mode='w:gz') as archive:
            archive.add(self._run_artifacts_path, arcname=f'{workload}-{self._time_stamp_format}', recursive=True)
        return tar_run_artifacts_path

    @logger_time_stamp
    def delete_local_artifacts(self):
        """
        This method deletes local artifacts
        :return:
        """
        workload = self._workload_name
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        # remove local run artifacts workload folder
        # verify that its not empty path
        if len(self._run_artifacts_path) > 3 and self._run_artifacts_path != '/' and self._run_artifacts_path and tar_run_artifacts_path and os.path.isfile(tar_run_artifacts_path) and not self._save_artifacts_local:
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
        workload = self._workload_name
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        run_artifacts_hierarchy = self._get_run_artifacts_hierarchy(workload_name=workload)
        # Upload when endpoint_url is not None
        s3operations = S3Operations()
        # change workload to key convention
        upload_file = f"{workload}-{self._time_stamp_format}.tar.gz"
        s3operations.upload_file(file_name_path=tar_run_artifacts_path,
                                 bucket=self._environment_variables_dict.get('bucket', ''),
                                 key=run_artifacts_hierarchy,
                                 upload_file=upload_file)

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

    @logger_time_stamp
    def verify_lso(self):
        """
        This method verifies that lso path exist
        :return:
        """
        if not self._lso_disk_id:
            raise EmptyLSOPath()

    @logger_time_stamp
    def delete_all(self):
        """
        This method deletes all pod or unbound pv in namespace
        :return:
        """
        # make undeploy benchmark controller manager if exist
        self.make_undeploy_benchmark_controller_manager_if_exist(runner_path=environment_variables.environment_variables_dict['runner_path'])
        if 'hammerdb' in self._workload:
            self._oc.delete_namespace(namespace=f"{self._workload.split('_')[2]}-db")
        if self._storage_type == 'lso':
            self._oc.delete_available_released_pv()
            self._oc.remove_lso_path()

    @logger_time_stamp
    def clear_nodes_cache(self):
        """
        This method clears nodes cache
        """
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
        self.delete_all()
        self.clear_nodes_cache()
        if self._odf_pvc:
            self.odf_workload_verification()
        if 'lso' in self._workload:
            self.verify_lso()
        # make deploy benchmark controller manager
        self.make_deploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])
        self._template.generate_yamls()
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
        self.delete_all()
