
import glob
import math
import os
import re
import time
from csv import DictReader
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_exceptions import MissingIOOperation
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
        self.__namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self.__username = self._environment_variables_dict.get('vm_user') or 'cloud-user'

    def _get_expected_file_count(self) -> int:
        """Parse IO_OPERATION from the rendered YAML and return the number of comma-separated items."""
        yaml_path = os.path.join(self._run_artifacts_path, f'{self.__name}.yaml')
        if not os.path.exists(yaml_path):
            candidates = sorted(glob.glob(os.path.join(self._run_artifacts_path, f'{self.__name}_*.yaml')))
            if candidates:
                yaml_path = candidates[0]
        with open(yaml_path, 'r') as f:
            for line in f:
                match = re.search(r'export IO_OPERATION=(.+)', line.strip())
                if match:
                    io_operation = match.group(1).strip()
                    return max(len(io_operation.split(',')), 1)
        raise MissingIOOperation(yaml_path=yaml_path)

    def _upload_vdbench_result(self, result: dict):
        """Upload a single vdbench CSV result to Elasticsearch."""
        if self._enable_prometheus_snapshot:
            result.update(self._prometheus_result)
        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
        self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def _scp_and_parse_csv_results(self, vm_name: str = '') -> list:
        """SCP CSV result files from the VM to local run artifacts path and parse them into dicts for ES upload."""
        vm_name = vm_name or self.__vm_name
        local_csv_files = self._virtctl.scp_vm_files(
            vm_name=vm_name, remote_dir='/workload/', local_dir=self._run_artifacts_path,
            namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username)
        result_list = []
        workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
        for csv_file in local_csv_files:
            with open(csv_file, 'r') as f:
                for line_dict in DictReader(f):
                    for key, value in line_dict.items():
                        try:
                            num = float(value)
                            line_dict[key] = 0.0 if math.isnan(num) or math.isinf(num) else round(num, 3)
                        except (ValueError, TypeError):
                            if value == 'n/a':
                                line_dict[key] = 0.0
                    if line_dict.get('Run', '').startswith('format_for_'):
                        continue
                    line_dict['vm_name'] = vm_name
                    workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
                    line_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')
                    result_list.append(dict(line_dict))
        return result_list

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
            scale_vm_name = f'{self.__vm_name}-{vm_num}'
            expected_count = self._get_expected_file_count()
            self.__status = self._virtctl.wait_for_vm_completed_by_file_count(
                vm_name=scale_vm_name, remote_dir='/workload/',
                expected_count=expected_count, namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username)
            self.__status = 'complete' if self.__status else 'failed'
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
            result_list = self._scp_and_parse_csv_results(vm_name=scale_vm_name)
            if self._es_host:
                for result in result_list:
                    self._upload_vdbench_result(result)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'),
                vm_name=scale_vm_name)
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
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()
            workload = self._workload.removesuffix('_ephemeral')
            self.__name = workload
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'
            self.__workload_name = workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            # create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
            if not self._scale:
                self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
                self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', run_type='vm', label_uuid=False)
                expected_count = self._get_expected_file_count()
                self.__status = self._virtctl.wait_for_vm_completed_by_file_count(
                vm_name=self.__vm_name, remote_dir='/workload/',
                expected_count=expected_count, namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username)
                self.__status = 'complete' if self.__status else 'failed'
                result_list = self._scp_and_parse_csv_results()
                if self._enable_prometheus_snapshot:
                    self._prometheus_metrics_operation.finalize_prometheus()
                    metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                    self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
                if self._es_host:
                    for result in result_list:
                        self._upload_vdbench_result(result)
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
