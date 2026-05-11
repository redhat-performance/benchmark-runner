
import os
import re
from datetime import datetime, timezone
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class SysbenchVM(WorkloadsOperations):
    """
    This class runs sysbench VM workload.
    Cloud-init installs and runs sysbench inside the VM guest OS.
    Results are extracted via virtctl scp.
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

    @typechecked
    def _parse_single_section(self, section: str, test_type: str) -> dict:
        """
        Parse a single sysbench test section and extract metrics.
        """
        metrics = {
            'uuid': self._uuid,
            'workload': 'sysbench',
            'kind': 'vm',
            'test_type': test_type,
            'user': self._environment_variables_dict.get('test_user', 'user'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'sysbench_threads': 0,
            'sysbench_time': 0,
            'events_avg': 0.0,
            'latency_95th': 0.0,
            'events_per_second': 0.0,
            'total_events': 0,
            'total_time': 0.0,
            'latency_avg': 0.0,
            'memory_throughput': 0.0,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        events_match = re.search(r'events\s+\(avg/stddev\):\s+([\d.]+)', section)
        if events_match:
            metrics['events_avg'] = float(events_match.group(1))

        latency_match = re.search(r'95th percentile:\s+([\d.]+)', section)
        if latency_match:
            metrics['latency_95th'] = float(latency_match.group(1))

        eps_match = re.search(r'events per second:\s+([\d.]+)', section)
        if eps_match:
            metrics['events_per_second'] = float(eps_match.group(1))

        total_events_match = re.search(r'total number of events:\s+(\d+)', section)
        if total_events_match:
            metrics['total_events'] = int(total_events_match.group(1))

        total_time_match = re.search(r'total time:\s+([\d.]+)s', section)
        if total_time_match:
            metrics['total_time'] = float(total_time_match.group(1))

        latency_avg_match = re.search(r'Latency.*?avg:\s+([\d.]+)', section, re.DOTALL)
        if latency_avg_match:
            metrics['latency_avg'] = float(latency_avg_match.group(1))

        threads_match = re.search(r'Number of threads:\s+(\d+)', section)
        if threads_match:
            metrics['sysbench_threads'] = int(threads_match.group(1))

        if metrics['total_time'] > 0:
            metrics['sysbench_time'] = round(metrics['total_time'])

        if test_type == 'memory':
            throughput_match = re.search(r'MiB transferred \(([\d.]+) MiB/sec\)', section)
            if throughput_match:
                metrics['memory_throughput'] = float(throughput_match.group(1))

        logger.info(f"Parsed sysbench {test_type}: events_avg={metrics['events_avg']}, latency_95th={metrics['latency_95th']}ms, threads={metrics['sysbench_threads']}, time={metrics['sysbench_time']}, memory_throughput={metrics['memory_throughput']}")
        return metrics

    @typechecked
    def _parse_sysbench_output(self, output: str) -> list:
        """
        Parse sysbench output containing CPU and memory test results.
        Returns a list of metrics dicts (one per test type).
        """
        if not output:
            logger.warning("No sysbench output to parse")
            return []

        results = []

        cpu_match = re.search(r'=== SYSBENCH CPU TEST ===(.*?)=== SYSBENCH CPU TEST DONE ===', output, re.DOTALL)
        if cpu_match:
            results.append(self._parse_single_section(cpu_match.group(1), 'cpu'))

        memory_match = re.search(r'=== SYSBENCH MEMORY TEST ===(.*?)=== SYSBENCH MEMORY TEST DONE ===', output, re.DOTALL)
        if memory_match:
            results.append(self._parse_single_section(memory_match.group(1), 'memory'))

        if not results:
            results.append(self._parse_single_section(output, 'cpu'))

        logger.info(f"Uploading {len(results)} sysbench results to ElasticSearch")
        return results

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
        Cloud-init handles installing and running sysbench inside the VM.
        Results are extracted via virtctl scp.
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

            # Create VirtualMachine (cloud-init will install and run sysbench)
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

            # Wait for result file (cloud-init writes to .tmp then renames to .txt on completion)
            local_output_path = os.path.join(self._run_artifacts_path, f'{self.__vm_name}_sysbench.txt')
            workload_complete = self._virtctl.wait_for_vm_workload_completed(
                vm_name=self.__vm_name,
                file_path='/opt/sysbench/output.txt',
                local_path=local_output_path,
                namespace=self.__namespace,
                key_path=self._ssh_key_path,
                username=self.__username,
                timeout=self._timeout
            )

            self.__status = 'complete' if workload_complete else 'failed'

            # Read parsed output
            sysbench_output = None
            if workload_complete and os.path.exists(local_output_path):
                with open(local_output_path, 'r') as f:
                    sysbench_output = f.read()
                logger.info(f"Extracted sysbench output ({len(sysbench_output)} bytes)")
            else:
                logger.warning("Failed to extract sysbench output from VM")

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
                if self.__status == 'complete' and sysbench_output:
                    logger.info("Parsing sysbench output")
                    metrics_list = self._parse_sysbench_output(sysbench_output)
                    for metrics in metrics_list:
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)
                    if ids is False:
                        raise ElasticSearchDataNotUploaded

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
                    self._upload_to_elasticsearch(
                        index=self.__es_index,
                        kind=self.__kind,
                        status='failed',
                        result={'run_artifacts_url': run_artifacts_url}
                    )
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)

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
