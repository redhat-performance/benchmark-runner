
import os
import time
import yaml
import datetime
import tarfile
import shutil
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import VMNotCompletedTimeout
from benchmark_runner.benchmark_operator.workload_flavors.generate_yaml_from_workload_flavors import TemplateOperations
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.benchmark_operator.benchmark_operator_exceptions import OCSNonInstalled, SystemMetricsRequiredElasticSearch
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.clouds.IBM.ibm_operations import IBMOperations
from benchmark_runner.common.clouds.shared.s3.s3_operations import S3Operations
from benchmark_runner.common.prometheus.prometheus_snapshot import PrometheusSnapshot
from benchmark_runner.common.prometheus.prometheus_snapshot_exceptions import PrometheusSnapshotError


class BenchmarkOperatorWorkloads:
    """
    This class contains all the custom_workloads
    """
    def __init__(self, kubeadmin_password: str = '', es_host: str = '', es_port: str = ''):
        # environment variables
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__time_stamp_format = self.__environment_variables_dict.get('time_stamp_format', '')
        self.__runner_version = self.__environment_variables_dict.get('build_version', '')
        self.__run_type = self.__environment_variables_dict.get('run_type', '')
        self.__system_metrics = self.__environment_variables_dict.get('system_metrics', '')
        self.__elasticsearch = self.__environment_variables_dict.get('elasticsearch', '')
        self.__run_artifacts = self.__environment_variables_dict.get('run_artifacts', '')
        self.__run_artifacts_path = self.__environment_variables_dict.get('run_artifacts_path', '')
        self.__date_key = self.__environment_variables_dict.get('date_key', '')
        self.__key = self.__environment_variables_dict.get('key', '')
        self.__endpoint_url = self.__environment_variables_dict.get('endpoint_url', '')
        self.__save_artifacts_local = self.__environment_variables_dict.get('save_artifacts_local', '')
        self.__enable_prometheus_snapshot = self.__environment_variables_dict.get('enable_prometheus_snapshot', '')
        self.__ssh = SSH()
        self.__kubeadmin_password = kubeadmin_password
        self.__oc = OC(kubeadmin_password=self.__kubeadmin_password)
        self.__dir_path = f'{os.path.dirname(os.path.realpath(__file__))}'
        self.__current_run_path = os.path.join(f'{self.__dir_path}/workload_flavors/current_run')
        self.__es_host = es_host
        self.__es_port = es_port
        if es_host and es_port:
            self.__es_operations = ESOperations(es_host=self.__es_host, es_port=self.__es_port)
        # Generate workload_flavors class
        self.__template = TemplateOperations()

        # Login when kubeadmin_password
        if self.__environment_variables_dict.get('kubeadmin_password', ''):
            self.__oc.login()

    def __remove_current_run_yamls(self, extension='.yaml'):
        """
        This method remove all current run yamls files
        :return:
        """
        name_list = []
        for file in os.listdir(self.__current_run_path):
            if file.endswith(extension):
                os.remove(os.path.join(self.__current_run_path, file))
        return name_list

    def __remove_run_workload_yaml_file(self, workload_full_name: str):
        """
        This method remove run file if exist
        :return:
        """
        yaml_file = os.path.join(self.__current_run_path, f'{workload_full_name}.yaml')
        if os.path.isfile(yaml_file):
            os.remove(os.path.join(self.__current_run_path, f'{workload_full_name}.yaml'))
            if 'hammerdb_pod' in workload_full_name or 'hammerdb_kata' in workload_full_name:
                names = workload_full_name.split('_')
                os.remove(os.path.join(self.__current_run_path, f'{names[-1]}.yaml'))
        else:
            logger.info('yaml file {} does not exist')

    def __check_elasticsearch_exist_for_system_metrics(self):
        """
        This method check if elasticsearch exist for system metrics
        :return:
        """
        if self.__system_metrics == 'True':
            if not self.__elasticsearch:
                raise SystemMetricsRequiredElasticSearch()

    @logger_time_stamp
    def update_node_selector(self, runner_path: str = environment_variables.environment_variables_dict['runner_path'], yaml_path: str = '', pin_node: str = ''):
        """
        This method update node selector in yaml
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
                            'kubernetes.io/hostname': f"{self.__environment_variables_dict.get(pin_node, '')}"}
                    data.append(doc)
            except yaml.YAMLError as exc:
                print(exc)

        # Write YAML file
        with open(os.path.join(self.__environment_variables_dict.get('runner_path', ''),
                               'benchmark-operator/config/manager/manager.yaml'), 'w', encoding='utf8') as outfile:
            yaml.safe_dump_all(data, outfile, default_flow_style=False, allow_unicode=True)

    @logger_time_stamp
    def remove_if_exist_run_yaml(self, extension: str = '.yaml'):
        """
        This method remove all run yaml files in yaml folder
        :return:
        """
        for file in os.listdir(self.__current_run_path):
            if file.endswith(extension):
                self.__oc._delete_async(yaml=os.path.join(self.__current_run_path, file))
                # wait 10 sec till terminate
                time.sleep(10)
                os.remove(os.path.join(self.__current_run_path, file))
                logger.info(f'Delete exist workload file {file}')

    @typechecked()
    @logger_time_stamp
    def make_deploy_benchmark_controller_manager(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
        This method make deploy benchmark operator
        :return:
        """
        benchmark_operator_path = 'benchmark-operator'
        current_dir = os.getcwd()
        os.chdir(os.path.join(runner_path, benchmark_operator_path))
        # Patch for custom image: export IMG=quay.io/user/benchmark-operator:latest;
        self.__ssh.run('make deploy')
        self.__oc.wait_for_pod_create(pod_name='benchmark-controller-manager')
        self.__oc.wait_for_initialized(label='control-plane=controller-manager', label_uuid=False)
        self.__oc.wait_for_ready(label='control-plane=controller-manager', label_uuid=False)
        os.chdir(current_dir)

    @typechecked()
    @logger_time_stamp
    def make_undeploy_benchmark_controller_manager(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
        This method make undeploy benchmark operator
        :return:
        """
        benchmark_operator_path = 'benchmark-operator'
        current_dir = os.getcwd()
        os.chdir(os.path.join(runner_path, benchmark_operator_path))
        self.__ssh.run('make undeploy')
        self.__oc.wait_for_pod_terminate(pod_name='benchmark-controller-manager')
        os.chdir(current_dir)

    @logger_time_stamp
    def make_undeploy_benchmark_controller_manager_if_exist(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
        This method make undeploy benchmark controller manager if exist
        @return:
        """
        # delete benchmark-operator pod if exist
        if self.__oc._is_pod_exist(pod_name='benchmark-controller-manager'):
            logger.info('make undeploy benchmark operator running pod')
            self.make_undeploy_benchmark_controller_manager(runner_path=runner_path)

    @typechecked()
    @logger_time_stamp
    def helm_install_benchmark_operator(self, runner_path: str = environment_variables.environment_variables_dict['runner_path']):
        """
        This method install benchmark operator
        :return:
        """
        benchmark_operator_path = 'benchmark-operator/charts/benchmark-operator'
        current_dir = os.getcwd()
        os.chdir(os.path.join(runner_path, benchmark_operator_path))
        self.__ssh.run('/usr/local/bin/helm install benchmark-operator . -n benchmark-operator --create-namespace')
        self.__oc.wait_for_pod_create(pod_name='benchmark-operator')
        self.__ssh.run('oc adm policy -n benchmark-operator add-scc-to-user privileged -z benchmark-operator')
        os.chdir(current_dir)

    @logger_time_stamp
    def delete_benchmark_operator_if_exist(self):
        """
        This method delete benchmark operator if exist
        @return:
        """
        # delete benchmark-operator pod if exist
        if self.__oc._is_pod_exist(pod_name='benchmark-operator', namespace=environment_variables.environment_variables_dict['namespace']):
            logger.info('delete benchmark operator running pod')
            self.helm_delete_benchmark_operator()

    @logger_time_stamp
    def helm_delete_benchmark_operator(self):
        """
        This method delete benchmark operator
        :return:
        """
        self.__ssh.run('/usr/local/bin/helm delete benchmark-operator -n benchmark-operator')
        self.__oc.wait_for_pod_terminate(pod_name='benchmark-operator')

    @logger_time_stamp
    def login(self):
        """
        This method login to the cluster
        """
        self.__oc.login()

    @logger_time_stamp
    def tear_down_pod_after_error(self, yaml: str, pod_name: str):
        """
        This method tear down pod in case of error
        @param yaml:
        @param pod_name:
        @return:
        """
        self.__oc.delete_pod_sync(yaml=yaml, pod_name=pod_name)
        self.remove_if_exist_run_yaml()
        self.make_undeploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

    @logger_time_stamp
    def tear_down_vm_after_error(self, yaml: str, vm_name: str):
        """
        This method tear down vm in case of error
        @param yaml:
        @param vm_name:
        """
        self.__oc.delete_vm_sync(yaml=yaml, vm_name=vm_name)
        self.remove_if_exist_run_yaml()
        self.make_undeploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

    @logger_time_stamp
    def system_metrics_collector(self, workload: str):
        """
        This method run system metrics collector
        @param workload: the workload
        :return:
        """
        if self.__run_type == 'test_ci':
            es_index = 'system-metrics-test-ci'
        else:
            es_index = 'system-metrics'
        self.__oc.wait_for_pod_create(pod_name='system-metrics-collector')
        self.__oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
        self.__oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
        # verify that data upload to elastic search
        if self.__es_host:
            self.__es_operations.verify_es_data_uploaded(index=es_index,
                                                         uuid=self.__oc.get_long_uuid(workload=workload), fast_check=True)

    def get_metadata(self, kind: str = None, database: str = None, status: str = None, run_artifacts_url: str = None) -> dict:
        """
        This method return metadata kind and database argument are optional
        @param kind: optional: pod, vm, or kata
        @param database: optional:mssql, postgres or mariadb
        @param status:
        @param run_artifacts_url:
        :return:
        """
        date_format = '%Y_%m_%d'
        metadata = {'ocp_version': self.__oc.get_ocp_server_version(),
                    'cnv_version': self.__oc.get_cnv_version(),
                    'kata_version': self.__oc.get_kata_version(),
                    'ocs_version': self.__oc.get_ocs_version(),
                    'runner_version': self.__runner_version,
                    'version': int(self.__runner_version.split('.')[-1]),
                    'ci_date': datetime.datetime.now().strftime(date_format)}
        if kind:
            metadata.update({'kind': kind})
        if status:
            metadata.update({'run_status': status})
        if run_artifacts_url:
            metadata.update({'run_artifacts_url': run_artifacts_url})
        if database:
            metadata.update({'vm_os_version': 'centos8'})
        else:
            metadata.update({'vm_os_version': 'fedora34'})

        # for hammerdb
        if database == 'mssql':
            metadata.update({'db_version': 2019})
        elif database == 'postgres':
            metadata.update({'db_version': 10})
        elif database == 'mariadb':
            metadata.update({'db_version': 10.3})
        return metadata

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
        status_dict = {'failed': 0, 'pass': 1}
        metadata = self.get_metadata()
        if ocp_resource_install_minutes_time != 0:
            ibm_operations = IBMOperations(user=self.__environment_variables_dict.get('provision_user', ''))
            ibm_operations.ibm_connect()
            ocp_install_minutes_time = ibm_operations.get_ocp_install_time()
            ibm_operations.ibm_disconnect()
        metadata.update({'status': status, 'status#': status_dict[status], 'ci_minutes_time': ci_minutes_time, 'benchmark_operator_id': benchmark_operator_id, 'benchmark_wrapper_id': benchmark_wrapper_id, 'ocp_install_minutes_time': ocp_install_minutes_time, 'ocp_resource_install_minutes_time': ocp_resource_install_minutes_time})
        self.__es_operations.upload_to_es(index='ci-status', data=metadata)

    def __create_vm_log(self, labels: list):
        """
        This method set vm log per workload
        :param labels: list of labels
        :return:
        """
        for label in labels:
            vm_name = self.__oc.get_vm(label=label)
            self.__oc.save_vm_log(vm_name=vm_name)

    def __create_pod_log(self, label: str = '', database: str = '') -> str:
        """
        This method create pod log per workload
        :param label:pod label
        :param database:
        :return:
        """
        pod_name = self.__oc.get_pod(label=label, database=database)
        if database:
            self.__oc.save_pod_log(pod_name=pod_name, database=database)
        else:
            self.__oc.save_pod_log(pod_name=pod_name)

    def __get_run_artifacts_hierarchy(self, workload_name: str = ''):
        """
        This method return log hierarchy
        :param workload_name: workload name
        :return:
        """
        key = self.__key
        run_type = self.__run_type.replace('_', '-')
        date_key = self.__date_key
        if workload_name:
            return os.path.join(key, run_type, date_key, workload_name)
        return os.path.join(key, run_type, date_key)

    def __create_run_artifacts(self, workload: str = '', database: str = '', labels: list = [], pod: bool = True):
        """
        This method create pod logs of benchmark-controller-manager, system-metrics and workload pod
        :param workload: workload name
        :param database: database name
        :param pod: False in case of vm
        :param labels: list of labels of pod names - using it when it different from workload name
        :return: run artifacts url
        """
        self.__create_pod_log(label='benchmark-controller-manager')
        self.__create_pod_log(label='system-metrics')
        # for vm call to create_vm_log
        if pod:
            # workload that contains 2 pods
            if labels:
                for label in labels:
                    self.__create_pod_log(label=label)
            else:
                self.__create_pod_log(label=workload)
            if database:
                self.__create_pod_log(database=database)
        workload_name = self.__environment_variables_dict.get('workload', '').replace('_', '-')
        return os.path.join(self.__environment_variables_dict.get('run_artifacts_url', ''), f'{self.__get_run_artifacts_hierarchy(workload_name=workload_name)}-{self.__time_stamp_format}.tar.gz')

    def __make_run_artifacts_tarfile(self, workload: str):
        """
        This method tar.gz log path and return the tar.gz path
        :return:
        """
        tar_run_artifacts_path = f"{self.__run_artifacts_path}.tar.gz"
        with tarfile.open(tar_run_artifacts_path, mode='w:gz') as archive:
            archive.add(self.__run_artifacts_path, arcname=f'{workload}-{self.__time_stamp_format}', recursive=True)
        return tar_run_artifacts_path

    @logger_time_stamp
    def upload_run_artifacts_to_s3(self, workload: str):
        """
        This method uploads log to s3
        :param workload:
        :return:
        """
        workload = workload.replace('_', '-')
        tar_run_artifacts_path = self.__make_run_artifacts_tarfile(workload)
        run_artifacts_hierarchy = self.__get_run_artifacts_hierarchy()
        # Upload when endpoint_url is not None
        if self.__endpoint_url:
            s3operations = S3Operations()
            # change workload to key convention
            upload_file = f"{workload}-{self.__time_stamp_format}.tar.gz"
            s3operations.upload_file(file_name_path=tar_run_artifacts_path,
                                     bucket=self.__environment_variables_dict.get('bucket', ''),
                                     key=run_artifacts_hierarchy,
                                     upload_file=upload_file)
        # remove local run artifacts workload folder
        # verify that its not empty path
        if len(self.__run_artifacts_path) > 3 and self.__run_artifacts_path != '/' and self.__run_artifacts_path and tar_run_artifacts_path and os.path.isfile(tar_run_artifacts_path) and not self.__save_artifacts_local:
            # remove run_artifacts_path
            shutil.rmtree(path=self.__run_artifacts_path)
            # remove tar.gz file
            os.remove(path=tar_run_artifacts_path)



#***********************************************************************************************
######################################## Workloads #############################################
#***********************************************************************************************


    @typechecked
    @logger_time_stamp
    def stressng_pod(self, name: str = ''):
        """
        This method run stressng workload
        :return:
        """
        try:
            if name == '':
                name = self.stressng_pod.__name__
            workload = name.replace('_', '-')
            kind = 'pod'
            if '_kata' in name:
                kind = 'kata'
            if self.__run_type == 'test_ci':
                es_index = 'stressng-test-ci-results'
            else:
                es_index = 'stressng-results'
            environment_variables.environment_variables_dict['kind'] = kind
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'), pod_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=stressng_workload', workload=workload)
            status = self.__oc.wait_for_pod_completed(label='app=stressng_workload', workload=workload)
            status = 'complete' if status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(workload=workload)
            if self.__es_host:
                # verify that data upload to elastic search according to unique uuid
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind=kind, status=status, run_artifacts_url=run_artifacts_url))
            self.__oc.delete_pod_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                pod_name=f'{workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{workload}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(workload=workload)
            self.__es_operations.upload_to_es(index=es_index, data=self.get_metadata(kind=kind, status='failed', run_artifacts_url=run_artifacts_url))
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{workload}-workload')
            raise err

    # The Kata workloads should not be decorated with
    @logger_time_stamp
    def stressng_kata(self):
        """
        This method run stressng kata workload
        :return:
        """
        self.stressng_pod(self.stressng_kata.__name__)

    @logger_time_stamp
    def stressng_vm(self):
        """
        This method run stressng vm workload
        :return:
        """
        try:
            if self.__run_type == 'test_ci':
                es_index = 'stressng-test-ci-results'
            else:
                es_index = 'stressng-results'
            workload = self.stressng_vm.__name__.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'), vm_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=stressng_workload', workload=workload)
            # Create vm log should be direct after vm is ready
            self.__create_vm_log(labels=[workload])
            status = self.__oc.wait_for_vm_completed(workload=workload)
            status = 'complete' if status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self.__create_run_artifacts(workload=workload, pod=False)
            # verify that data upload to elastic search
            if self.__es_host:
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind=self.__environment_variables_dict.get('kind', ''), status=status, run_artifacts_url=run_artifacts_url))
            self.__oc.delete_vm_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                vm_name=f'{workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(workload=workload, pod=False)
            self.__es_operations.upload_to_es(index=es_index, data=self.get_metadata(kind=self.__environment_variables_dict.get('kind', ''), status='failed', run_artifacts_url=run_artifacts_url))
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise err

    @typechecked
    @logger_time_stamp
    def uperf_pod(self, name: str = ''):
        """
        This method run uperf workload
        :return:
        """
        try:
            if name == '':
                name = self.uperf_pod.__name__
            workload = name.replace('_', '-')
            kind = 'pod'
            if '_kata' in name:
                kind = 'kata'
            if self.__run_type == 'test_ci':
                es_index = 'uperf-test-ci-results'
            else:
                es_index = 'uperf-results'
            environment_variables.environment_variables_dict['kind'] = kind
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-server')
            # uperf server
            server_name = self.__environment_variables_dict.get('pin_node1', '')
            if server_name:
                # uperf server name is limited up to 27 chars
                if len(server_name) > 27:
                    server_name = server_name[:28]
                label = f'app=uperf-bench-server-{server_name}-0'
                self.__oc.wait_for_initialized(label=label, workload=workload)
                self.__oc.wait_for_ready(label=label, workload=workload)
            # in case that no pin node
            else:
                label = f'benchmark-operator-workload=uperf'
                self.__oc.wait_for_initialized(label=label, workload=workload, label_uuid=False)
                self.__oc.wait_for_ready(label=label, workload=workload, label_uuid=False)
            # uperf client
            self.__oc.wait_for_pod_create(pod_name='uperf-client')
            self.__oc.wait_for_initialized(label='app=uperf-bench-client', workload=workload)
            self.__oc.wait_for_ready(label='app=uperf-bench-client', workload=workload)
            status = self.__oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=workload)
            status = 'complete' if status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(workload=workload, labels=['uperf-client', 'uperf-server'])
            if self.__es_host:
                # verify that data upload to elastic search
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload), workload=name)
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind=kind, status=status, run_artifacts_url=run_artifacts_url))
            self.__oc.delete_pod_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'),
                pod_name=f'uperf-client')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(workload=workload, labels=['uperf-client', 'uperf-server'])
            self.__es_operations.upload_to_es(index=es_index, data=self.get_metadata(kind=kind, status='failed', run_artifacts_url=run_artifacts_url))
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err

    @logger_time_stamp
    def uperf_kata(self):
        """
        This method run uperf kata workload
        :return:
        """
        self.uperf_pod(self.uperf_kata.__name__)

    @logger_time_stamp
    def uperf_vm(self):
        """
        This method run uperf vm workload
        :return:
        """
        try:
            if self.__run_type == 'test_ci':
                es_index = 'uperf-test-ci-results'
            else:
                es_index = 'uperf-results'
            workload = self.uperf_vm.__name__.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            # uperf server
            self.__oc.wait_for_vm_create(vm_name='uperf-server')
            self.__oc.wait_for_initialized(label='app=uperf-bench-server-0', workload=workload)
            self.__oc.wait_for_ready(label='app=uperf-bench-server-0', workload=workload)
            # client server
            self.__oc.wait_for_vm_create(vm_name='uperf-client')
            self.__oc.wait_for_initialized(label='app=uperf-bench-client', workload=workload)
            self.__oc.wait_for_ready(label='app=uperf-bench-client', workload=workload)
            # Create vm log should be direct after vm is ready
            self.__create_vm_log(labels=['uperf-server', 'uperf-client'])
            status = self.__oc.wait_for_vm_completed(workload=workload)
            status = 'complete' if status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self.__create_run_artifacts(workload=workload, pod=False)
            # verify that data upload to elastic search
            if self.__es_host:
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload), workload=self.uperf_vm.__name__)
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind=self.__environment_variables_dict.get('kind', ''), status=status, run_artifacts_url=run_artifacts_url))
            self.__oc.delete_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'),
                                     vm_name='uperf-server')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err
        except Exception as err:
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self.__create_run_artifacts(workload=workload, pod=False)
            self.__es_operations.upload_to_es(index=es_index, data=self.get_metadata(kind=self.__environment_variables_dict.get('kind', ''), status=status, run_artifacts_url=run_artifacts_url))
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err

    @typechecked
    @logger_time_stamp
    def hammerdb_pod(self, database: str, name: str = ''):
        """
        This method run hammerdb pod workload
        :return:
        """
        try:
            if name == '':
                name = self.hammerdb_pod.__name__
            workload = name.replace('_', '-')
            kind = 'pod'
            if '_kata' in name:
                kind = 'kata'
            if self.__run_type == 'test_ci':
                es_index = 'hammerdb-test-ci-results'
            else:
                es_index = 'hammerdb-results'
            environment_variables.environment_variables_dict['kind'] = kind
            # database
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database, namespace=f'{database}-db')
            self.__oc.wait_for_initialized(label=f'app={database}', workload=database, namespace=f'{database}-db', label_uuid=False)
            self.__oc.wait_for_ready(label=f'app={database}', workload=database, namespace=f'{database}-db', label_uuid=False)
            # hammerdb
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'), pod_name=f'{workload}-creator')
            # hammerdb creator
            self.__oc.wait_for_pod_create(pod_name=f'{workload}-creator')
            self.__oc.wait_for_initialized(label='app=hammerdb_creator', workload=workload)
            self.__oc.wait_for_ready(label='app=hammerdb_creator', workload=workload)
            self.__oc.wait_for_pod_completed(label='app=hammerdb_creator', workload=workload)
            # hammerdb workload
            self.__oc.wait_for_pod_create(pod_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=hammerdb_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=hammerdb_workload', workload=workload)
            status = self.__oc.wait_for_pod_completed(label='app=hammerdb_workload', workload=workload)
            status = 'complete' if status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(labels=[f'{workload}-creator', f'{workload}-workload'], database=database)
            if self.__es_host:
                # verify that data upload to elastic search
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind=kind, database=database, status=status, run_artifacts_url=run_artifacts_url))
            # delete hammerdb
            self.__oc.delete_pod_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                pod_name=f'{workload}-creator')
            # delete database
            self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'),
                                      pod_name=database,
                                      namespace=f'{database}-db')
        except ElasticSearchDataNotUploaded as err:
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{workload}-creator')
            # delete database
            self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database,
                                      namespace=f'{database}-db')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self.__create_run_artifacts(labels=[f'{workload}-creator', f'{workload}-workload'], database=database)
            self.__es_operations.upload_to_es(index=es_index, data=self.get_metadata(kind=kind, database=database, status='failed', run_artifacts_url=run_artifacts_url))
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{workload}-creator')
            # delete database
            self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database,
                                      namespace=f'{database}-db')
            raise err

    @typechecked
    @logger_time_stamp
    def hammerdb_kata(self, database: str):
        """
        This method run hammerdb kata workload
        :return:
        """
        self.hammerdb_pod(database, self.hammerdb_kata.__name__)

    @typechecked
    @logger_time_stamp
    def hammerdb_vm(self, database: str):
        """
        This method run hammerdb vm workload
        :return:
        """
        try:
            if self.__run_type == 'test_ci':
                es_index = 'hammerdb-test-ci-results'
            else:
                es_index = 'hammerdb-results'
            workload = self.hammerdb_vm.__name__.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'), vm_name=f'{workload}-workload')
            # hammerdb workload and database
            self.__oc.wait_for_vm_create(vm_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=hammerdb_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=hammerdb_workload', workload=workload)
            # Create vm log should be direct after vm is ready
            self.__create_vm_log(labels=[workload])
            status = self.__oc.wait_for_vm_completed(workload=workload)
            status = 'complete' if status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self.__create_run_artifacts(workload=workload, pod=False)
            # verify that data upload to elastic search
            if self.__es_host:
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind=self.__environment_variables_dict.get('kind', ''), database=database, status=status, run_artifacts_url=run_artifacts_url))
            self.__oc.delete_vm_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                vm_name=f'{workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise VMNotCompletedTimeout(workload=workload)
        except Exception as err:
            run_artifacts_url = self.__create_run_artifacts(workload=workload, pod=False)
            self.__es_operations.upload_to_es(index=es_index, data=self.get_metadata(kind=self.__environment_variables_dict.get('kind', ''), database=database, status=status, run_artifacts_url=run_artifacts_url))
            # delete hammerdb
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise err

