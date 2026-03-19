
import os
import subprocess
import time
import yaml
from datetime import datetime, timezone
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class StressngVM(WorkloadsOperations):
    """
    This class runs stressng VM workload using direct VirtualMachine creation (no operator)
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__vm_name = ''

    def _extract_file_from_vm(self, vm_name, file_path):
        """
        Extract a file from a VM using kubectl exec into virt-launcher pod

        Args:
            vm_name: Name of the VM
            file_path: Path to file inside the VM

        Returns:
            File contents as string, or None if extraction fails
        """
        try:
            # Get virt-launcher pod name
            pod_cmd = f"oc get pods -n {self._environment_variables_dict['namespace']} -l kubevirt.io=virt-launcher -o name | grep {vm_name}"
            result = subprocess.run(pod_cmd, shell=True, capture_output=True, text=True)
            pod_name = result.stdout.strip().replace('pod/', '')

            if not pod_name:
                logger.error(f"Could not find virt-launcher pod for VM {vm_name}")
                return None

            # Extract file from compute container
            extract_cmd = f"oc exec -n {self._environment_variables_dict['namespace']} {pod_name} -c compute -- cat {file_path}"
            result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Failed to extract {file_path} from VM {vm_name}: {result.stderr}")
                return None

            return result.stdout

        except Exception as e:
            logger.error(f"Exception extracting file from VM: {e}")
            return None

    def _parse_stressng_yaml(self, yaml_content):
        """
        Parse stress-ng YAML output and return metrics

        Args:
            yaml_content: stress-ng YAML output as string

        Returns:
            Dictionary with parsed metrics
        """
        # Get environment variables for metadata
        runtype = self._environment_variables_dict.get('runtype', 'sequential')
        timeout = self._environment_variables_dict.get('timeout', 30)
        cpu_stressors = self._environment_variables_dict.get('cpu_stressors', 1)
        cpu_percentage = self._environment_variables_dict.get('cpu_percentage', 100)
        vm_stressors = self._environment_variables_dict.get('vm_stressors', 1)
        vm_bytes = self._environment_variables_dict.get('vm_bytes', '128M')
        mem_stressors = self._environment_variables_dict.get('mem_stressors', 1)

        # Default document
        doc = {
            'uuid': self._uuid,
            'workload': 'stressng',
            'kind': 'vm',
            'runtype': runtype,
            'timeout': timeout,
            'cpu_stressors': cpu_stressors,
            'cpu_percentage': cpu_percentage,
            'vm_stressors': vm_stressors,
            'vm_bytes': vm_bytes,
            'mem_stressors': mem_stressors,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        }

        if not yaml_content:
            logger.warning("No stress-ng YAML content to parse")
            return doc

        try:
            # Parse YAML
            data = yaml.safe_load(yaml_content)

            if not data or 'metrics' not in data:
                logger.warning("No metrics found in stress-ng YAML")
                return doc

            # Extract individual stressor results
            for metric in data.get('metrics', []):
                stressor = metric.get('stressor', '')
                bogo_ops = metric.get('bogo-ops', 0)
                if stressor:
                    doc[stressor] = bogo_ops

            logger.info(f"Parsed {len(data.get('metrics', []))} stressor metrics from stress-ng output")

        except Exception as e:
            logger.error(f"Error parsing stress-ng YAML: {e}")

        return doc

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
        This method runs the stressng VM workload
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

            # Create VirtualMachine
            logger.info("Creating stressng VirtualMachine")
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)

            # Wait for VM to be ready
            self._oc.wait_for_vm_create(vm_name=self.__vm_name)
            self._oc.wait_for_initialized(label=f'app=stressng-vm-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=stressng-vm-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            # Wait for workload to complete by polling for signal file
            logger.info("Waiting for stress-ng workload to complete...")
            max_wait = 600  # 10 minutes timeout
            wait_interval = 5
            elapsed = 0
            workload_complete = False

            while elapsed < max_wait:
                # Check if signal file exists
                signal_check = self._extract_file_from_vm(self.__vm_name, '/tmp/workload_complete.signal')
                if signal_check is not None:
                    logger.info("Workload completed (signal file found)")
                    workload_complete = True
                    break
                time.sleep(wait_interval)
                elapsed += wait_interval
                if elapsed % 30 == 0:
                    logger.info(f"Still waiting for workload completion... ({elapsed}s elapsed)")

            if not workload_complete:
                logger.warning(f"Workload did not complete within {max_wait}s timeout")
                self.__status = 'failed'
            else:
                self.__status = 'complete'

            # Extract stress-ng results while VM is still running
            logger.info(f"Extracting stress-ng results from VM: {self.__vm_name}")
            yaml_content = self._extract_file_from_vm(self.__vm_name, '/tmp/stressng.yml')

            # Create vm log after extraction (VM still running)
            logger.info("Creating VM logs")
            vm_name = self._create_vm_log(labels=[self.__vm_name])

            if self._enable_prometheus_snapshot:
                # Prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__vm_name])

            # Upload results to ElasticSearch
            if self._es_host:
                if yaml_content:
                    # Parse stress-ng YAML
                    logger.info("Parsing stress-ng YAML output")
                    metrics = self._parse_stressng_yaml(yaml_content)

                    # Upload to ElasticSearch
                    logger.info("Uploading stress-ng results to ElasticSearch")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

                    # Verify data was uploaded
                    ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=60)

                    # Update metadata for each result (if data was found)
                    if ids:
                        for id in ids:
                            self._update_elasticsearch_index(
                                index=self.__es_index,
                                id=id,
                                kind=self.__kind,
                                status=self.__status,
                                run_artifacts_url=run_artifacts_url,
                                prometheus_result=self._prometheus_result
                            )
                else:
                    logger.warning("Failed to extract stress-ng YAML from VM, uploading minimal metadata")
                    # Upload minimal metadata even if we couldn't extract results
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

        except Exception as err:
            # Save run artifacts logs
            if self._oc.vm_exists(vm_name=self.__vm_name):
                vm_name = self._create_vm_log(labels=[self.__vm_name])

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
                # Upload error metadata
                data_dict = {
                    'uuid': self._uuid,
                    'workload': 'stressng',
                    'kind': self.__kind,
                    'run_artifacts_url': run_artifacts_url
                }
                self._upload_to_elasticsearch(
                    index=self.__es_index,
                    kind=self.__kind,
                    status='failed',
                    result=data_dict
                )

            # Cleanup on error
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
            raise err
