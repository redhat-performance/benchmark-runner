
import glob
import json
import math
import os
import re
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_exceptions import MissingIOOperation
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class FioVM(WorkloadsOperations):
    """
    This class runs fio vm
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
        """Wait for fio_summary.json — the last file created by the runner script"""
        return 1

    def _upload_fio_result(self, result: dict):
        if self._enable_prometheus_snapshot:
            result.update(self._prometheus_result)
        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
        self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def _scp_and_parse_json_results(self, vm_name: str = '') -> list:
        vm_name = vm_name or self.__vm_name
        local_json_files = self._virtctl.scp_vm_files(
            vm_name=vm_name, remote_dir='/workload/', local_dir=self._run_artifacts_path,
            file_type='fio_summary.json', namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username)
        result_list = []
        workload_name = self._environment_variables_dict.get('workload', '').replace('_', '-')
        if not local_json_files:
            logger.warning(f'fio_summary.json not found on {vm_name}')
            return result_list
        summary_file = local_json_files[0]
        try:
            with open(summary_file, 'r') as f:
                summary = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f'Failed to parse FIO summary from {summary_file}: {e}')
            return result_list
        workload = self._get_workload_file_name(workload=self._get_run_artifacts_hierarchy(workload_name=workload_name, is_file=True))
        run_artifacts_url = os.path.join(self._run_artifacts_url, f'{workload}.tar.gz')
        for block_size, ops in summary.items():
            for io_operation, metrics in ops.items():
                result = {
                    'block_size': block_size,
                    'io_operation': io_operation,
                    'total_iops': metrics.get('TotalIOPS', 0),
                    'total_bw_kbs': metrics.get('TotalBW_KBs', 0),
                    'lat_avg_usec': metrics.get('LatAvg_usec', 0),
                    'lat_p99_usec': metrics.get('LatP99_usec', 0),
                    'vm_name': vm_name,
                    'run_artifacts_url': run_artifacts_url,
                }
                result_list.append(result)
        result_json_path = os.path.join(self._run_artifacts_path, f'{vm_name}.json')
        with open(result_json_path, 'w') as f:
            json.dump(result_list, f, indent=2)
        logger.info(f'FIO results saved to {result_json_path}')
        os.remove(summary_file)
        return result_list

    def save_error_logs(self):
        if self._es_host:
            self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._get_workload_file_name(self.__workload_name), is_file=True)}.tar.gz')
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed',
                                          result=self.__data_dict)
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    def __create_vm_scale(self, vm_num: str):
        try:
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))
            self._oc.wait_for_vm_create(vm_name=f'{self.__vm_name}-{vm_num}')
        except Exception as err:
            self.save_error_logs()
            raise err

    def __run_vm_scale(self, vm_num: str):
        try:
            self._oc.wait_for_ready(label=f'app=fio-{self._trunc_uuid}-{vm_num}', run_type='vm', label_uuid=False)
            scale_vm_name = f'{self.__vm_name}-{vm_num}'
            expected_count = self._get_expected_file_count()
            self.__status = self._virtctl.wait_for_vm_completed_by_file_count(
                vm_name=scale_vm_name, remote_dir='/workload/',
                expected_count=expected_count, file_type='fio_summary.json', namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username)
            self.__status = 'complete' if self.__status else 'failed'
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
            result_list = self._scp_and_parse_json_results(vm_name=scale_vm_name)
            if self._es_host:
                for result in result_list:
                    self._upload_fio_result(result)
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'),
                vm_name=scale_vm_name)
        except Exception as err:
            self.save_error_logs()
            raise err

    def __delete_vm_scale(self, vm_num: str):
        try:
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'))
        except Exception as err:
            self.save_error_logs()
            raise err

    @logger_time_stamp
    def run(self):
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()
            workload = self._workload.removesuffix('_ephemeral')
            self.__name = workload
            if self._run_type == 'test_ci':
                self.__es_index = 'fio-test-ci-results'
            else:
                self.__es_index = 'fio-results'
            self.__workload_name = workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'fio_configmap.yaml'))
            if not self._scale:
                self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
                self._oc.wait_for_ready(label=f'app=fio-{self._trunc_uuid}', run_type='vm', label_uuid=False)
                expected_count = self._get_expected_file_count()
                self.__status = self._virtctl.wait_for_vm_completed_by_file_count(
                vm_name=self.__vm_name, remote_dir='/workload/',
                expected_count=expected_count, file_type='fio_summary.json', namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username)
                self.__status = 'complete' if self.__status else 'failed'
                result_list = self._scp_and_parse_json_results()
                if self._enable_prometheus_snapshot:
                    self._prometheus_metrics_operation.finalize_prometheus()
                    metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                    self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
                if self._es_host:
                    for result in result_list:
                        self._upload_fio_result(result)
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    vm_name=self.__vm_name)
            else:
                self.__scale = int(self._scale)
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)), limit=self._threads_limit))
                for target in (self.__create_vm_scale, self.__run_vm_scale, self.__delete_vm_scale):
                    proc = []
                    for bulk in bulks:
                        for vm_num in bulk:
                            p = Process(target=target, args=(str(vm_num),))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
                        time.sleep(self._bulk_sleep_time)
                        proc = []
            self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            self.save_error_logs()
            raise err
