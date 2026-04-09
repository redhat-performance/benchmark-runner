
import os

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class HammerdbVm(WorkloadsOperations):
    """
    This class runs HammerDB VM workload.
    The VM cloud-init runs the full benchmark (DB setup + HammerDB + parse_results.py).
    Results are retrieved by copying /tmp/hammerdb-results.json from the running VM
    via the QEMU guest agent (no virtctl console streaming required).
    """
    HAMMERDB_RESULTS_FILE = '/tmp/hammerdb-results.json'

    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__database = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__vm_name = ''
        self.__namespace = self._environment_variables_dict.get('namespace', 'benchmark-runner')
        self.__username = self._environment_variables_dict.get('vm_user', 'cloud-user')

    def __save_error_logs(self):
        """Save logs and upload failure status to Elasticsearch on error"""
        if self._es_host:
            run_artifacts_url = os.path.join(
                self._run_artifacts_url,
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )
            tmpl = self._hammerdb_elasticsearch_template_fields()
            self._upload_to_elasticsearch(
                index=self.__es_index,
                kind=self.__kind,
                status='failed',
                result={**{'run_artifacts_url': run_artifacts_url}, **tmpl},
                database=self.__database,
            )
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    @logger_time_stamp
    def run(self):
        """
        Run HammerDB VM workload: create VM, wait for ready, copy /tmp/hammerdb-results.json
        from the VM via QEMU guest agent, upload per-thread results to Elasticsearch.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # e.g. workload = 'hammerdb_vm_mariadb' -> database = 'mariadb', kind = 'vm'
            parts = self._workload.split('_')
            self.__database = parts[2]
            self.__kind = 'vm'
            self.__name = f'hammerdb_{self.__kind}_{self.__database}'
            self.__workload_name = f'hammerdb-{self.__database}-vm'
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'

            if self._run_type == 'test_ci':
                self.__es_index = 'hammerdb-test-ci-results'
            else:
                self.__es_index = 'hammerdb-results'

            vm_yaml = os.path.join(self._run_artifacts_path, f'{self.__name}.yaml')
            configmap_yaml = os.path.join(
                self._run_artifacts_path,
                f'hammerdb_{self.__kind}_{self.__database}_configmap.yaml'
            )

            # 1. Generate SSH key and inject public key into VM cloud-init via template regeneration
            ssh_key_path = self._virtctl.generate_ssh_key()
            self._environment_variables_dict['vm_ssh_public_key'] = self._virtctl.get_ssh_public_key(ssh_key_path)
            self._template.generate_yamls(scale=str(self._scale), scale_nodes=self._scale_node_list,
                                          redis=self._redis, thread_limit=self._threads_limit)

            # 2. Create namespace and ConfigMaps (creator, workload, results-parser)
            self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'namespace.yaml'))
            self._oc.create_async(yaml=configmap_yaml)

            # 3. Create VM (Secret + optional PVC + VirtualMachine)
            self._oc.create_vm_sync(yaml=vm_yaml, vm_name=self.__vm_name)

            # 4. Wait for VM guest to be ready (VMI running)
            self._oc.wait_for_ready(label=f'app={self.__vm_name}', run_type='vm', label_uuid=False)

            # 5. Wait for workload completion and SCP /tmp/hammerdb-results.json via virtctl
            local_json_path = os.path.join(self._run_artifacts_path, os.path.basename(self.HAMMERDB_RESULTS_FILE))
            workload_complete = self._virtctl.wait_for_vm_workload_completed(
                vm_name=self.__vm_name,
                file_path=self.HAMMERDB_RESULTS_FILE,
                local_path=local_json_path,
                namespace=self.__namespace,
                key_path=ssh_key_path,
                username=self.__username,
                timeout=self._timeout
            )
            self.__status = 'complete' if workload_complete else 'failed'
            if not workload_complete:
                logger.warning('Timed out waiting for results in VM %s', self.__vm_name)

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # 7. Parse results from the retrieved JSON
            hammerdb_results_dict = self._parse_hammerdb_results_vm(local_json_path)
            if not hammerdb_results_dict:
                logger.warning('HammerDB results could not be parsed from copied JSON (path=%s)', local_json_path)

            # 8. Upload per-thread results to Elasticsearch
            if self._es_host:
                run_artifacts_url = os.path.join(
                    self._run_artifacts_url,
                    f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
                )
                thread_results = self._hammerdb_thread_results(hammerdb_results_dict)
                if thread_results:
                    for thread_result in thread_results:
                        self._upload_hammerdb_thread_result(
                            index=self.__es_index,
                            kind=self.__kind,
                            status=self.__status,
                            run_artifacts_url=run_artifacts_url,
                            database=self.__database,
                            thread_result=thread_result,
                        )
                        extra_match = {
                            k: thread_result[k]
                            for k in ('thread', 'current_worker')
                            if k in thread_result
                        }
                        self._verify_elasticsearch_data_uploaded(
                            index=self.__es_index,
                            uuid=self._uuid,
                            extra_match=extra_match if extra_match else None,
                        )

            # 9. Cleanup
            self._oc.delete_vm_sync(yaml=vm_yaml, vm_name=self.__vm_name)
            self._oc.delete_async(yaml=configmap_yaml)

        except ElasticSearchDataNotUploaded as err:
            self.__save_error_logs()
            raise err
        except Exception as err:
            self.__save_error_logs()
            raise err
