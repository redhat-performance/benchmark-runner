
import glob
import json
import os
import sys
import time
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.bootstorm_vm import BootstormVM


class WindowsVM(BootstormVM):
    """
    This class runs Windows vm
    """
    def __init__(self):
        super().__init__()
        if not self._windows_url:
            raise ValueError('Missing Windows DV URL')
        self._per_node_dv = self._environment_variables_dict.get('per_node_dv', False)
        self._created_sc_name = ''

    def _create_snapshot_clone_sc(self):
        """Create a StorageClass with snapshot clone strategy for fast LVMS cloning"""
        base_sc = self._environment_variables_dict['vm_storage_class']
        new_sc = f'{base_sc}-bootstorm'
        # Delete if leftover from a previous run
        try:
            self._oc.run(f'{self._oc._cli} delete sc {new_sc} --wait=false')
        except Exception:
            pass
        time.sleep(2)
        # Get base SC details via jsonpath
        provisioner = self._oc.run(f"{self._oc._cli} get sc {base_sc} -o jsonpath='{{.provisioner}}'").strip().strip("'")
        reclaim = self._oc.run(f"{self._oc._cli} get sc {base_sc} -o jsonpath='{{.reclaimPolicy}}'").strip().strip("'")
        binding = self._oc.run(f"{self._oc._cli} get sc {base_sc} -o jsonpath='{{.volumeBindingMode}}'").strip().strip("'")
        params_json = self._oc.run(f"{self._oc._cli} get sc {base_sc} -o jsonpath='{{.parameters}}'").strip().strip("'")
        sc_yaml = (
            f'apiVersion: storage.k8s.io/v1\n'
            f'kind: StorageClass\n'
            f'metadata:\n'
            f'  name: {new_sc}\n'
            f'  annotations:\n'
            f'    cdi.kubevirt.io/clone-strategy: "snapshot"\n'
            f'provisioner: {provisioner}\n'
            f'reclaimPolicy: {reclaim or "Delete"}\n'
            f'volumeBindingMode: {binding or "WaitForFirstConsumer"}\n'
            f'allowVolumeExpansion: true\n'
        )
        if params_json and params_json != '{}':
            try:
                params = json.loads(params_json)
                sc_yaml += 'parameters:\n'
                for k, v in params.items():
                    sc_yaml += f'  {k}: "{v}"\n'
            except json.JSONDecodeError:
                pass
        sc_dir = os.path.join('/tmp', 'bootstorm-sc')
        os.makedirs(sc_dir, exist_ok=True)
        sc_file = os.path.join(sc_dir, 'bootstorm_sc.yaml')
        with open(sc_file, 'w') as f:
            f.write(sc_yaml)
        self._oc.create_async(yaml=sc_file)
        logger.info(f'Created StorageClass {new_sc} with snapshot clone strategy')
        for _ in range(30):
            time.sleep(1)
            try:
                result = self._oc.run(f"{self._oc._cli} get storageprofile {new_sc} -o jsonpath='{{.status.cloneStrategy}}'")
                if result and result.strip().strip("'"):
                    logger.info(f'StorageProfile {new_sc} ready')
                    break
            except Exception:
                pass
        return new_sc

    def _delete_snapshot_clone_sc(self):
        """Delete the auto-created StorageClass"""
        if self._created_sc_name:
            sc_file = os.path.join('/tmp', 'bootstorm-sc', 'bootstorm_sc.yaml')
            if os.path.isfile(sc_file):
                try:
                    self._oc.delete_async(yaml=sc_file)
                    logger.info(f'Deleted StorageClass {self._created_sc_name}')
                except Exception:
                    logger.warning(f'Failed to delete StorageClass {self._created_sc_name}')

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            if self._run_type in ('test_ci', 'chaos_ci', 'func_ci'):
                self._es_index = f"windows-{self._run_type.replace('_', '-')}-results"
            else:
                self._es_index = 'windows-results'
            if self._per_node_dv:
                old_sc = self._environment_variables_dict['vm_storage_class']
                self._created_sc_name = self._create_snapshot_clone_sc()
                self._environment_variables_dict['vm_storage_class'] = self._created_sc_name
            self._initialize_run()
            if self._per_node_dv and self._created_sc_name:
                # Patch already-rendered YAML files with the new SC name
                for yaml_file in glob.glob(os.path.join(self._run_artifacts_path, '*.yaml')):
                    with open(yaml_file, 'r') as f:
                        content = f.read()
                    if old_sc in content:
                        with open(yaml_file, 'w') as f:
                            f.write(content.replace(old_sc, self._created_sc_name))
            if not self._verification_only:
                if self._per_node_dv and self._scale_node_list:
                    for node in self._scale_node_list:
                        self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, f'windows_dv_{node}.yaml'))
                    for node in self._scale_node_list:
                        self._oc.wait_for_dv_status(status='Succeeded', dv_name=f'windows-clone-dv-{node}')
                else:
                    self._oc.create_async(yaml=os.path.join(self._run_artifacts_path, 'windows_dv.yaml'))
                    self._oc.wait_for_dv_status(status='Succeeded')
            self.run_vm_workload()
            if self._delete_all:
                if self._per_node_dv and self._scale_node_list:
                    for node in self._scale_node_list:
                        self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, f'windows_dv_{node}.yaml'))
                else:
                    self._oc.delete_async(yaml=os.path.join(self._run_artifacts_path, 'windows_dv.yaml'))
                # delete namespace
                self._oc.delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
                self._delete_snapshot_clone_sc()
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self._name}.yaml'),
                vm_name=self._vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._es_host:
                self._data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self._workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._upload_to_elasticsearch(index=self._es_index, kind=self._kind, status='failed', result=self._data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self._es_index, uuid=self._uuid)
            raise err
