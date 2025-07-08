
import os
import time
from multiprocessing import Process, Manager

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations
from benchmark_runner.common.oc.oc import VMStatus


class BootstormVM(WorkloadsOperations):
    """
    This class runs bootstorm vm
    """

    def __init__(self):
        super().__init__()
        self._name = ''
        self._workload_name = ''
        self._es_index = ''
        self._kind = ''
        self._status = ''
        self._vm_name = ''
        self._data_dict = {}
        self._bootstorm_start_time = {}
        # calc total run time - save first vm run time
        self._bootstorm_first_run_time = None

    def save_error_logs(self):
        """
        This method uploads logs into elastic and s3 bucket in case of error
        @return:
        """
        if self._es_host:
            self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                                f'{self._get_run_artifacts_hierarchy(workload_name=self._get_workload_file_name(self._workload_name), is_file=True)}.tar.gz')
            self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status='failed',
                                          result=self._data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    @logger_time_stamp
    def _set_bootstorm_vm_first_run_time(self):
        """
        This method sets the first vm run time
        @return:
        """
        self._bootstorm_first_run_time = time.time()

    @logger_time_stamp
    def _get_bootstorm_vm_total_run_time(self):
        """
        This method retrieves the total run time from the first VM execution
        @return: The delta time from the first VM execution
        """
        delta = time.time() - self._bootstorm_first_run_time
        return round(delta, 3) * self.MILLISECONDS

    @logger_time_stamp
    def _set_bootstorm_vm_start_time(self, vm_name: str = ''):
        """
        This method captures boot start time for specified VM
        @return:
        """
        self._bootstorm_start_time[vm_name] = time.time()

    @logger_time_stamp
    def _wait_vm_access(self, vm_name: str):
        """
        This method waits for VM access and returns the VM node on success, or False if it fails
        @return:
        """
        if self._oc.get_vm_node(vm_name=vm_name):
            vm_node = self._oc.get_vm_node(vm_name=vm_name)
            if self._oc.wait_for_vm_access(vm_name=vm_name):
                logger.info(f"Successfully virtctl into VM: '{vm_name}' in node {vm_node} ")
            return vm_node
        return False

    @logger_time_stamp
    def _wait_ssh_vm(self, vm_name: str):
        """
        This method verifies ssh into VM and return vm node in success or False if failed
        @return:
        """
        self._virtctl.expose_vm(vm_name=vm_name)
        # wait till vm ssh login
        if self._oc.get_vm_node(vm_name=vm_name):
            vm_node = self._oc.get_vm_node(vm_name=vm_name)
            if vm_node:
                node_ip = self._oc.get_nodes_addresses()[vm_node]
                vm_node_port = self._oc.get_exposed_vm_port(vm_name=vm_name)
                if self._oc.wait_for_vm_ssh(vm_name=vm_name, node_ip=node_ip, vm_node_port=vm_node_port):
                    logger.info(f"Successfully ssh into VM: '{vm_name}' in Node: '{vm_node}' ")
                return vm_node
        return False

    @logger_time_stamp
    def _get_bootstorm_vm_elapsed_time(self, vm_name: str, vm_node: str) -> dict:
        """
        Returns the boot elapse time for the specified VM in milliseconds.
        @return: Dictionary with vm_name, node, and boot elapse time.
        """
        if vm_node:
            delta = round((time.time() - self._bootstorm_start_time[vm_name]) * self.MILLISECONDS, 3)
            data = {'vm_name': vm_name, 'node': vm_node, 'bootstorm_time': delta, 'access_vm': int(bool(vm_node)),}
            logger.info(data)
            return data
        return {}

    def _create_vm_scale(self, vm_num: str):
        """
        This method creates VMs in parallel
        """
        try:
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}_{vm_num}.yaml'))
            # run_strategy run immediately the vm
            if not self._run_strategy:
                self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}', status=VMStatus.Stopped)
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def _finalize_vm(self):
        self._status = 'complete' if self._data_dict else 'failed'
        # update total vm run time
        if not self._verification_only:
            if self._enable_prometheus_snapshot:
                # prometheus queries
                self._prometheus_metrics_operation.finalize_prometheus()
                metric_results = self._prometheus_metrics_operation.run_prometheus_queries()
                self._prometheus_result = self._prometheus_metrics_operation.parse_prometheus_metrics(data=metric_results)
                self._data_dict.update(self._prometheus_result)
            total_run_time = self._get_bootstorm_vm_total_run_time()
            self._data_dict.update({'total_run_time': total_run_time})
        # Google drive run_artifacts_url folder path
        if self._google_drive_path:
            self._data_dict.update({'run_artifacts_url': self.get_run_artifacts_google_drive()})
        if self._es_host:
            # upload several run results
            self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status=self._status,
                                          result=self._data_dict)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

    def _run_vm(self):
        """
        This method runs one VM, upload results to Elasticsearch, and destroys VM synchronously
        @return:
        """
        self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'))
        self._oc.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}', status=VMStatus.Stopped)
        self._set_bootstorm_vm_first_run_time()
        self._set_bootstorm_vm_start_time(vm_name=self._vm_name)
        self._virtctl.start_vm_sync(vm_name=self._vm_name)
        self.vm_node = self._wait_vm_access(vm_name=self._vm_name)
        self._data_dict = self._get_bootstorm_vm_elapsed_time(vm_name=self._vm_name, vm_node=self.vm_node)
        self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url,
                                                            f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
        self._finalize_vm()
        self._oc.delete_vm_sync(
            yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
            vm_name=self._vm_name)

    def _verify_single_vm_access(self, vm_name, retries=5, delay=10):
        """
        This method verifies access to a single VM using a retry mechanism, and saves the error and YAML file in case of failure
        :param vm_name: The name of the VM to verify.
        :param retries: Number of retry attempts.
        :param delay: Time to wait (in seconds) between retries.
        @return: access_status 'True' if successful, or an error message if it fails
        """
        access_status = None
        for attempt in range(retries):
            try:
                access_status = self._oc.get_vm_access(vm_name)

                if str(access_status).lower() == "true":
                    # Log success and store relevant data
                    logger.info(f"VM {vm_name} verified successfully (virtctl SSH status: {access_status}).")
                    break  # Exit loop on success
                else:
                    logger.info(f"Attempt {attempt + 1}/{retries}: VM {vm_name} not reachable via Virtctl SSH. Retrying...")

            except Exception as e:
                logger.info(f"Attempt {attempt + 1}/{retries} failed for Virtctl SSH VM {vm_name}: {e}")

            # Sleep before retrying
            if attempt < retries - 1:
                time.sleep(delay)

        # Final update to self._data_dict after all attempts
        vm_node = self._oc.get_vm_node(vm_name)  # Get the node again in case it changed
        self._data_dict = {
            'vm_name': vm_name,
            'node': vm_node,
            'access_vm': 1 if str(access_status).lower() == "true" else 0, # int value for Grafana
            'access_status': access_status,
            'test_name': self._test_name,
            'run_artifacts_url': os.path.join(
                self._run_artifacts_url,
                f"{self._get_run_artifacts_hierarchy(self._workload_name, True)}-{self._time_stamp_format}.tar.gz"
            )
        }

        if str(access_status).lower() != "true":
            logger.info(
                f"All attempts failed for VM {vm_name}. Final SSH status: {self._data_dict.get('access_status', 'No status available')}")
            error_log_path = f"{self._run_artifacts_path}/{vm_name}_error.log"

            # Retrieve the status or use a default message
            status_message = self._data_dict.get('access_status') or "No status available"

            try:
                self._oc.save_to_yaml(vm_name, str(access_status).lower() == 'true', output_dir=self._run_artifacts_path)
                self._oc.save_describe_yaml(vm_name, str(access_status).lower() == 'true', output_dir=self._run_artifacts_path)
                with open(error_log_path, "w") as error_log_file:
                    error_log_file.write(self._oc.get_vm_status(vm_name=vm_name) + "\n")
                    error_log_file.write("VM Status: " + access_status + "\n")
                    error_log_file.write("Running node: " + self._oc.get_vm_node(vm_name=vm_name) + "\n\n")
                    error_log_file.write(str(status_message) + "\n")
            except Exception as write_err:
                logger.error(f"Failed to write error log for {vm_name}: {write_err}")

        self._finalize_vm()
        return access_status

    def _verify_single_vm_access_wrapper(self, vm_name, return_dict):
        """
        This method verifies access to a single VM, saves its YAML files, and updates the VM status in return_dict
        :param vm_name:
        :param return_dict:
        :return:
        """
        vm_access = self._verify_single_vm_access(vm_name)
        return_dict[vm_name] = vm_access

    def _verify_vms_access_in_parallel(self, vm_names: list):
        """
        Verifies access to a list of VMs in parallel using subprocesses.

        :param vm_names: List of VM names to verify.
        :return: List of VM names that failed the access verification.
        """
        if not vm_names:
            return []

        failure_vms = []
        manager = Manager()
        return_dict = manager.dict()

        # Split vm_names according to self._threads_limit
        for i in range(0, len(vm_names), self._threads_limit):
            bulk = vm_names[i:i + self._threads_limit]
            processes = []

            for vm_name in bulk:
                p = Process(target=self._verify_single_vm_access_wrapper, args=(vm_name, return_dict))
                p.start()
                processes.append(p)

            for p in processes:
                p.join()

        # After all processes are done, collect failures
        for vm_name, status in return_dict.items():
            if str(status).lower() != 'true':
                failure_vms.append(vm_name)
        return failure_vms

    def _verify_vms_access(self, vm_names: list, delay=10):
        """
        This method verifies access for each VM
        It prepares the data for ElasticSearch, generates a must-gather in case of an error, and uploads it to Google Drive.
        :param delay: delay between each iteration
        """
        try:
            if not vm_names:
                return []
            upgrade_done = True
            failure_vms = []  # List to store failed VM names

            if self._wait_for_upgrade_version:
                logger.info(f"wait for ocp upgrade version: {self._wait_for_upgrade_version}")
                upgrade_done = self._oc.get_cluster_status() == f'Cluster version is {self._wait_for_upgrade_version}'
                start_time = time.time()

                while (self._timeout <= 0 or time.time() - start_time <= self._timeout) and not upgrade_done:
                    failure_vms = self._verify_vms_access_in_parallel(vm_names)
                    upgrade_done = self._oc.get_cluster_status() == f'Cluster version is {self._wait_for_upgrade_version}'

                    if upgrade_done:
                        break

                    # Sleep between each cycle
                    time.sleep(delay)
            else:
                failure_vms = self._verify_vms_access_in_parallel(vm_names)

            if self._wait_for_upgrade_version:
                logger.info(f'Cluster is upgraded to: {self._wait_for_upgrade_version}')

            if failure_vms:
                if self._must_gather_log:
                    self._oc.generate_must_gather(destination_path=self._run_artifacts_path)
                    self._oc.generate_cnv_must_gather(destination_path=self._run_artifacts_path, cnv_version=self._cnv_version)
                    self._oc.generate_odf_must_gather(destination_path=self._run_artifacts_path, odf_version=self._odf_version)
                # Error log with details of failed VM, for catching all vm errors
                logger.error(f"Failed to verify virtctl SSH login for the following VMs: {', '.join(failure_vms)}")
            # Upload artifacts in validation
            if self._google_drive_shared_drive_id:
                self.upload_run_artifacts_to_google_drive()
            elif self._endpoint_url:
                self.upload_run_artifacts_to_s3()
            else:
                self._save_artifacts_local = True
            if self._es_host:
                self._data_dict.update({'run_artifacts_url': self.get_run_artifacts_google_drive(), 'failure_vms': failure_vms, 'verification_failure': True})
                # upload several run results
                self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status=self._status,result=self._data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)

        except Exception as err:
            # Save run artifacts logs
            self.save_error_logs()
            raise err

    def _run_vm_scale(self, vm_num: str):
        """
        This method runs VMs in parallel and wait for login to be enabled
        """
        try:
            vm_name = f'{self._workload_name}-{self._trunc_uuid}-{vm_num}'
            self._set_bootstorm_vm_start_time(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
            # run_strategy run immediately the vm
            if not self._run_strategy:
                self._virtctl.start_vm_async(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
            self._virtctl.wait_for_vm_status(vm_name=vm_name, status=VMStatus.Running)
            vm_node = self._wait_vm_access(vm_name)
            self._data_dict = self._get_bootstorm_vm_elapsed_time(vm_name=vm_name, vm_node=vm_node)
            self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-scale-{self._time_stamp_format}.tar.gz')
            self._finalize_vm()
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def _stop_vm_scale(self, vm_num: str):
        """
        This method stops VMs async in parallel
        """
        try:
            self._virtctl.stop_vm_async(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def _wait_for_stop_vm_scale(self, vm_num: str):
        """
        This method waits for VMs stop in parallel
        """
        try:
            self._virtctl.wait_for_vm_status(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def _delete_vm_scale(self, vm_num: str):
        """
        This method deletes VMs async in parallel
        """
        try:
            self._oc.delete_async(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}_{vm_num}.yaml'))
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def _wait_for_delete_vm_scale(self, vm_num: str):
        """
        This method waits for VMs delete in parallel
        """
        try:
            self._oc.wait_for_vm_delete(vm_name=f'{self._workload_name}-{self._trunc_uuid}-{vm_num}')
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err

    def _initialize_run(self):
        """
        Initialize prometheus start time, vm name, kind and create benchmark-runner namespace for bootstorm vms
        """
        if self._enable_prometheus_snapshot:
            self._prometheus_metrics_operation.init_prometheus()
        self._name = self._workload
        self._workload_name = self._workload.replace('_', '-')
        self._vm_name = f'{self._workload_name}-{self._trunc_uuid}'
        self._kind = 'vm'
        self._environment_variables_dict['kind'] = 'vm'
        if not self._verification_only:
            # create namespace
            self._oc.create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))

    def run_vm_workload(self):
        # verification only w/o running or deleting any resource
        if self._verification_only:
            vm_names = self._oc._get_all_vm_names()
            if vm_names:
                self._verify_vms_access(vm_names)
            else:
                logger.info("No running VMs")
        else:
            if not self._scale:
                self._run_vm()
            # scale
            else:
                first_run_time_updated = False
                # Create VMs
                if self._create_vms_only:
                    steps = (self._create_vm_scale, )
                # Run VMs without deleting
                elif not self._delete_all:
                    steps = (self._create_vm_scale, self._run_vm_scale)
                else:
                    steps = (self._create_vm_scale, self._run_vm_scale, self._stop_vm_scale,
                             self._wait_for_stop_vm_scale,self._delete_vm_scale, self._wait_for_delete_vm_scale)

                # create run bulks
                bulks = tuple(self.split_run_bulks(iterable=range(self._scale * len(self._scale_node_list)),
                                                   limit=self._threads_limit))
                # create, run and delete vms
                for target in steps:
                    proc = []
                    for bulk in bulks:
                        for vm_num in bulk:
                            # save the first run vm time
                            if self._run_vm_scale == target and not first_run_time_updated:
                                self._set_bootstorm_vm_first_run_time()
                                first_run_time_updated = True
                            p = Process(target=target, args=(str(vm_num),))
                            p.start()
                            proc.append(p)
                        for p in proc:
                            p.join()
                        # sleep between bulks
                        time.sleep(self._bulk_sleep_time)
                        proc = []

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self._initialize_run()
            if self._run_type in ('test_ci', 'chaos_ci'):
                # ElasticSearch name convention must be with '-'
                self._es_index = f"bootstorm-{self._run_type.replace('_', '-')}-results"
            else:
                self._es_index = 'bootstorm-results'
            self.run_vm_workload()
            if self._delete_all:
                # delete namespace
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
                vm_name=self._vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            self.save_error_logs()
            raise err
