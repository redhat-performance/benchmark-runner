
import os
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class VdbenchVM(WorkloadsOperations):
    """
    This class runs vdbench vm
    """
    START_STAMP = '@@~@@START-WORKLOAD@@~@@'
    END_STAMP = '@@~@@END-WORKLOAD@@~@@'

    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__vm_name = ''
        self.__scale = ''
        self.__data_dict = {}

    def save_error_logs(self):
        """
        This method uploads logs into elastic and s3 bucket in case of error
        @return:
        """
        if self._es_host:
            self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._get_workload_file_name(self.__workload_name), is_file=True)}.tar.gz')
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed',
                                          result=self.__data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def __create_vm_scale(self, vm_num: str):
        """
        This method creates vm in parallel
        """
        try:
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))
            self._oc.wait_for_vm_create(vm_name=f'{self.__vm_name}-{vm_num}')
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def __run_vm_scale(self, vm_num: str):
        """
        This method runs vm in parallel
        """
        try:
            self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}-{vm_num}', run_type='vm', label_uuid=False)
            # Create vm log should be direct after vm is ready
            self.__vm_name = self._create_vm_log(labels=[f'{self.__workload_name}-{self._trunc_uuid}-{vm_num}'])
            self.__status = self._oc.wait_for_vm_log_completed(vm_name=self.__vm_name, end_stamp=self.END_STAMP)
            self.__status = 'complete' if self.__status else 'failed'
            # prometheus queries
            self._prometheus_metrics_operation.finalize_prometheus()
            metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
            prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
            # save run artifacts logs
            result_list = self._create_vm_run_artifacts(vm_name=f'{self.__workload_name}-{self._trunc_uuid}-{vm_num}', start_stamp=self.START_STAMP, end_stamp=self.END_STAMP, log_type='.csv')
            if self._es_host:
                # upload several run results
                for result in result_list:
                    result.update(prometheus_result)
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'),
                vm_name=f'{self.__vm_name}-{vm_num}')
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def __delete_vm_scale(self, vm_num: str):
        """
        This method deletes vm in parallel
        """
        try:
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self._prometheus_metrics_operation.init_prometheus()
            self.__name = self._workload
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            # create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
            if not self._scale:
                self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
                self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', run_type='vm', label_uuid=False)
                # Create vm log should be direct after vm is ready
                self.__vm_name = self._create_vm_log(labels=[self.__workload_name])
                self.__status = self._oc.wait_for_vm_log_completed(vm_name=self.__vm_name, end_stamp=self.END_STAMP)
                self.__status = 'complete' if self.__status else 'failed'
                # save run artifacts logs
                result_list = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.START_STAMP, end_stamp=self.END_STAMP, log_type='.csv')
                # prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
                if self._es_host:
                    # upload several run results
                    for result in result_list:
                        result.update(prometheus_result)
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                    # verify that data upload to elastic search according to unique uuid
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    vm_name=self.__vm_name)
            # scale
            else:
                self.__scale = int(self._scale)
                # create redis and state signals
                sync_pods = {'redis': 'redis', 'state_signals_exporter_pod': 'state-signals-exporter'}
                for pod, name in sync_pods.items():
                    if pod == 'redis':
                        pod_name = f'redis-master'
                    else:
                        pod_name = name
                    self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{pod}.yaml'), pod_name=pod_name)
                    self._oc.wait_for_initialized(label=f'app={name}', label_uuid=False)
                    self._oc.wait_for_ready(label=f'app={name}', label_uuid=False)
                # prepare scale run
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)), limit=self._threads_limit))
                # create, run and delete vms
                for target in (self.__create_vm_scale, self.__run_vm_scale, self.__delete_vm_scale):
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
                self._create_scale_logs()
                # delete redis and state signals
                for pod, name in sync_pods.items():
                    if pod == 'redis':
                        pod_name = f'redis-master'
                    else:
                        pod_name = name
                    self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{pod}.yaml'), pod_name=pod_name)
            # delete namespace
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err
