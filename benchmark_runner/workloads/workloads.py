
import os
from typeguard import typechecked

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.workloads.workloads_operations import WorkloadsOperations


class Workloads(WorkloadsOperations):
    """
    This class create workload
    """
    def __init__(self):
        """
        All inherit from WorkloadsOperations
        """
        super().__init__()

    @typechecked
    @logger_time_stamp
    def vdbench_pod(self, name: str = ''):
        """
    This method run vdbench pog workload
    :return:
    """
        pod_name = ''
        kind = ''
        status = ''
        try:
            if name == '':
                name = self.vdbench_pod.__name__
            workload = name.replace('_', '-')
            pod_name = f'{workload}-{self._trunc_uuid}'
            kind = 'pod'
            if '_kata' in name:
                kind = 'kata'
            if self._run_type == 'test_ci':
                es_index = 'vdbench-test-ci-results'
            else:
                es_index = 'vdbench-results'
            self._environment_variables_dict['kind'] = kind
            self._oc.create_pod_sync(yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'), pod_name=pod_name)
            self._oc.wait_for_initialized(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False)
            self._oc.wait_for_ready(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False)
            status = self._oc.wait_for_pod_completed(label=f'app=vdbench-{self._trunc_uuid}', label_uuid=False, job=False)
            status = 'complete' if status else 'failed'
            # save run artifacts logs
            result = self._create_run_artifacts(pod_name=pod_name)
            metadata = self._get_metadata(kind=kind, status=status, result=result)
            if self._es_host:
                self.es_operations.upload_to_es(index=es_index, data=metadata)
                # verify that data upload to elastic search according to unique uuid
                self.es_operations.verify_es_data_uploaded(index=es_index, uuid=self._uuid)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=pod_name)
        except ElasticSearchDataNotUploaded as err:
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=pod_name)
            raise err
        except Exception as err:
            # save run artifacts logs
            result = self._create_run_artifacts(pod_name=pod_name)
            metadata = self._get_metadata(kind=kind, status=status, result=result)
            self.es_operations.upload_to_es(index=es_index, data=metadata)
            self._oc.delete_pod_sync(
                yaml=os.path.join(f'{self._run_artifacts_path}', f'{self.vdbench_pod.__name__}.yaml'),
                pod_name=pod_name)
            raise err

    # The Kata workloads should not be decorated with
    @logger_time_stamp
    def vdbench_kata(self):
        """
        This method run vdbench kata workload
        :return:
        """
        self.vdbench_pod(self.vdbench_kata.__name__)

    @logger_time_stamp
    def run(self):
        """
        The method run workload
        :return:
        """
        self.initialize_workload()
        workloads = Workloads()
        class_method = getattr(workloads, self._workload)
        class_method()
        self.finalize_workload()




