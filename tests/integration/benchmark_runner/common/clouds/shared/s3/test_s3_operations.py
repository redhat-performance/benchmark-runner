
import tempfile

from benchmark_runner.common.clouds.shared.s3.s3_operations import S3Operations
from tests.integration.benchmark_runner.test_environment_variables import *


def __get_run_artifacts_hierarchy(workload_name: str = ''):
    """
    This method returns log hierarchy
    :param workload_name: workload name
    :return:
    """
    key = test_environment_variable.get('key', '')
    run_type = test_environment_variable.get('run_type', '')
    date_key = test_environment_variable.get('date_key', '')
    if workload_name:
        return os.path.join(key, run_type, date_key, workload_name)
    return os.path.join(key, run_type, date_key)


def get_s3operations():
    """
    This method returns s3operations instance
    :return:
    """
    return S3Operations(region_name=test_environment_variable.get('region_name', ''),
                        endpoint_url=test_environment_variable.get('endpoint_url', ''),
                        aws_access_key_id=test_environment_variable.get('access_key_id', ''),
                        aws_secret_access_key=test_environment_variable.get('secret_access_key', ''))


def test_upload_file():
    """
    This test uploads file/object to s3 and verify it
    :return:
    """
    s3operations = get_s3operations()
    expected_file_name = 'file.txt'
    with tempfile.TemporaryDirectory() as temp_local_directory:
        with open(os.path.join(temp_local_directory, expected_file_name), 'w') as f:
            f.write('test')
        s3operations.upload_file(file_name_path=os.path.join(temp_local_directory, expected_file_name),
                                 bucket=test_environment_variable.get('bucket', ''),
                                 key=__get_run_artifacts_hierarchy(workload_name='test'),
                                 upload_file=expected_file_name)
        assert s3operations.file_exist(bucket=test_environment_variable.get('bucket', ''), key=__get_run_artifacts_hierarchy(workload_name='test'), file_name=expected_file_name)


def test_download_file():
    """
    This test downloads file/object from s3 and verify it
    :return:
    """
    s3operations = get_s3operations()
    expected_file_name = 'file.txt'
    with tempfile.TemporaryDirectory() as temp_local_directory:
        s3operations.download_file(bucket=test_environment_variable.get('bucket', ''),
                                   key=__get_run_artifacts_hierarchy(workload_name='test'),
                                   download_file=expected_file_name,
                                   file_name_path=os.path.join(temp_local_directory, expected_file_name))
        assert os.path.exists(os.path.join(temp_local_directory, expected_file_name))


def test_file_delete():
    """
    This test deletes of file/object from s3 and verify it
    :return:
    """
    s3operations = get_s3operations()
    expected_file_name = 'file.txt'
    s3operations.delete_file(bucket=test_environment_variable.get('bucket', ''),
                             key=__get_run_artifacts_hierarchy(workload_name='test'),
                             file_name=expected_file_name)
    assert not s3operations.file_exist(bucket=test_environment_variable.get('bucket', ''),
                                       key=__get_run_artifacts_hierarchy(workload_name='test'),
                                       file_name=expected_file_name)


def test_delete_folder():
    """
    This test deletes whole folder/key from s3 and verify it
    :return:
    """
    # Upload test object
    test_upload_file()
    s3operations = get_s3operations()
    s3operations.delete_folder(bucket=test_environment_variable.get('bucket', ''),
                               key=f'{test_environment_variable.get('key', '')}/test-ci')
    assert not s3operations.folder_exist(bucket=test_environment_variable.get('bucket', ''),
                                      key=f'{test_environment_variable.get('key', '')}/test-ci')
