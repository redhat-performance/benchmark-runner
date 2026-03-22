
import json
import os
from datetime import datetime, timezone

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class StressngVM(WorkloadsOperations):
    """
    This class runs stressng VM workload using direct VirtualMachine creation (no operator).
    Cloud-init installs and runs stress-ng inside the VM guest OS.
    Results are extracted via virtctl ssh/scp.
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
        This method runs the stressng VM workload.
        Cloud-init handles installing and running stress-ng inside the VM.
        Results are extracted via virtctl scp.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

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

            # Wait for JSON result file (parser runs inside VM after stress-ng completes)
            local_json_path = os.path.join(self._run_artifacts_path, f'{self.__vm_name}_stressng.json')
            workload_complete = self._virtctl.wait_for_vm_workload_completed(
                vm_name=self.__vm_name,
                file_path='/tmp/stressng.json',
                local_path=local_json_path,
                namespace=self.__namespace,
                key_path=self._ssh_key_path,
                timeout=self._timeout
            )

            self.__status = 'complete' if workload_complete else 'failed'

            # Read parsed JSON
            parsed_metrics = None
            if workload_complete and os.path.exists(local_json_path):
                with open(local_json_path, 'r') as f:
                    parsed_metrics = json.load(f)
                logger.info(f"Parsed metrics from VM: {parsed_metrics}")
            else:
                logger.warning("Failed to extract stress-ng JSON from VM")

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
                    # Build full metrics dict with metadata + parsed values from VM
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
                        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                        'cpu': parsed_metrics.get('cpu', 0.0),
                        'cpu_bogomips': parsed_metrics.get('cpu_bogomips', 0.0),
                        'vm': parsed_metrics.get('vm', 0.0),
                        'vm_bogomips': parsed_metrics.get('vm_bogomips', 0.0),
                        'memcpy': parsed_metrics.get('memcpy', 0.0),
                        'bogo_ops': parsed_metrics.get('bogo_ops', 0.0),
                    }

                    logger.info(f"Uploading stress-ng results: cpu_bogomips={metrics['cpu_bogomips']}, vm_bogomips={metrics['vm_bogomips']}")
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=metrics)

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
                    logger.warning("No stress-ng JSON captured, uploading minimal metadata")
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
