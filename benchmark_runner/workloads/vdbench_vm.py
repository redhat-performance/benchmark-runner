
import os
from multiprocessing import Process

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class VdbenchVM(WorkloadsOperations):
    """
    This class run vdbench vm
    """
    START_STAMP = '@@~@@START-WORKLOAD@@~@@'
    END_STAMP = '@@~@@END-WORKLOAD@@~@@'

    def __init__(self):
        super().__init__()
        self.__name = ''
        self.__workload_name = ''
        self.__es_index = ''
        self.__kind = ''
        self.__status = ''
        self.__pod_name = ''
        self.__vm_name = ''
        self.__data_dict = {}

    def __run_scale(self, vm_num: str):
        """
        This method run vm in parallel
        """
        self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'), vm_name=self.__vm_name)
        self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}-{vm_num}', run_type='vm', label_uuid=False)
        # Create vm log should be direct after vm is ready
        self.__vm_name = self._create_vm_log(labels=[f'{self.__workload_name}-{self._trunc_uuid}-{vm_num}'])
        self.__status = self._oc.wait_for_vm_log_completed(vm_name=self.__vm_name, end_stamp=self.END_STAMP)
        self.__status = 'complete' if self.__status else 'failed'
        # save run artifacts logs
        result_list = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.START_STAMP, end_stamp=self.END_STAMP)
        if self._es_host:
            # upload several run results
            for result in result_list:
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
            # verify that data upload to elastic search according to unique uuid
            self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
        self._oc.delete_vm_sync(
            yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}_{vm_num}.yaml'),
            vm_name=f'{self.__vm_name}-{vm_num}')

    @logger_time_stamp
    def run(self):
        """
        This method runs the workload
        :return:
        """
        try:
            self.__name = self._workload
            if self._run_type == 'test_ci':
                self.__es_index = 'vdbench-test-ci-results'
            else:
                self.__es_index = 'vdbench-results'
            self.__workload_name = self._workload.replace('_', '-')
            self.__vm_name = f'{self.__workload_name}-{self._trunc_uuid}'
            self.__kind = 'vm'
            self._environment_variables_dict['kind'] = 'vm'
            if not self._scale:
                self._oc.create_vm_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'), vm_name=self.__vm_name)
                self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', run_type='vm', label_uuid=False)
                # Create vm log should be direct after vm is ready
                self.__vm_name = self._create_vm_log(labels=[self.__workload_name])
                self.__status = self._oc.wait_for_vm_log_completed(vm_name=self.__vm_name, end_stamp=self.END_STAMP)
                self.__status = 'complete' if self.__status else 'failed'
                # save run artifacts logs
                result_list = self._create_vm_run_artifacts(vm_name=self.__vm_name, start_stamp=self.START_STAMP, end_stamp=self.END_STAMP)
                if self._es_host:
                    # upload several run results
                    for result in result_list:
                        self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status=self.__status, result=result)
                    # verify that data upload to elastic search according to unique uuid
                    self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
                self._oc.delete_vm_sync(
                    yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                    vm_name=self.__vm_name)
            # scale
            else:
                # create namespace
                self._oc._create_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
                # create redis and state signals
                sync_pods = {'redis': 'redis', 'state_signals_exporter_pod': 'state-signals-exporter'}
                for pod, name in sync_pods.items():
                    if pod == 'redis':
                        pod_name = f'redis-master'
                    else:
                        pod_name = name
                    self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{pod}.yaml'), pod_name=pod_name)
                    self._oc.wait_for_initialized(label=f'app={name}', label_uuid=False)
                    self._oc.wait_for_ready(label=f'app={name}', label_uuid=False)
                proc = []
                scale = int(self._scale)
                count = 0
                for scale_node in range(len(self._scale_node_list)):
                    for scale_num in range(scale):
                        count += 1
                        p = Process(target=self.__run_scale, args=(str(count),))
                        p.start()
                        proc.append(p)
                for p in proc:
                    p.join()
                self._create_scale_logs()
                # delete redis and state signals
                for pod, name in sync_pods.items():
                    if pod == 'redis':
                        pod_name = f'redis-master'
                    else:
                        pod_name = name
                    self._oc.delete_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{pod}.yaml'), pod_name=pod_name)
                # delete namespace
                self._oc._delete_async(yaml=os.path.join(f'{self._run_artifacts_path}', 'namespace.yaml'))
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_vm_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.__name}.yaml'),
                vm_name=self.__vm_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            if self._es_host:
                self.__data_dict['run_artifacts_url'] = os.path.join(self._run_artifacts_url, f'{self._get_run_artifacts_hierarchy(workload_name=self.__workload_name, is_file=True)}-{self._time_stamp_format}.tar.gz')
                self._upload_to_elasticsearch(index=self.__es_index, kind=self.__kind, status='failed', result=self.__data_dict)
                # verify that data upload to elastic search according to unique uuid
                self._verify_elasticsearch_data_uploaded(index=self.__es_index, uuid=self._uuid)
            raise err
