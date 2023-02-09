
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations
from benchmark_runner.common.oc.oc import VMStatus
from benchmark_runner.common.prometheus.prometheus_metrics_operations import PrometheusMetricsOperation


class BootstormVM(WorkloadsOperations):
    """
    This class run bootstorm vm
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__vm_name = ''
        self.__data_dict = {}
        self.__bootstorm_start_time = {}
        self.__prometheus_metrics_operation = PrometheusMetricsOperation()

    @logger_time_stamp
    def __set_bootstorm_vm_start_time(self, vm_name: str = ''):
        """
        This method captures boot start time for specified VM
        @return:
        """
        self.__bootstorm_start_time[vm_name] = time.time()

    @logger_time_stamp
    def __get_bootstorm_vm_elapse_time(self, vm_name: str):
        """
        This method returns boot elapse time for specified VM in milliseconds
        @return: Dictionary with vm_name, node and its boot elapse time
        """
        vm_bootstorm_time = {}

        self._virtctl.expose_vm(vm_name=vm_name)
        # wait till vm login
        vm_node = self._oc.get_vm_node(vm_name=vm_name)
        node_ip = self._oc.get_nodes_addresses()[vm_node]
        vm_node_port = self._oc.get_exposed_vm_port(vm_name=vm_name)
        if self._oc.wait_for_vm_login(vm_name=vm_name, node_ip=node_ip, vm_node_port=vm_node_port):
            vm_bootstorm_time['vm_name'] = vm_name
            vm_bootstorm_time['node'] = vm_node
            delta = time.time() - self.__bootstorm_start_time[vm_name]
            vm_bootstorm_time['bootstorm_time'] = round(delta, 3) * self.MILLISECONDS
        return vm_bootstorm_time

    def __create_vm_scale(self, vm_num: str):
        """
        This method creates VMs in parallel
        """
        self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))
        self._oc.wait_for_vm_status(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}', status=VMStatus.Stopped)

    def __run_vm_scale(self, vm_num: str):
        """
        This method start VMs in parallel and wait for login to be enabled
        """
        vm_name = f'bootstorm-vm-{self._trunc_uuid}-{vm_num}'
        self.__set_bootstorm_vm_start_time(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}')
        self._virtctl.start_vm_async(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}')
        self._virtctl.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Running)
        self.__data_dict = self.__get_bootstorm_vm_elapse_time(vm_name=vm_name)
        self.__status = 'complete' if self.__data_dict else 'failed'
        self.__prometheus_metrics_operation.finalize_prometheus()
        metric_results = self.__prometheus_metrics_operation.run_prometheus_queries()
        prometheus_result = self.parse_prometheus_metrics(data=metric_results)
        self.__data_dict.update(prometheus_result)
        # upload to elasticsearch
        if self._es_host:
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status,
                                          result=self.__data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def __stop_vm_scale(self, vm_num: str):
        """
        This method stops VMs async in parallel
        """
        self._virtctl.stop_vm_async(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}')

    def __wait_for_stop_vm_scale(self, vm_num: str):
        """
        This method waits for VMs stop in parallel
        """
        self._virtctl.wait_for_vm_status(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}')

    def __delete_vm_scale(self, vm_num: str):
        """
        This method deletes VMs async in parallel
        """
        self._oc.delete_async(
            yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))

    def __wait_for_delete_vm_scale(self, vm_num: str):
        """
        This method waits for VMs delete in parallel
        """
        self._oc.wait_for_vm_delete(vm_name=f'bootstorm-vm-{self._trunc_uuid}-{vm_num}')

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self.__prometheus_metrics_operation.init_prometheus()
            self.__name = self._workload
            if self._run_type == 'test_ci':
                self.__es_index = 'bootstorm-test-ci-results'
            else:
                self.__es_index = 'bootstorm-results'
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            if not self._scale:
                self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'))
                self._oc.wait_for_vm_status(vm_name=f'bootstorm-vm-{self._trunc_uuid}', status=VMStatus.Stopped)
                self.__set_bootstorm_vm_start_time(vm_name=self.__vm_name)
                self._virtctl.start_vm_sync(vm_name=self.__vm_name)
                self.__data_dict = self.__get_bootstorm_vm_elapse_time(vm_name=self.__vm_name)
                self.__status = 'complete' if self.__data_dict else 'failed'
                self.__prometheus_metrics_operation.finalize_prometheus()
                metric_results = self.__prometheus_metrics_operation.run_prometheus_queries()
                prometheus_result = self.parse_prometheus_metrics(data=metric_results)
                self.__data_dict.update(prometheus_result)
                if self._es_host:
                    # upload several run results
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=self.__data_dict)
                    # verify that data upload to elastic search according to unique uuid
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    vm_name=self.__vm_name)
            # scale
            else:
                # create namespace
                self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
                # create run bulks
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)), limit=self._threads_limit))
                # create, run and delete vms
                for target in (self.__create_vm_scale, self.__run_vm_scale, self.__stop_vm_scale, self.__wait_for_stop_vm_scale, self.__delete_vm_scale, self.__wait_for_delete_vm_scale):
                    proc = []
                    for bulk in bulks:
                        for vm_num in bulk:
                            p = Process(target=target, args=(str(vm_num),))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
                        # sleep between bulks
                        time.sleep(self._bulk_sleep_time)
                        proc = []
                # delete namespace
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._es_host:
                self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=self.__data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            raise err
