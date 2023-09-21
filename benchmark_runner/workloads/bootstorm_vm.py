
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations
from benchmark_runner.common.oc.oc import VMStatus


class BootstormVM(WorkloadsOperations):
    """
    This class runs bootstorm vm
    """
    def __init__(self):
        super().__init__()
        self._name = ''
        self._workload_name = ''
        self._es_index = ''
        self._kind = ''
        self._status = ''
        self._vm_name = ''
        self._data_dict = {}
        self._bootstorm_start_time = {}

    @logger_time_stamp
    def _set_bootstorm_vm_start_time(self, vm_name: str = ''):
        """
        This method captures boot start time for specified VM
        @return:
        """
        self._bootstorm_start_time[vm_name] = time.time()

    @logger_time_stamp
    def _get_bootstorm_vm_elapsed_time(self, vm_name: str):
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
            delta = time.time() - self._bootstorm_start_time[vm_name]
            vm_bootstorm_time['bootstorm_time'] = round(delta, 3) * self.MILLISECONDS
        return vm_bootstorm_time

    def _create_vm_scale(self, vm_num: str):
        """
        This method creates VMs in parallel
        """
        self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}_{vm_num}.yaml'))
        self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}', status=VMStatus.Stopped)

    def _run_vm(self):
        """
        This method runs one VM, upload results to Elasticsearch, and destroys VM synchronously
        @return:
        """
        self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'))
        self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}', status=VMStatus.Stopped)
        self._set_bootstorm_vm_start_time(vm_name=self._vm_name)
        self._virtctl.start_vm_sync(vm_name=self._vm_name)
        self._data_dict = self._get_bootstorm_vm_elapsed_time(vm_name=self._vm_name)
        self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                            f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
        self._status = 'complete' if self._data_dict else 'failed'
        # prometheus queries
        self._prometheus_metrics_operation.finalize_prometheus()
        metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
        prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
        self._data_dict.update(prometheus_result)
        if self._es_host:
            # upload several run results
            self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status=self._status,
                                          result=self._data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)
        self._oc.delete_vm_sync(
            yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
            vm_name=self._vm_name)

    def _run_vm_scale(self, vm_num: str):
        """
        This method runs VMs in parallel and wait for login to be enabled
        """
        vm_name = f'{self._workload_name}-{self._trunc_uuid}-{vm_num}'
        self._set_bootstorm_vm_start_time(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
        self._virtctl.start_vm_async(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
        self._virtctl.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Running)
        self._data_dict = self._get_bootstorm_vm_elapsed_time(vm_name=vm_name)
        self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-scale-{self._time_stamp_format}.tar.gz')
        self._status = 'complete' if self._data_dict else 'failed'
        # prometheus queries
        self._prometheus_metrics_operation.finalize_prometheus()
        metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
        prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
        self._data_dict.update(prometheus_result)
        # upload to elasticsearch
        if self._es_host:
            self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status=self._status,
                                          result=self._data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    def _stop_vm_scale(self, vm_num: str):
        """
        This method stops VMs async in parallel
        """
        self._virtctl.stop_vm_async(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')

    def _wait_for_stop_vm_scale(self, vm_num: str):
        """
        This method waits for VMs stop in parallel
        """
        self._virtctl.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')

    def _delete_vm_scale(self, vm_num: str):
        """
        This method deletes VMs async in parallel
        """
        self._oc.delete_async(
            yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}_{vm_num}.yaml'))

    def _wait_for_delete_vm_scale(self, vm_num: str):
        """
        This method waits for VMs delete in parallel
        """
        self._oc.wait_for_vm_delete(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')

    def _initialize_run(self):
        """
        Initialize prometheus start time, vm name, kind and create benchmark-runner namespace for bootstorm vms
        """
        self._prometheus_metrics_operation.init_prometheus()
        self._name = self._workload
        self._workload_name = self._workload.replace('_', '-')
        self._vm_name = f'{self._workload_name}-{self._trunc_uuid}'
        self._kind = 'vm'
        self._environment_variables_dict['kind'] = 'vm'
        # create namespace
        self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self._initialize_run()
            if self._run_type == 'test_ci':
                self._es_index = 'bootstorm-test-ci-results'
            else:
                self._es_index = 'bootstorm-results'
            if not self._scale:
                self._run_vm()
            # scale
            else:
                # create run bulks
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)), limit=self._threads_limit))
                # create, run and delete vms
                for target in (self._create_vm_scale, self._run_vm_scale, self._stop_vm_scale, self._wait_for_stop_vm_scale, self._delete_vm_scale, self._wait_for_delete_vm_scale):
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
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
                vm_name=self._vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._es_host:
                self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status='failed', result=self._data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)
            raise err
