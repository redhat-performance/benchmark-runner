
import os
import time

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class HammerdbVm(WorkloadsOperations):
    """
    This class runs HammerDB VM workload with scale support.
    Same code path for 1 VM and N VMs.
    The VM cloud-init runs the full benchmark (DB setup + HammerDB + parse_results.py).
    Results are retrieved by copying /tmp/hammerdb-results.json from the running VM.
    """
    HAMMERDB_RESULTS_FILE = '/tmp/hammerdb-results.json'

    def __init__(self):
        super().__init__()
        self._name = ''
        self._workload_name = ''
        self._database = ''
        self._es_index = ''
        self._kind = ''
        self._namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self._username = self._environment_variables_dict.get('vm_user') or 'cloud-user'
        self._ssh_key_path = ''
        self._vm_nodes = {}

    def _get_vm_name(self, vm_num: str) -> str:
        if self._scale:
            return f'{self._workload_name}-{self._trunc_uuid}-{vm_num}'
        return f'{self._workload_name}-{self._trunc_uuid}'

    def _get_vm_yaml(self, vm_num: str) -> str:
        if self._scale:
            return os.path.join(self._run_artifacts_path, f'{self._name}_{vm_num}.yaml')
        return os.path.join(self._run_artifacts_path, f'{self._name}.yaml')

    def _create_vm(self, vm_num: str):
        """Phase 1: Create VM and wait for ready."""
        try:
            vm_name = self._get_vm_name(vm_num)
            self._oc.create_async(yaml=self._get_vm_yaml(vm_num))
            self._oc.wait_for_ready(label=f'app={vm_name}', run_type='vm', label_uuid=False)
        except Exception as err:
            self._save_error_logs()
            raise err

    def _wait_and_collect(self, vm_num: str):
        """Phase 2: Wait for workload completion and SCP results."""
        try:
            vm_name = self._get_vm_name(vm_num)
            local_json_path = os.path.join(self._run_artifacts_path, f'hammerdb-results_{vm_num}.json')
            workload_complete = self._virtctl.wait_for_vm_workload_completed(
                vm_name=vm_name,
                file_path=self.HAMMERDB_RESULTS_FILE,
                local_path=local_json_path,
                namespace=self._namespace,
                key_path=self._ssh_key_path,
                username=self._username,
                timeout=self._timeout
            )
            if not workload_complete:
                logger.warning(f'Timed out waiting for results in VM {vm_name}')
        except Exception as err:
            self._save_error_logs()
            raise err

    def _delete_vm(self, vm_num: str):
        """Phase 3: Delete VM."""
        try:
            vm_name = self._get_vm_name(vm_num)
            self._oc.delete_vm_sync(yaml=self._get_vm_yaml(vm_num), vm_name=vm_name)
        except Exception as err:
            self._save_error_logs()
            raise err

    def _upload_results(self, vm_count: int):
        """Upload all VM results to ES from the main process (no SSL issues)."""
        if self._enable_prometheus_snapshot:
            self._prometheus_metrics_operation.finalize_prometheus()
            metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
            self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

        run_artifacts_url = os.path.join(
            self._run_artifacts_url,
            f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
        )

        for vm_num in range(vm_count):
            local_json_path = os.path.join(self._run_artifacts_path, f'hammerdb-results_{vm_num}.json')
            hammerdb_results_dict = self._parse_hammerdb_results_vm(local_json_path)
            if not hammerdb_results_dict:
                logger.warning(f'HammerDB results could not be parsed from {local_json_path}')
            elif self._es_host:
                vm_name = self._get_vm_name(str(vm_num))
                vm_node = self._vm_nodes.get(vm_num)
                thread_results = self._hammerdb_thread_results(hammerdb_results_dict)
                for thread_result in thread_results:
                    thread_result.update({
                        'vm_name': vm_name,
                        'vm_name_num': f'hammerdb-vm-{vm_num}',
                        'node': vm_node,
                    })
                    self._upload_hammerdb_thread_result(
                        index=self._es_index,
                        kind=self._kind,
                        status='complete',
                        run_artifacts_url=run_artifacts_url,
                        database=self._database,
                        thread_result=thread_result,
                    )
                    self._verify_elasticsearch_data_uploaded(
                        index=self._es_index,
                        uuid=self._uuid,
                    )
            else:
                logger.info(f'HammerDB results parsed from {local_json_path} (ES upload skipped: no host configured)')

    def _save_error_logs(self):
        """Save logs and upload failure status to Elasticsearch on error."""
        if self._es_host:
            run_artifacts_url = os.path.join(
                self._run_artifacts_url,
                f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )
            tmpl = self._hammerdb_elasticsearch_template_fields()
            self._upload_to_elasticsearch(
                index=self._es_index,
                kind=self._kind,
                status='failed',
                result={**{'run_artifacts_url': run_artifacts_url}, **tmpl},
                database=self._database,
            )
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    @logger_time_stamp
    def run(self):
        """
        Run HammerDB VM workload. Same flow for 1 VM and N VMs.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            parts = self._workload.split('_')
            self._database = parts[2]
            self._kind = 'vm'
            self._name = f'hammerdb_{self._kind}_{self._database}'
            self._workload_name = f'hammerdb-{self._database}-vm'

            if self._run_type == 'test_ci':
                self._es_index = 'hammerdb-test-ci-results'
            else:
                self._es_index = 'hammerdb-results'

            self._ssh_key_path = self._virtctl.generate_ssh_key()
            self._environment_variables_dict['vm_ssh_public_key'] = self._virtctl.get_ssh_public_key(self._ssh_key_path)
            self._template.generate_yamls(scale=str(self._scale), scale_nodes=self._scale_node_list,
                                          redis=self._redis, thread_limit=self._threads_limit)

            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))
            configmap_yaml = os.path.join(
                self._run_artifacts_path,
                f'hammerdb_{self._kind}_{self._database}_configmap.yaml'
            )
            self._oc.create_async(yaml=configmap_yaml)

            if self._scale:
                vm_count = self._scale * len(self._scale_node_list)
                threads_limit = self._threads_limit
                bulk_sleep = self._bulk_sleep_time
            else:
                vm_count = 1
                threads_limit = 1
                bulk_sleep = 0

            bulks = tuple(self.split_run_bulks(iterable=range(vm_count), limit=threads_limit))

            self._run_parallel_phases([self._create_vm, self._wait_and_collect], bulks, bulk_sleep)

            for vm_num in range(vm_count):
                self._vm_nodes[vm_num] = self._oc.get_vm_node(vm_name=self._get_vm_name(str(vm_num)))

            if self._delete_all:
                self._run_parallel_phases([self._delete_vm], bulks, bulk_sleep)

            self._upload_results(vm_count)

            if self._delete_all:
                self._oc.delete_async(yaml=configmap_yaml)
                self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self._save_error_logs()
            raise err
        except Exception as err:
            self._save_error_logs()
            raise err
