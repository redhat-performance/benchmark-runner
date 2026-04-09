
import json
import os
import time
from datetime import datetime, timezone

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class UperfVM(WorkloadsOperations):
    """
    This class runs uperf VM workload using direct VirtualMachine creation (no operator).
    Cloud-init installs and runs uperf inside the VM guest OS.
    Results are extracted via virtctl scp.
    """
    def __init__(self):
        super().__init__()
        self.__name = self._workload
        self.__workload_name = self._workload.replace('_', '-')
        self.__es_index = ''
        self.__kind = 'vm'
        self.__status = ''
        self.__server_vm_name = f'uperf-server-{self._trunc_uuid}'
        self.__client_vm_name = f'uperf-client-{self._trunc_uuid}'
        self.__template_ops = TemplateOperations(workload=self._workload)
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
        This method runs the uperf VM workload.
        Cloud-init handles installing and running uperf inside the VMs.
        Results are extracted via virtctl scp.
        """
        try:
            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.init_prometheus()

            # Set ElasticSearch index
            if self._run_type == 'test_ci':
                self.__es_index = 'uperf-test-ci-results'
            else:
                self.__es_index = 'uperf-results'

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

            # Get server VMI IP
            server_ip = self._oc.get_vmi_ip(namespace=self.__namespace, vm_name=self.__server_vm_name)
            if not server_ip:
                raise RuntimeError(f"Failed to get server VMI IP")
            logger.info(f"Server VMI IP: {server_ip}")

            # Get server VMI node
            server_node = self._oc.get_vm_node(namespace=self.__namespace, vm_name=self.__server_vm_name)
            logger.info(f"Server VMI Node: {server_node}")

            # Get cluster name
            cluster_name = self._oc.get_cluster_name()

            # Update environment variables with server info for client template
            self._environment_variables_dict['server_ip'] = server_ip
            self._environment_variables_dict['server_node'] = server_node
            self._environment_variables_dict['clustername'] = cluster_name

            # Give server a moment to fully start uperf listener
            time.sleep(5)

            # Re-generate YAML with server IP
            self.__template_ops.set_environment_variables(self._environment_variables_dict)
            self.__template_ops.generate_yamls()
            logger.info(f"Regenerated client VM YAML with server IP: {server_ip}")

            # Delete the client VM by name (not by YAML, which would delete server too)
            logger.info("Deleting client VM (created with empty server_ip) before recreating...")
            self._oc.delete_vm_sync(vm_name=self.__client_vm_name, namespace=self.__namespace)
            self._oc.wait_for_vm_delete(vm_name=self.__client_vm_name, namespace=self.__namespace)

            # Apply combined YAML (Secret + Server VM + Client VM)
            logger.info(f"Creating client VM with server IP: {server_ip}")
            yaml_path = os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml')
            self._oc.apply_async(yaml=yaml_path)

            # Wait for client VM to be ready
            logger.info("Waiting for uperf client VM")
            self._oc.wait_for_vm_create(vm_name=self.__client_vm_name)
            self._oc.wait_for_initialized(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)
            self._oc.wait_for_ready(label=f'app=uperf-client-{self._trunc_uuid}', workload=self.__workload_name, label_uuid=False)

            # Get client VMI IP and node
            client_ip = self._oc.get_vmi_ip(namespace=self.__namespace, vm_name=self.__client_vm_name)
            client_node = self._oc.get_vm_node(namespace=self.__namespace, vm_name=self.__client_vm_name)
            logger.info(f"Client VMI IP: {client_ip}, Client VMI Node: {client_node}")
            self._environment_variables_dict['client_ips'] = client_ip + ' ' if client_ip else ''
            self._environment_variables_dict['client_node'] = client_node

            # Wait for JSON result file (parser runs inside VM after uperf completes)
            local_json_path = os.path.join(self._run_artifacts_path, f'{self.__client_vm_name}_uperf.json')
            workload_complete = self._virtctl.wait_for_vm_workload_completed(
                vm_name=self.__client_vm_name,
                file_path='/tmp/uperf.json',
                local_path=local_json_path,
                namespace=self.__namespace,
                key_path=self._ssh_key_path,
                timeout=self._timeout
            )

            self.__status = 'complete' if workload_complete else 'failed'

            # Read parsed JSON (array of test results)
            parsed_results = None
            if workload_complete and os.path.exists(local_json_path):
                with open(local_json_path, 'r') as f:
                    parsed_results = json.load(f)
                logger.info(f"Parsed {len(parsed_results)} uperf test results from VM")
            else:
                logger.warning("Failed to extract uperf JSON from VM")

            # Create vm logs
            logger.info("Creating VM logs")
            vm_name = self._create_vm_log(labels=[self.__server_vm_name, self.__client_vm_name])

            if self._enable_prometheus_snapshot:
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)

            # Save run artifacts logs
            run_artifacts_url = self._create_run_artifacts(labels=[self.__server_vm_name, self.__client_vm_name])

            # Upload results to ElasticSearch
            if self._es_host:
                if parsed_results:
                    logger.info(f"Uploading {len(parsed_results)} uperf results to ElasticSearch")
                    for parsed in parsed_results:
                        # Build full metrics dict: metadata + parsed values from VM
                        metrics = {
                            'uuid': self._uuid,
                            'workload': 'uperf',
                            'kind': 'vm',
                            'test_type': parsed.get('test_type', 'stream'),
                            'protocol': parsed.get('protocol', 'tcp'),
                            'message_size': parsed.get('message_size', 64),
                            'read_message_size': parsed.get('message_size', 64),
                            'num_threads': parsed.get('num_threads', 1),
                            'bytes': parsed.get('bytes', 0),
                            'ops': parsed.get('ops', 0),
                            'norm_byte': parsed.get('norm_byte', 0),
                            'norm_ops': parsed.get('norm_ops', 0),
                            'norm_ltcy': parsed.get('norm_ltcy', 0.0),
                            'duration': parsed.get('duration', 0),
                            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                            'uperf_ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
                            'user': self._environment_variables_dict.get('test_user', 'user'),
                            'run_id': self._environment_variables_dict.get('run_id', 'NA'),
                            'cluster_name': self._environment_variables_dict.get('clustername', ''),
                            'iteration': 0,
                            'client_ips': self._environment_variables_dict.get('client_ips', ''),
                            'remote_ip': server_ip,
                            'service_ip': self._environment_variables_dict.get('service_ip', 'False'),
                            'service_type': self._environment_variables_dict.get('service_type', ''),
                            'port': self._environment_variables_dict.get('port', '30000'),
                            'client_node': self._environment_variables_dict.get('client_node', ''),
                            'server_node': server_node,
                            'num_pairs': self._environment_variables_dict.get('num_pairs', ''),
                            'multus_client': self._environment_variables_dict.get('multus_client', ''),
                            'networkpolicy': self._environment_variables_dict.get('networkpolicy', ''),
                            'density': self._environment_variables_dict.get('density', ''),
                            'nodes_in_iter': self._environment_variables_dict.get('nodes_in_iter', ''),
                            'step_size': self._environment_variables_dict.get('step_size', ''),
                            'colocate': self._environment_variables_dict.get('colocate', ''),
                            'density_range': self._environment_variables_dict.get('density_range', ''),
                            'node_range': self._environment_variables_dict.get('node_range', ''),
                            'pod_id': '',
                            'hostnetwork': self._environment_variables_dict.get('hostnetwork', 'False')
                        }
                        throughput_gbps = round((metrics['norm_byte'] * 8) / (1024**3), 4) if metrics['norm_byte'] > 0 else 0
                        logger.info(f"  {metrics['test_type']}-{metrics['protocol']}-{metrics['message_size']}-{metrics['num_threads']}: "
                                    f"throughput={throughput_gbps}Gbps, latency={metrics['norm_ltcy']}ms")
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
                    logger.warning("Failed to extract uperf JSON from client VM, uploading minimal metadata")
                    minimal_data = {
                        'uuid': self._uuid,
                        'workload': 'uperf',
                        'kind': self.__kind,
                        'run_artifacts_url': run_artifacts_url
                    }
                    self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=minimal_data)

            # Cleanup: delete VirtualMachines
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)

            # Delete namespace
            if self._delete_all:
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

        except ElasticSearchDataNotUploaded as err:
            # Cleanup on ES upload failure
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
                data_dict = {
                    'uuid': self._uuid,
                    'workload': 'uperf',
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
            self._oc.delete_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__server_vm_name)
            raise err