# ***********************************************************************************************
######################################## End Workloads #############################################
# ***********************************************************************************************

    @typechecked
    @logger_time_stamp
    def run_workload_func(self, workload_full_name: str):
        """
        The method run specific workload function according to the workload string
        :param workload_full_name:
        :return:
        """
        # remove running workloads if exist
        self.remove_if_exist_run_yaml()
        workload_name = workload_full_name.split('_')

        self.__template.generate_yamls(workload=workload_full_name)
        if 'hammerdb' in workload_full_name:
            # check if ocs is installed
            if self.__environment_variables_dict.get('ocs_pvc', '') == 'True':
                if not self.__oc.is_ocs_installed():
                    raise OCSNonInstalled()
            class_method = getattr(BenchmarkOperatorWorkloads, f'{workload_name[0]}_{workload_name[1]}')
            class_method(self, workload_name[2])
        else:
            class_method = getattr(BenchmarkOperatorWorkloads, workload_full_name)
            class_method(self)
        # remove workload yaml at the end of run
        self.__remove_run_workload_yaml_file(workload_full_name=workload_full_name)

    @logger_time_stamp
    def run_workload(self, workload: str):
        """
        This method run the input workload
        :return:
        """

        # check that there is elasticsearch when system metric is True
        self.__check_elasticsearch_exist_for_system_metrics()

        # make undeploy benchmark controller manager if exist
        self.make_undeploy_benchmark_controller_manager_if_exist(runner_path=environment_variables.environment_variables_dict['runner_path'])

        # make deploy benchmark controller manager
        self.make_deploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

        # Start collection of Prometheus snapshot
        if self.__enable_prometheus_snapshot:
            try:
                if not os.path.isdir(self.__run_artifacts_path):
                    os.mkdir(self.__run_artifacts_path)
                snapshot = PrometheusSnapshot(oc=self.__oc, artifacts_path=self.__run_artifacts_path, verbose=True)
                snapshot.prepare_for_snapshot()
            except PrometheusSnapshotError as err:
                raise PrometheusSnapshotError(err)
            except Exception as err:
                raise err

        # run workload
        self.run_workload_func(workload_full_name=workload)

        # Retrieve the Prometheus snapshot
        if self.__enable_prometheus_snapshot:
            try:
                snapshot.retrieve_snapshot()
            except PrometheusSnapshotError as err:
                raise PrometheusSnapshotError(err)
            except Exception as err:
                raise err

        # upload logs to s3
        self.upload_run_artifacts_to_s3(workload=workload)

        # make undeploy benchmark controller manager
        self.make_undeploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])
