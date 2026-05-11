
import os
from datetime import datetime, timezone

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class SysbenchVM(WorkloadsOperations):
    """
    This class runs sysbench VM workload.
    """
    def __init__(self):
        super().__init__()
        self.__name = self._workload
        self.__workload_name = self._workload.replace('_', '-')
        self.__es_index = ''
        self.__kind = 'vm'
        self.__status = ''
        self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
        self.__namespace = self._environment_variables_dict['namespace']
        self.__username = self._environment_variables_dict.get('vm_user', '') or 'fedora'

    def save_error_logs(self):
        if self._es_host:
            data_dict = {
                'run_artifacts_url': os.path.join(
                    self._run_artifacts_url,
                    f'{self._get_run_artifacts_hierarchy(workload_name=self._get_workload_file_name(self.__workload_name), is_file=True)}.tar.gz'
                )
            }
            self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=data_dict)
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

    @logger_time_stamp
    def run(self):
        """
        This method runs the sysbench VM workload.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'sysbench-test-ci-results'
            else:
                self.__es_index = 'sysbench-results'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create VirtualMachine
            logger.info("Creating sysbench VirtualMachine")
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)

            # Wait for VM to be ready
            self._oc.wait_for_vm_create(vm_name=self.__vm_name)
            self._oc.wait_for_initialized(label=f'app={self.__vm_name}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app={self.__vm_name}', workload=self.__workload_name, label_uuid=False)

            logger.info("VirtualMachine is ready, cloud-init will install and run sysbench inside the VM...")

            # Get cluster name
            cluster_name = self._oc.get_cluster_name()
            self._environment_variables_dict['clustername'] = cluster_name

            # Wait for sysbench to complete (check for mem.txt — last output file)
            local_json_path = os.path.join(self._run_artifacts_path, f'{self.__vm_name}_sysbench.json')
            workload_complete = self._virtctl.wait_for_vm_workload_completed(
                vm_name=self.__vm_name,
                file_path='/opt/sysbench/done',
                local_path=os.path.join(self._run_artifacts_path, f'{self.__vm_name}_done'),
                namespace=self.__namespace,
                key_path=self._ssh_key_path,
                username=self.__username,
                timeout=self._timeout
            )

            # Parse results: write parser locally, SCP to VM, run via SSH, SCP result back
            if workload_complete:
                logger.info("Sysbench complete, parsing results via SSH")
                parser_lines = [
                    "import re, json",
                    "r = {'workload': 'sysbench'}",
                    "for f, p in [('cpu', 'cpu'), ('mem', 'memory')]:",
                    "    t = open(f'/opt/sysbench/{f}.txt').read()",
                    "    for x, k, fn in [",
                    r"        (r'events\s+\(avg/stddev\):\s+([\d.]+)', 'events_avg', float),",
                    r"        (r'95th percentile:\s+([\d.]+)', 'latency_95th', float),",
                    r"        (r'events per second:\s+([\d.]+)', 'events_per_second', float),",
                    r"        (r'total number of events:\s+(\d+)', 'total_events', int),",
                    r"        (r'total time:\s+([\d.]+)s', 'total_time', float),",
                    r"        (r'avg:\s+([\d.]+)', 'latency_avg', float),",
                    r"        (r'Number of threads:\s+(\d+)', 'threads', int),",
                    r"        (r'MiB transferred \(([\d.]+) MiB/sec\)', 'throughput_mib', float),",
                    "    ]:",
                    "        m = re.search(x, t, re.DOTALL)",
                    "        if m:",
                    "            r[f'{p}_{k}'] = fn(m.group(1))",
                    "json.dump(r, open('/opt/sysbench/sysbench.json', 'w'))",
                ]
                parser_content = '\n'.join(parser_lines) + '\n'
                local_parser = os.path.join(self._run_artifacts_path, 'sysbench_parser.py')
                with open(local_parser, 'w') as f:
                    f.write(parser_content)
                self._virtctl._scp_to_vm(
                    vm_name=self.__vm_name, local_path=local_parser,
                    remote_path='/opt/sysbench/parse.py', namespace=self.__namespace,
                    key_path=self._ssh_key_path, username=self.__username
                )
                self._virtctl.virtctl_ssh(
                    vm_name=self.__vm_name, command='python3 /opt/sysbench/parse.py',
                    namespace=self.__namespace, key_path=self._ssh_key_path, username=self.__username
                )
                self._virtctl._scp_file(
                    vm_name=self.__vm_name, remote_path='/opt/sysbench/sysbench.json',
                    local_path=local_json_path, namespace=self.__namespace,
                    key_path=self._ssh_key_path, username=self.__username
                )

            self.__status = 'complete' if workload_complete else 'failed'

            # Read parsed JSON
            parsed_metrics = self._load_vm_json_results(local_json_path, 'sysbench') if workload_complete else None

            # Create vm logs
            logger.info("Creating VM logs")
            vm_name = self._create_vm_log(labels=[self.__vm_name])

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__vm_name])

            if self._es_host:
                if parsed_metrics:
                    parsed_metrics['uuid'] = self._uuid
                    parsed_metrics['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

                    logger.info(f"Uploading sysbench results: cpu_events_avg={parsed_metrics.get('cpu_events_avg')}, memory_throughput_mib={parsed_metrics.get('memory_throughput_mib')}")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=parsed_metrics)

                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)

                    if ids:
                        for doc_id in ids:
                            self._update_elasticsearch_index(
                                index=self.__es_index,
                                id=doc_id,
                                kind=self.__kind,
                                status=self.__status,
                                run_artifacts_url=run_artifacts_url,
                                prometheus_result=self._prometheus_result
                            )
                else:
                    logger.warning("No sysbench JSON captured, uploading minimal metadata")
                    minimal_data = {
                        'uuid': self._uuid,
                        'workload': 'sysbench',
                        'kind': self.__kind,
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=minimal_data)

            # Cleanup: delete VirtualMachine
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            raise err

        except Exception as err:
            if self._oc.vm_exists(vm_name=self.__vm_name):
                vm_name = self._create_vm_log(labels=[self.__vm_name])

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=3)
                if ids:
                    for doc_id in ids:
                        self._update_elasticsearch_index(
                            index=self.__es_index,
                            id=doc_id,
                            kind=self.__kind,
                            status='failed',
                            run_artifacts_url=run_artifacts_url
                        )
                else:
                    data_dict = {
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(
                        index=self.__es_index,
                        kind=self.__kind,
                        status='failed',
                        result=data_dict
                    )
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

            # Cleanup on error
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            raise err
