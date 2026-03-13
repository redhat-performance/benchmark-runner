
import os
import time
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class UperfVM(WorkloadsOperations):
    """
    This class runs uperf VM workload using direct VirtualMachine creation (no operator)
    """
    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__server_vm_name = ''
        self.__client_vm_name = ''

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
        This method runs the uperf VM workload
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set workload type
            self.__kind = 'vm'
            self.__name = self._workload
            self.__workload_name = self._workload.replace('_', '-')
            self.__server_vm_name = f'uperf-server-{self._trunc_uuid}'
            self.__client_vm_name = f'uperf-client-{self._trunc_uuid}'

            # Set ElasticSearch index (must match template: {{ workload_name }}{{ es_suffix }})
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci'
            else:
                self.__es_index = 'uperf'

            self._environment_variables_dict['kind'] = self.__kind

            # Create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

            # Create VirtualMachines (server + client in one YAML)
            logger.info("Creating uperf server and client VirtualMachines")
            self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)

            # Wait for server VM to be ready
            logger.info("Waiting for uperf server VM")
            self._oc.wait_for_vm_create(vm_name=self.__server_vm_name)
            self._oc.wait_for_initialized(label=f'app=uperf-server-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=uperf-server-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            logger.info("Server VM is ready, getting server IP")

            # Get server VMI IP - retry until IP is assigned
            import subprocess
            server_ip = ""
            max_retries = 30
            for attempt in range(max_retries):
                server_ip_cmd = f"oc get vmi -n {self._environment_variables_dict['namespace']} {self.__server_vm_name} -o jsonpath='{{.status.interfaces[0].ipAddress}}'"
                result = subprocess.run(server_ip_cmd, shell=True, capture_output=True, text=True)
                server_ip = result.stdout.strip().strip("'")
                if server_ip:
                    logger.info(f"Server VMI IP: {server_ip}")
                    break
                logger.info(f"Waiting for server VMI IP (attempt {attempt + 1}/{max_retries})...")
                time.sleep(2)

            if not server_ip:
                raise RuntimeError(f"Failed to get server VMI IP after {max_retries} attempts")

            # Update environment variables with server IP for client template
            self._environment_variables_dict['server_ip'] = server_ip

            # Give server a moment to fully start uperf listener
            time.sleep(5)

            # Re-generate YAML with server IP
            from benchmark_runner.common.template_operations.template_operations import TemplateOperations
            template_ops = TemplateOperations(workload=self._workload)
            template_ops.set_environment_variables(self._environment_variables_dict)
            template_ops.generate_yamls()
            logger.info(f"Regenerated client VM YAML with server IP: {server_ip}")

            # Apply the regenerated YAML directly using oc apply to create client VM
            logger.info("Applying regenerated YAML to create client VM with server IP")
            yaml_path = os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml')
            apply_cmd = f"oc apply -f {yaml_path}"
            result = subprocess.run(apply_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to apply YAML: {result.stderr}")
                raise RuntimeError(f"Failed to apply regenerated YAML: {result.stderr}")
            logger.info(f"Applied YAML successfully: {result.stdout}")

            # Wait for client VM to be ready
            logger.info("Waiting for uperf client VM")
            self._oc.wait_for_vm_create(vm_name=self.__client_vm_name)
            self._oc.wait_for_initialized(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            # Create vm logs should be direct after vms are ready
            logger.info("VirtualMachines are ready, creating logs")
            vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            # Wait for client VM completion (client finishes when tests are done)
            self.__status = self._oc.wait_for_vm_completed(workload=self.__workload_name, vm_name=vm_name)
            self.__status = 'complete' if self.__status else 'failed'

            if self._enable_prometheus_snapshot:
                # Prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__server_vm_name, self.__client_vm_name])

            if self._es_host:
                # Verify that data uploaded to ElasticSearch (snafu uploads it during VM run)
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

            # Cleanup: delete VirtualMachines
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            self.save_error_logs()
            # Cleanup on error
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)
            raise err

        except Exception as err:
            # Save run artifacts logs
            if self._oc.vm_exists(vm_name=self.__server_vm_name) or self._oc.vm_exists(vm_name=self.__client_vm_name):
                vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            run_artifacts_url = os.path.join(
                self._environment_variables_dict.get('run_artifacts_url', ''),
                f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz'
            )

            if self._es_host:
                ids = self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid, timeout=3)
                if ids:
                    for id in ids:
                        self._update_elasticsearch_index(
                            index=self.__es_index,
                            id=id,
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
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)
            raise err
