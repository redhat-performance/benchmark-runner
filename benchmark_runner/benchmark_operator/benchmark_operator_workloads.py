
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.oc.oc_exceptions import VMNotCompletedTimeout
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.benchmark_operator.benchmark_operator_workloads_operations import BenchmarkOperatorWorkloadsOperations


class BenchmarkOperatorWorkloads(BenchmarkOperatorWorkloadsOperations):
    """
    This class contains all the custom_workloads
    """
    def __init__(self):
        super().__init__()
        self.__workload = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''

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
            self.__workload = name.replace('_', '-')
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'), pod_name=f'{self.__workload}-workload')
            self._oc.wait_for_initialized(label='app=stressng_workload', workload=self.__workload)
            self._oc.wait_for_ready(label='app=stressng_workload', workload=self.__workload)
            self.__status = self._oc.wait_for_pod_completed(label='app=stressng_workload', workload=self.__workload)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload)
            if self._es_host:
                # verify that data upload to elastic search according to unique uuid
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'),
                pod_name=f'{self.__workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{self.__workload}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_pod.__name__}.yaml'),
                                           pod_name=f'{self.__workload}-workload')
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
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'
            self.__workload = self.stressng_vm.__name__.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_vm.__name__}.yaml'), vm_name=f'{self.__workload}-workload')
            self._oc.wait_for_initialized(label='app=stressng_workload', workload=self.__workload)
            self._oc.wait_for_ready(label='app=stressng_workload', workload=self.__workload)
            # Create vm log should be direct after vm is ready
            vm_name = self._create_vm_log(labels=[self.__workload])
            self.__status = self._oc.wait_for_vm_completed(workload=self.__workload, vm_name=vm_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, pod=False)
            # verify that data upload to elastic search
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self._environment_variables_dict.get('kind', ''), status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_vm.__name__}.yaml'),
                vm_name=f'{self.__workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name=f'{self.__workload}-workload')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, pod=False)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self._environment_variables_dict.get('kind', ''), status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.stressng_vm.__name__}.yaml'),
                                          vm_name=f'{self.__workload}-workload')
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
            self.__workload = name.replace('_', '-')
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-server')
            # uperf server
            server_name = self._environment_variables_dict.get('pin_node1', '')
            if server_name:
                # uperf server name is limited up to 27 chars
                if len(server_name) > 27:
                    server_name = server_name[:28]
                label = f'app=uperf-bench-server-{server_name}-0'
                self._oc.wait_for_initialized(label=label, workload=self.__workload)
                self._oc.wait_for_ready(label=label, workload=self.__workload)
            # in case that no pin node
            else:
                label = f'benchmark-operator-workload=uperf'
                self._oc.wait_for_initialized(label=label, workload=self.__workload, label_uuid=False)
                self._oc.wait_for_ready(label=label, workload=self.__workload, label_uuid=False)
            # uperf client
            self._oc.wait_for_pod_create(pod_name='uperf-client')
            self._oc.wait_for_initialized(label='app=uperf-bench-client', workload=self.__workload)
            self._oc.wait_for_ready(label='app=uperf-bench-client', workload=self.__workload)
            self.__status = self._oc.wait_for_pod_completed(label='app=uperf-bench-client', workload=self.__workload)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, labels=['uperf-client', 'uperf-server'])
            if self._es_host:
                # verify that data upload to elastic search
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'),
                pod_name=f'uperf-client')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, labels=['uperf-client', 'uperf-server'])
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_pod.__name__}.yaml'), pod_name=f'uperf-client')
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
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'
            self.__workload = self.uperf_vm.__name__.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            # uperf server
            self._oc.wait_for_vm_create(vm_name='uperf-server')
            self._oc.wait_for_initialized(label='app=uperf-bench-server-0', workload=self.__workload)
            self._oc.wait_for_ready(label='app=uperf-bench-server-0', workload=self.__workload)
            # client server
            self._oc.wait_for_vm_create(vm_name='uperf-client')
            self._oc.wait_for_initialized(label='app=uperf-bench-client', workload=self.__workload)
            self._oc.wait_for_ready(label='app=uperf-bench-client', workload=self.__workload)
            # Create vm log should be direct after vm is ready
            vm_name = self._create_vm_log(labels=['uperf-server', 'uperf-client'])
            self.__status = self._oc.wait_for_vm_completed(workload=self.__workload, vm_name=vm_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, pod=False)
            # verify that data upload to elastic search
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self._environment_variables_dict.get('kind', ''), status=self.__status, run_artifacts_url=run_artifacts_url)
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_vm.__name__}.yaml'),
                                     vm_name='uperf-server')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
            raise err
        except Exception as err:
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, pod=False)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self._environment_variables_dict.get('kind', ''), status='failed', run_artifacts_url=run_artifacts_url)
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.uperf_vm.__name__}.yaml'), vm_name='uperf-server')
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
            self.__workload = name.replace('_', '-')
            self.__kind = 'pod'
            if '_kata' in name:
                self.__kind = 'kata'
            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'
            environment_variables.environment_variables_dict['kind'] = self.__kind
            # database
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'), pod_name=database, namespace=f'{database}-db')
            self._oc.wait_for_initialized(label=f'app={database}', workload=database, namespace=f'{database}-db', label_uuid=False)
            self._oc.wait_for_ready(label=f'app={database}', workload=database, namespace=f'{database}-db', label_uuid=False)
            # hammerdb
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'), pod_name=f'{self.__workload}-creator')
            # hammerdb creator
            self._oc.wait_for_pod_create(pod_name=f'{self.__workload}-creator')
            self._oc.wait_for_initialized(label='app=hammerdb_creator', workload=self.__workload)
            self._oc.wait_for_ready(label='app=hammerdb_creator', workload=self.__workload)
            self._oc.wait_for_pod_completed(label='app=hammerdb_creator', workload=self.__workload)
            # hammerdb workload
            self._oc.wait_for_pod_create(pod_name=f'{self.__workload}-workload')
            self._oc.wait_for_initialized(label='app=hammerdb_workload', workload=self.__workload)
            self._oc.wait_for_ready(label='app=hammerdb_workload', workload=self.__workload)
            self.__status = self._oc.wait_for_pod_completed(label='app=hammerdb_workload', workload=self.__workload)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[f'{self.__workload}-creator', f'{self.__workload}-workload'], database=database)
            if self._es_host:
                # verify that data upload to elastic search
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self.__kind, database=database, status=self.__status, run_artifacts_url=run_artifacts_url)
            # delete hammerdb
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                pod_name=f'{self.__workload}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'),
                                      pod_name=database,
                                      namespace=f'{database}-db')
        except ElasticSearchDataNotUploaded as err:
            # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{self.__workload}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'), pod_name=database,
                                      namespace=f'{database}-db')
            raise err
        except Exception as err:
            # save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[f'{self.__workload}-creator', f'{self.__workload}-workload'], database=database)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', run_artifacts_url=run_artifacts_url, database=database)
        # delete hammerdb
            self.tear_down_pod_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_pod.__name__}_{database}.yaml'),
                                           pod_name=f'{self.__workload}-creator')
            # delete database
            self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{database}.yaml'), pod_name=database,
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
            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'
            self.__workload = self.hammerdb_vm.__name__.replace('_', '-')
            environment_variables.environment_variables_dict['kind'] = 'vm'
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'), vm_name=f'{self.__workload}-workload')
            # hammerdb workload and database
            self._oc.wait_for_vm_create(vm_name=f'{self.__workload}-workload')
            self._oc.wait_for_initialized(label='app=hammerdb_workload', workload=self.__workload)
            self._oc.wait_for_ready(label='app=hammerdb_workload', workload=self.__workload)
            # Create vm log should be direct after vm is ready
            vm_name = self._create_vm_log(labels=[self.__workload])
            self.__status = self._oc.wait_for_vm_completed(workload=self.__workload, vm_name=vm_name)
            self.__status = 'complete' if self.__status else 'failed'
            # system metrics
            if environment_variables.environment_variables_dict['system_metrics'] == 'True':
                self.system_metrics_collector(workload=self.__workload)
            # save run artifacts logs of benchmark-controller-manager and system-metrics
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, pod=False)
            # verify that data upload to elastic search
            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._oc.get_long_uuid(workload=self.__workload))
                # update metadata
                for id in ids:
                    self._update_elasticsearch_index(index=self.__es_index, id=id, kind=self._environment_variables_dict.get('kind', ''), status=self.__status, run_artifacts_url=run_artifacts_url, database=database)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                vm_name=f'{self.__workload}-workload')
        except ElasticSearchDataNotUploaded as err:
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name=f'{self.__workload}-workload')
            raise VMNotCompletedTimeout(workload=self.__workload)
        except Exception as err:
            run_artifacts_url = self._create_run_artifacts(workload=self.__workload, pod=False)
            self._upload_to_elasticsearch(index=self.__es_index, kind=self._environment_variables_dict.get('kind', ''), status='failed', run_artifacts_url=run_artifacts_url, database=database)
            # delete hammerdb
            self.tear_down_vm_after_error(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.hammerdb_vm.__name__}_{database}.yaml'),
                                          vm_name=f'{self.__workload}-workload')
            raise err

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """
        self.initialize_workload()
        workload_name = self._workload.split('_')
        benchmark_operator_workloads = BenchmarkOperatorWorkloads()
        if 'hammerdb' in self._workload:
            class_method = getattr(benchmark_operator_workloads, f'{workload_name[0]}_{workload_name[1]}')
            class_method(database=workload_name[2])
        else:
            class_method = getattr(benchmark_operator_workloads, self._workload)
            class_method()
        self.finalize_workload()
