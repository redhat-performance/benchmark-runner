
import os
import time
import yaml
import datetime
from typeguard import typechecked
from tenacity import retry, stop_after_attempt

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.common.oc.oc_exceptions import VMNotCompletedTimeout
from benchmark_runner.benchmark_operator.workload_flavors.generate_yaml_from_workload_flavors import TemplateOperations
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.main.environment_variables import environment_variables


class BenchmarkOperatorWorkloads:
    """
    This class contains all the custom_workloads
    """
    def __init__(self, kubeadmin_password: str = '', es_host: str = '', es_port: str = ''):
        # environment variables
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__runner_version = self.__environment_variables_dict.get('build_version', '')
        self.__run_type = self.__environment_variables_dict.get('run_type', '')
        self.__ssh = SSH()
        self.__kubeadmin_password = kubeadmin_password
        self.__oc = OC(kubeadmin_password=self.__kubeadmin_password)
        self.__dir_path = f'{os.path.dirname(os.path.realpath(__file__))}'
        self.__current_run_path = f'{self.__dir_path}/workload_flavors/{self.__run_type}/current_run'
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
            if 'hammerdb_pod' in workload_full_name:
                names = workload_full_name.split('_')
                os.remove(os.path.join(self.__current_run_path, f'{names[-1]}.yaml'))
        else:
            logger.info('yaml file {} does not exist')

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
        if self.__oc._is_pod_exist(pod_name='benchmark-controller-manager', namespace=environment_variables.environment_variables_dict['namespace']):
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
        @param workload:
        :return:
        """
        self.__oc.wait_for_pod_create(pod_name='system-metrics-collector')
        self.__oc.wait_for_initialized(label='app=system-metrics-collector', workload=workload)
        self.__oc.wait_for_pod_completed(label='app=system-metrics-collector', workload=workload)
        # verify that data upload to elastic search
        if self.__es_host:
            if self.__run_type == 'test_ci':
                es_index = 'system-metrics-test-ci'
            else:
                es_index = 'system-metrics'
            self.__es_operations.verify_es_data_uploaded(index=es_index,
                                                         uuid=self.__oc.get_long_uuid(workload=workload), fast_check=True)

    def get_metadata(self, kind: str = None, database: str = None):
        """
        This method return metadata kind and database argument are optional
        @param kind: optional: pod or vm
        @param database: optional:mssql, postgres or mariadb
        :return:
        """
        date_format = '%Y_%m_%d'
        metadata = {'ocp_version': self.__oc.get_ocp_server_version(),
                    'cnv_version': self.__oc.get_cnv_version(),
                    'ocs_version': self.__oc.get_ocs_version(),
                    'runner_version': self.__runner_version,
                    'version': int(self.__runner_version.split('.')[-1]),
                    'ci_date': datetime.datetime.now().strftime(date_format)}
        if kind:
            metadata.update({'kata_version': '',
                             'kind': kind,
                             'vm_os_version': 'centos8'})
        # for hammerdb
        if database == 'mssql':
            metadata.update({'db_version': 2019})
        elif database == 'postgres':
            metadata.update({'db_version': 10})
        elif database == 'mariadb':
            metadata.update({'db_version': 10.3})
        return metadata

    def update_ci_status(self, status: str, ci_minutes_time: int, benchmark_operator_id: str, benchmark_wrapper_id: str):
        """
        This method update ci status Pass/Failed
        :param benchmark_wrapper_id: benchmark_wrapper last repository commit id
        :param benchmark_operator_id: benchmark_operator last repository commit id
        :param ci_minutes_time: Ci time in minutes
        :param status: Pass/Failed
        :return:
        """
        status_dict = {'failed': 0, 'pass': 1}
        metadata = self.get_metadata()
        metadata.update({'status': status, 'status#': status_dict[status], 'ci_minutes_time': ci_minutes_time, 'benchmark_operator_id': benchmark_operator_id, 'benchmark_wrapper_id': benchmark_wrapper_id})
        self.__es_operations.upload_to_es(index='ci-status', data=metadata)

#***********************************************************************************************
######################################## Workloads #############################################
#***********************************************************************************************

    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def stressng_pod(self):
        """
        This method run stressng workload
        :return:
        """
        try:
            workload = self.stressng_pod.__name__.replace('_', '-')
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'), pod_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=stressng_workload', workload=workload)
            self.__oc.wait_for_pod_completed(label='app=stressng_workload', workload=workload)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            if self.__es_host:
                if self.__run_type == 'test_ci':
                    es_index = 'stressng-test-ci-results'
                else:
                    es_index = 'stressng-results'
                # verify that data upload to elastic search according to unique uuid
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind='pod'))
            self.__oc.delete_pod_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                pod_name=f'{workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{workload}-workload')
            raise err
        except Exception as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{workload}-workload')
            raise err

    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def stressng_vm(self):
        """
        This method run stressng vm workload
        :return:
        """
        try:
            workload = self.stressng_vm.__name__.replace('_', '-')
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'), vm_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=stressng_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=stressng_workload', workload=workload)
            self.__oc.wait_for_vm_completed(workload=workload)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
               self.system_metrics_collector(workload=workload)
            # verify that data upload to elastic search
            if self.__es_host:
                if self.__run_type == 'test_ci':
                    es_index = 'stressng-test-ci-results'
                else:
                    es_index = 'stressng-results'
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind='vm'))
            self.__oc.delete_vm_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                vm_name=f'{workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise err
        except Exception as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise err

    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def uperf_pod(self):
        """
        This method run uperf workload
        :return:
        """
        try:
            workload = self.uperf_pod.__name__.replace('_', '-')
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-server')
            # uperf server
            server_name = self.__environment_variables_dict.get('pin_node1', '')
            # name up to 27 chars
            if len(server_name) > 27:
                server_name = server_name[:28]
            self.__oc.wait_for_initialized(label=f'app=uperf-bench-server-{server_name}-0', workload=workload)
            self.__oc.wait_for_ready(label=f'app=uperf-bench-server-{server_name}-0', workload=workload)
            # uperf client
            self.__oc.wait_for_pod_create(pod_name=f'uperf-client')
            self.__oc.wait_for_initialized(label='app=uperf-bench-client', workload=workload)
            self.__oc.wait_for_ready(label='app=uperf-bench-client', workload=workload)
            self.__oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=workload)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            if self.__es_host:
                if self.__run_type == 'test_ci':
                    es_index = 'uperf-test-ci-results'
                else:
                    es_index = 'uperf-results'
                # verify that data upload to elastic search
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload), workload=self.uperf_pod.__name__)
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind='pod'))
            self.__oc.delete_pod_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'),
                pod_name=f'uperf-client')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err
        except Exception as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err

    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def uperf_vm(self):
        """
        This method run uperf vm workload
        :return:
        """
        try:
            workload = self.uperf_vm.__name__.replace('_', '-')
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            # uperf server
            self.__oc.wait_for_vm_create(vm_name='uperf-server')
            self.__oc.wait_for_initialized(label='app=uperf-bench-server-0', workload=workload)
            self.__oc.wait_for_ready(label='app=uperf-bench-server-0', workload=workload)
            # client server
            self.__oc.wait_for_vm_create(vm_name='uperf-client')
            self.__oc.wait_for_initialized(label='app=uperf-bench-client', workload=workload)
            self.__oc.wait_for_ready(label='app=uperf-bench-client', workload=workload)
            self.__oc.wait_for_vm_completed(workload=workload)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # verify that data upload to elastic search
            if self.__es_host:
                if self.__run_type == 'test_ci':
                    es_index = 'uperf-test-ci-results'
                else:
                    es_index = 'uperf-results'
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload), workload=self.uperf_vm.__name__)
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind='vm'))
            self.__oc.delete_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'),
                                     vm_name='uperf-server')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err
        except Exception as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err

    @typechecked
    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def hammerdb_pod(self, database: str):
        """
        This method run hammerdb pod workload
        :return:
        """
        try:
            workload = self.hammerdb_pod.__name__.replace('_', '-')
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
            self.__oc.wait_for_pod_completed(label='app=hammerdb_workload', workload=workload)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            if self.__es_host:
                if self.__run_type == 'test_ci':
                    es_index = 'hammerdb-test-ci-results'
                else:
                    es_index = 'hammerdb-results'
                # verify that data upload to elastic search
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind='pod', database=database))
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
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{workload}-creator')
            # delete database
            self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database,
                                      namespace=f'{database}-db')
            raise err

    @typechecked
    @logger_time_stamp
    @retry(stop=stop_after_attempt(3))
    def hammerdb_vm(self, database: str):
        """
        This method run hammerdb vm workload
        :return:
        """
        try:
            workload = self.hammerdb_vm.__name__.replace('_', '-')
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'), vm_name=f'{workload}-workload')
            # hammerdb workload and database
            self.__oc.wait_for_vm_create(vm_name=f'{workload}-workload')
            self.__oc.wait_for_initialized(label='app=hammerdb_workload', workload=workload)
            self.__oc.wait_for_ready(label='app=hammerdb_workload', workload=workload)
            self.__oc.wait_for_vm_completed(workload=workload)
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=workload)
            # verify that data upload to elastic search
            if self.__es_host:
                if self.__run_type == 'test_ci':
                    es_index = 'hammerdb-test-ci-results'
                else:
                    es_index = 'hammerdb-results'
                ids = self.__es_operations.verify_es_data_uploaded(index=es_index, uuid=self.__oc.get_long_uuid(workload=workload))
                # update metadata
                for id in ids:
                    self.__es_operations.update_es_index(index=es_index, id=id, metadata=self.get_metadata(kind='vm', database=database))
            self.__oc.delete_vm_sync(
                yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                vm_name=f'{workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name=f'{workload}-workload')
            raise VMNotCompletedTimeout(workload=workload)
        except Exception as err:
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
        if 'hammerdb' in workload_full_name:
            self.__template.generate_hammerdb_yamls(workload=f'{workload_name[0]}_{workload_name[1]}', database=workload_name[2])
            class_method = getattr(BenchmarkOperatorWorkloads, f'{workload_name[0]}_{workload_name[1]}')
            class_method(self, workload_name[2])
        else:
            self.__template.generate_workload_yamls(workload=workload_full_name)
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
        # make undeploy benchmark controller manager if exist
        self.make_undeploy_benchmark_controller_manager_if_exist(runner_path=environment_variables.environment_variables_dict['runner_path'])

        # make deploy benchmark controller manager
        self.make_deploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

        # run workload
        self.run_workload_func(workload_full_name=workload)

        # make undeploy benchmark controller manager
        self.make_undeploy_benchmark_controller_manager(runner_path=environment_variables.environment_variables_dict['runner_path'])

