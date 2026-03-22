
import os
import re
import time
from datetime import datetime, timezone
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class StressngVM(WorkloadsOperations):
    """
    This class runs stressng VM workload using direct VirtualMachine creation (no operator).
    Cloud-init installs and runs stress-ng inside the VM guest OS.
    Results are extracted via qemu-guest-agent.
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__vm_name = ''

    @typechecked
    def _parse_stressng_output(self, output: str) -> dict:
        """
        Parse stress-ng output and extract metrics

        Args:
            output: Raw stress-ng output text (may include boot messages and other console noise)

        Returns:
            Dictionary with parsed metrics
        """
        metrics = {
            'uuid': self._uuid,
            'workload': 'stressng',
            'kind': 'vm',
            'user': self._environment_variables_dict.get('test_user', 'user'),
            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
            'cluster_name': self._environment_variables_dict.get('clustername', ''),
            'runtype': self._environment_variables_dict.get('runtype', 'all'),
            'timeout': self._environment_variables_dict.get('timeout', 5),
            'cpu_stressors': self._environment_variables_dict.get('cpu_stressors', 1),
            'cpu_percentage': self._environment_variables_dict.get('cpu_percentage', 100),
            'vm_stressors': self._environment_variables_dict.get('vm_stressors', 1),
            'vm_bytes': self._environment_variables_dict.get('vm_bytes', '256M'),
            'mem_stressors': self._environment_variables_dict.get('mem_stressors', 1),
            'cpu_bogomips': 0.0,
            'vm_bogomips': 0.0,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        if not output:
            logger.warning("No stress-ng output to parse")
            return metrics

        # Parse bogo ops from stress-ng metrics-brief output
        # Example: "stress-ng: metrc: [987] cpu               11725     10.01 ..."
        cpu_match = re.search(r'\scpu\s+([\d.]+)', output)
        if cpu_match:
            metrics['cpu_bogomips'] = float(cpu_match.group(1))

        vm_match = re.search(r'\svm\s+([\d.]+)', output)
        if vm_match:
            metrics['vm_bogomips'] = float(vm_match.group(1))

        logger.info(f"Parsed metrics: cpu_bogomips={metrics['cpu_bogomips']}, vm_bogomips={metrics['vm_bogomips']}")
        return metrics

    def save_error_logs(self):
        """
        This method uploads logs into elastic and s3 bucket in case of error
        """
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
        This method runs the stressng VM workload.
        Cloud-init handles installing and running stress-ng inside the VM.
        Results are extracted via qemu-guest-agent.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set workload type
            self.__kind = 'vm'
            self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'stressng-test-ci-results'
            else:
                self.__es_index = 'stressng-results'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create VirtualMachine (cloud-init will install and run stress-ng)
            logger.info("Creating stressng VirtualMachine")
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)

            # Wait for VM to be ready
            self._oc.wait_for_vm_create(vm_name=self.__vm_name)
            self._oc.wait_for_initialized(label=f'app=stressng-vm-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=stressng-vm-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            logger.info("VirtualMachine is ready, cloud-init will install and run stress-ng inside the VM...")

            # Get cluster name
            cluster_name = self._oc.get_cluster_name()
            self._environment_variables_dict['clustername'] = cluster_name

            # Wait for guest agent to connect (cloud-init installs qemu-guest-agent)
            namespace = self._environment_variables_dict['namespace']
            logger.info("Waiting for qemu-guest-agent to connect...")
            agent_ready = self._oc.wait_for_guest_agent(vm_name=self.__vm_name, namespace=namespace, timeout=180)

            # Find virt-launcher pod and domain
            pod_name = self._oc.get_virt_launcher_pod(vm_name=self.__vm_name, namespace=namespace)
            domain = self._oc.get_vm_domain(pod_name=pod_name, namespace=namespace) if pod_name else ''

            if not agent_ready or not pod_name or not domain:
                logger.warning(f"Guest agent setup incomplete: agent={agent_ready}, pod={pod_name}, domain={domain}")

            # Wait for stress-ng to complete by polling for signal file via guest agent
            # Use general timeout for polling (default 3600s = 1 hour)
            stressng_timeout = int(self._environment_variables_dict.get('stressng_timeout', 30))
            max_wait = self._timeout
            logger.info(f"Waiting up to {max_wait}s for stress-ng completion (stress-ng timeout={stressng_timeout}s)...")

            workload_complete = False
            poll_interval = 5
            for elapsed in range(0, max_wait, poll_interval):
                if pod_name and domain:
                    # Check for signal file via guest agent
                    check_result = self._oc.guest_exec(pod_name=pod_name, domain=domain, command='/bin/test', args=['-f', '/opt/stressng/workload_complete.signal'], namespace=namespace)
                    if check_result is not None:
                        logger.info(f"stress-ng completed (signal file found after {elapsed}s)")
                        workload_complete = True
                        break
                if elapsed > 0 and elapsed % 30 == 0:
                    logger.info(f"Still waiting for stress-ng completion... ({elapsed}s)")
                time.sleep(poll_interval)

            self.__status = 'complete' if workload_complete else 'failed'

            if not workload_complete:
                logger.warning(f"Timed out after {max_wait}s waiting for stress-ng completion")

            # Extract stress-ng results via guest agent
            stressng_output = None
            if pod_name and domain:
                # Try guest-exec (cat) first
                logger.info("Extracting stress-ng results via guest-exec...")
                stressng_output = self._oc.guest_exec(pod_name=pod_name, domain=domain, command='/bin/cat', args=['/opt/stressng/output.txt'], namespace=namespace)

                # Fallback to guest-file-read if guest-exec failed
                if not stressng_output:
                    logger.info("guest-exec failed, trying guest-file-read fallback...")
                    stressng_output = self._oc.guest_file_read(pod_name=pod_name, domain=domain, file_path='/opt/stressng/output.txt', namespace=namespace)

                if stressng_output:
                    logger.info(f"Extracted stress-ng output ({len(stressng_output)} bytes)")
                    # Save to run artifacts for debugging
                    output_log = os.path.join(self._run_artifacts_path, f'{self.__vm_name}_stressng_output.log')
                    with open(output_log, 'w') as f:
                        f.write(stressng_output)
                else:
                    logger.warning("Failed to extract stress-ng output via both guest-exec and guest-file-read")

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
                if stressng_output:
                    # Parse stress-ng output
                    logger.info("Parsing stress-ng output")
                    metrics = self._parse_stressng_output(stressng_output)

                    # Upload to ElasticSearch
                    logger.info("Uploading stress-ng results to ElasticSearch")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    # Verify data was uploaded
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)

                    # Update metadata
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
                    logger.warning("No stress-ng output captured, uploading minimal metadata")
                    minimal_data = {
                        'uuid': self._uuid,
                        'workload': 'stressng',
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
            self.save_error_logs()
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            raise err

        except Exception as err:
            # Save run artifacts logs
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
