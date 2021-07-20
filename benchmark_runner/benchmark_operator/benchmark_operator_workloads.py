
import os
import time

from typeguard import typechecked
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.oc.oc import OC
from benchmark_runner.benchmark_operator.templates.generate_yaml_from_templates import TemplateOperations
from benchmark_runner.common.elasticsearch.es_operations import ESOperations
from benchmark_runner.common.ssh.ssh import SSH
from benchmark_runner.benchmark_operator.benchmark_operator_exceptions import VMWorkloadNeedElasticSearch


class BenchmarkOperatorWorkloads:
    """
    This class contains all the custom_workloads
    """
    def __init__(self, kubeadmin_password: str = '', es_host: str = '', es_port: str = '', workload: str = ''):
        self.__ssh = SSH()
        self.__kubeadmin_password = kubeadmin_password
        self.__oc = OC(kubeadmin_password=self.__kubeadmin_password)
        self.__dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__workload = workload
        self.__es_host = es_host
        self.__es_port = es_port
        self.__current_run_path = os.path.join(self.__dir_path, 'current_run')
        if es_host and es_port:
            self.__es_operations = ESOperations(es_host=self.__es_host, es_port=self.__es_port)
        else:
            self.__verify_elasticsearch_exist_for_vm_workload(workload=self.__workload)
        # Generate templates class
        self.__template = TemplateOperations()
        self.__oc.login()

    @typechecked()
    def __verify_elasticsearch_exist_for_vm_workload(self, workload: str):
        """
        This method verify that elastic search exist for vm workloads to verify completed status
        :return: error in case no elasticsearch
        """
        if 'vm' in workload and not self.__es_host:
            raise VMWorkloadNeedElasticSearch

    def __get_run_yamls(self, extension='.yaml'):
        """
        This method get all run yamls files
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

    def __delete_run_yamls(self, extension: str = '.yaml'):
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

    @logger_time_stamp
    def delete_benchmark_operator_if_exist(self):
        """
        This method delete benchmark operator if exist
        """
        # delete benchmark-operator pod if exist
        if self.__oc._is_pod_exist(pod_name='benchmark-operator', namespace='my-ripsaw'):
            self.helm_delete_benchmark_operator()

    @typechecked()
    @logger_time_stamp
    def helm_install_benchmark_operator(self, install_path: str = ''):
        """
        This function install benchmark operator
        :return:
        """
        benchmark_operator_path = 'benchmark-operator/charts/benchmark-operator'
        current_dir = os.getcwd()
        if install_path:
            os.chdir(os.path.join(install_path, benchmark_operator_path))
        else:
            os.chdir(os.path.join('/', benchmark_operator_path))
        self.__ssh.run('/usr/local/bin/helm install benchmark-operator . -n my-ripsaw --create-namespace')
        self.__oc.wait_for_pod_create(pod_name='benchmark-operator')
        self.__ssh.run('~/./oc adm policy -n my-ripsaw add-scc-to-user privileged -z benchmark-operator')
        os.chdir(current_dir)

    @logger_time_stamp
    def helm_delete_benchmark_operator(self):
        """
        This function delete benchmark operator
        :return:
        """
        self.__ssh.run('/usr/local/bin/helm delete benchmark-operator -n my-ripsaw')
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
        self.__delete_run_yamls()
        self.helm_delete_benchmark_operator()

    @logger_time_stamp
    def tear_down_vm_after_error(self, yaml: str, pod_name: str):
        """
        This method tear down vm in case of error
        """
        self.__oc.delete_vm_sync(yaml=yaml, vm_name=pod_name)
        self.__delete_run_yamls()
        self.helm_delete_benchmark_operator()

    @logger_time_stamp
    def stressng_pod(self):
        """
        This method run stressng workload
        :return:
        """
        try:
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'), pod_name='stressng-workload')
            self.__oc.wait_for_initialized(label='app=stressng_workload')
            self.__oc.wait_for_ready(label='app=stressng_workload')
            self.__oc.wait_for_completed(label='app=stressng_workload')
            if self.__es_host:
                # verify that data upload to elastic search according to uniq uuid
                self.__es_operations.verify_es_data_uploaded(index='ripsaw-stressng-results', uuid=self.__oc.get_long_uuid())
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name='stressng-workload')
            raise err
        except Exception as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name='stressng-workload')
            raise err
        self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_pod.__name__}.yaml'),
                                  pod_name='stressng-workload')

    @logger_time_stamp
    def stressng_vm(self):
        """
        This method run stressng vm workload
        :return:
        """
        try:
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'), vm_name='stressng-vm-benchmark-workload')
            # stressng workload and database
            self.__oc.wait_for_vm_create(vm_name='stressng-vm-benchmark-workload')
            self.__oc.wait_for_initialized(label='kubevirt.io=virt-launcher')
            self.__oc.wait_for_ready(label='kubevirt.io=virt-launcher')
            # verify that data upload to elastic search, vm completed status
            self.__es_operations.verify_es_data_uploaded(index='ripsaw-stressng-results', uuid=self.__oc.get_long_uuid())
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name='stressng-vm-benchmark-workload')
            raise err
        except Exception as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name='stressng-vm-benchmark-workload')
            raise err
        self.__oc.delete_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.stressng_vm.__name__}.yaml'),
                                 vm_name='stressng-vm-benchmark-workload')

    @logger_time_stamp
    def uperf_pod(self):
        """
        This method run uperf workload
        :return:
        """
        try:
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name='uperf-server')
            # uperf server
            self.__oc.wait_for_initialized(label='app=uperf-bench-server-perf-sm5039-5-6.perf.lab.en-0')
            self.__oc.wait_for_ready(label='app=uperf-bench-server-perf-sm5039-5-6.perf.lab.en-0')
            # uperf client
            self.__oc.wait_for_pod_create(pod_name='uperf-client')
            self.__oc.wait_for_initialized(label='app=uperf-bench-client')
            self.__oc.wait_for_ready(label='app=uperf-bench-client')
            self.__oc.wait_for_completed(label='app=uperf-bench-client')
            if self.__es_host:
                # verify that data upload to elastic search
                self.__es_operations.verify_es_data_uploaded(index='ripsaw-uperf-results', uuid=self.__oc.get_long_uuid(), workload=self.uperf_pod.__name__)
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name='uperf-client')
            raise err
        except Exception as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name='uperf-client')
            raise err
        self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_pod.__name__}.yaml'),
                                  pod_name='uperf-client')

    @logger_time_stamp
    def uperf_vm(self):
        """
        This method run uperf vm workload
        :return:
        """
        try:
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            # uperf server
            self.__oc.wait_for_vm_create(vm_name='uperf-server')
            self.__oc.wait_for_initialized(label='app=uperf-bench-server-0')
            self.__oc.wait_for_ready(label='app=uperf-bench-server-0')
            # client server
            self.__oc.wait_for_vm_create(vm_name='uperf-client')
            self.__oc.wait_for_initialized(label='app=uperf-bench-client')
            self.__oc.wait_for_ready(label='app=uperf-bench-client')
            # verify that data upload to elastic search, vm completed status
            self.__es_operations.verify_es_data_uploaded(index='ripsaw-uperf-results', uuid=self.__oc.get_long_uuid(), workload=self.uperf_vm.__name__)
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err
        except Exception as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err
        self.__oc.delete_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.uperf_vm.__name__}.yaml'),
                                 vm_name='uperf-server')

    @typechecked
    @logger_time_stamp
    def hammerdb_pod(self, database: str):
        """
        This method run hammerdb pod workload
        :return:
        """
        try:
            # database
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database, namespace=f'{database}-db')
            self.__oc.wait_for_initialized(label=f'app={database}', namespace=f'{database}-db')
            self.__oc.wait_for_ready(label=f'app={database}', namespace=f'{database}-db')
            # hammerdb
            self.__oc.create_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'), pod_name='hammerdb-benchmark-creator')
            # hammerdb creator
            self.__oc.wait_for_pod_create(pod_name='hammerdb-benchmark-creator')
            self.__oc.wait_for_initialized(label='app=hammerdb_creator')
            self.__oc.wait_for_ready(label='app=hammerdb_creator')
            self.__oc.wait_for_completed(label='app=hammerdb_creator')
            # hammerdb workload
            self.__oc.wait_for_pod_create(pod_name='hammerdb-benchmark-workload')
            self.__oc.wait_for_initialized(label='app=hammerdb_workload')
            self.__oc.wait_for_ready(label='app=hammerdb_workload')
            self.__oc.wait_for_completed(label='app=hammerdb_workload')
            if self.__es_host:
                # verify that data upload to elastic search
                self.__es_operations.verify_es_data_uploaded(index='ripsaw-hammer-results', uuid=self.__oc.get_long_uuid())
        except ElasticSearchDataNotUploaded as err:
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name='hammerdb-benchmark-creator')
            # delete database
            self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database,
                                      namespace=f'{database}-db')
            raise err
        except Exception as err:
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name='hammerdb-benchmark-creator')
            # delete database
            self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database,
                                      namespace=f'{database}-db')
            raise err
        # delete hammerdb
        self.__oc.delete_pod_sync(
            yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
            pod_name='hammerdb-benchmark-creator')
        # delete database
        self.__oc.delete_pod_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{database}.yaml'), pod_name=database,
                                  namespace=f'{database}-db')

    @typechecked
    @logger_time_stamp
    def hammerdb_vm(self, database: str):
        """
        This method run hammerdb vm workload
        :return:
        """
        try:
            self.__oc.create_vm_sync(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'), vm_name='hammerdb-vm-benchmark-workload')
            # hammerdb workload and database
            self.__oc.wait_for_vm_create(vm_name='hammerdb-vm-benchmark-workload')
            self.__oc.wait_for_initialized(label='app=hammerdb_workload')
            self.__oc.wait_for_ready(label='app=hammerdb_workload')
            # verify that data upload to elastic search, vm completed status
            self.__es_operations.verify_es_data_uploaded(index='ripsaw-hammer-results', uuid=self.__oc.get_long_uuid())
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name='hammerdb-vm-benchmark-workload')
            raise err
        except Exception as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name='hammerdb-vm-benchmark-workload')
            raise err
        self.__oc.delete_vm_sync(
            yaml=os.path.join(f'{self.__current_run_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
            vm_name='hammerdb-vm-benchmark-workload')

    @typechecked
    @logger_time_stamp
    def run_workload_func(self, workload_full_name: str):
        """
        The method run specific workload function according to the workload string
        :param workload_full_name:
        :return:
        """
        # remove running workloads if exist
        self.__delete_run_yamls()
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
    def run_workload(self):
        """
        This method run the input workload
        :return:
        """

        self.delete_benchmark_operator_if_exist()

        # elasticsearch is must for VM workload for completed status verifications
        self.__verify_elasticsearch_exist_for_vm_workload(workload=self.__workload)

        # install benchmark operator
        self.helm_install_benchmark_operator()

        # run workload
        self.run_workload_func(workload_full_name=self.__workload)

        # delete benchmark operator
        self.helm_delete_benchmark_operator()


