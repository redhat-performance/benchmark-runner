

import os
import boto3
import typeguard
from botocore.exceptions import ClientError
from os import listdir
from os.path import isfile, join

from benchmark_runner.common.clouds.shared.s3.s3_operations_exceptions import S3FileNotUploaded, S3FileNotDownloaded, S3FileNotDeleted, S3KeyNotCreated, S3FileNotExist, S3FailedCreatePresingedURL
from benchmark_runner.main.environment_variables import environment_variables


class S3Operations:
    """ This class is responsible for S3 operations """

    def __init__(self, region_name: str = '', endpoint_url: str = None, aws_access_key_id: str = None, aws_secret_access_key: str = None):
        # environment variables
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        # must add region for pytest
        if region_name:
            self.__region = region_name
            self.__endpoint_url = endpoint_url
            self.__aws_access_key_id = aws_access_key_id
            self.__aws_secret_access_key = aws_secret_access_key
        else:
            self.__region = self.__environment_variables_dict.get('region_name', '')
            # must be None for pytest
            self.__endpoint_url = self.__environment_variables_dict.get('endpoint_url', None)
            self.__aws_access_key_id = self.__environment_variables_dict.get('access_key_id', '')
            self.__aws_secret_access_key = self.__environment_variables_dict.get('secret_access_key', '')
        self.__s3_client = boto3.client(service_name='s3',
                                        region_name=self.__region,
                                        endpoint_url=self.__endpoint_url,
                                        aws_access_key_id=self.__aws_access_key_id,
                                        aws_secret_access_key=self.__aws_secret_access_key)

    @typeguard.typechecked
    def upload_file(self, file_name_path: str, bucket: str, key: str, upload_file: str):
        """
        This method upload file to s3
        :param file_name_path:'/home/user/test.txt'
        :param bucket:'benchmark'
        :param key:'test-data'
        :param upload_file:'test.txt'
        :return:
        """
        try:
            self.__s3_client.upload_file(Filename=file_name_path,
                                         Bucket=bucket,
                                         Key=f'{key}/{upload_file}',
                                         ExtraArgs={'ServerSideEncryption': 'AES256'})

        except ClientError:
            raise
        except Exception:
            raise S3FileNotUploaded

    @typeguard.typechecked
    def download_file(self, bucket: str, key: str, download_file: str, file_name_path: str):
        """
        This method download file from s3
        :param bucket:'benchmark'
        :param key:'logs/ec2-idle/2021/01/19/18'
        :param download_file: 'test.txt'
        :param file_name_path:'D:\\Performance\\Projects\\py-image-service\\data\\rt_results\\test.txt'
        :return:
        """
        try:
            if download_file:
                self.__s3_client.download_file(Bucket=bucket, Key=f'{key}/{download_file}', Filename=file_name_path)
            else:
                self.__s3_client.download_file(Bucket=bucket, Key=key, Filename=file_name_path)

        except ClientError:
            raise
        except Exception:
            raise S3FileNotDownloaded

    @typeguard.typechecked
    def delete_file(self, bucket: str, key: str, file_name: str):
        """
        This method delete file from s3
        :param bucket:'benchmark'
        :param key:'test-data'
        :param file_name: 'test.txt'
        :return:
        """
        try:
            self.__s3_client.delete_object(Bucket=bucket, Key=f'{key}/{file_name}')

        except ClientError:
            raise
        except Exception:
            raise S3FileNotDeleted

    @typeguard.typechecked
    def delete_folder(self, bucket: str, key: str):
        """
        This method delete folder from s3
        :param bucket:'benchmark'
        :param key:'framework/test'
        :return:
        """
        try:
            objects_to_delete = self.__s3_client.list_objects(Bucket=bucket, Prefix=key)
            delete_keys = {
                'Objects': [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]}
            if delete_keys['Objects']:
                self.__s3_client.delete_objects(Bucket=bucket, Delete=delete_keys)

        except ClientError:
            raise
        except Exception:
            raise S3FileNotDeleted

    @typeguard.typechecked
    def create_folder(self, bucket: str, key: str):
        """
        This method download file from s3
        :param bucket:'benchmark'
        :param key:'framework/test'
        :return:
        """
        try:
            self.__s3_client.put_object(Bucket=bucket, Key=key)

        except ClientError:
            raise
        except Exception:
            raise S3KeyNotCreated

    @typeguard.typechecked
    def file_exist(self, bucket: str, key: str, file_name: str):
        """
        This method check if file exist
        :param bucket:'benchmark'
        :param key:'framework/test'
        :param file_name:'file.txt'
        :return:
        """
        try:
            response = self.__s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
            if response.get('Contents'):
                for item in response['Contents']:
                    if file_name in item['Key']:
                        return True
            return False

        # Todo add custom error
        except ClientError:
            raise
        except Exception:
            raise S3FileNotExist

    @typeguard.typechecked
    def upload_objects(self, local_source: str, s3_target: str):
        """
        This method upload local data folder to s3 target path
        :param local_source: local data folder i.e. '/home/user/'
        :param s3_target: target s3 path i.e. 'data_store/calc_image_data/'
        :return:
        """
        try:
            if '/' in s3_target:
                targets = s3_target.split('/')
                bucket = targets[0]
                key = '/'.join(targets[1:])
            else:
                bucket = s3_target
                key = ''

            files = [f for f in listdir(local_source) if isfile(join(local_source, f))]
            for file in files:
                filename = os.path.join(local_source, file)
                self.upload_file(file_name_path=filename, bucket=bucket, key=key, upload_file=file)

        except ClientError as err:
            raise
        except Exception:
            raise S3FileNotUploaded

    @typeguard.typechecked
    def download_objects(self, s3_target: str, local_source: str):
        """
        This method download from s3 target to local data folder
        :param local_source: local data folder i.e. '/home/user/
        :param s3_target: target s3 path i.e. 'data_store/calc_image_data/'
        :return:
        """
        files = []
        try:
            if '/' in s3_target:
                targets = s3_target.split('/')
                bucket = targets[0]
                key = '/'.join(targets[1:])
            else:
                bucket = s3_target
                key = ''

            response = self.__s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
            if response.get('Contents'):
                for item in response['Contents']:
                    if item['Key'].split('/')[-1]:
                        files.append(item['Key'].split('/')[-1])
                    else:
                        files.append(item['Key'])

            for file in files:
                file_name = os.path.join(local_source, file)
                self.download_file(bucket=bucket, key=key, download_file=file, file_name_path=file_name)

        except ClientError as err:
            raise
        except Exception:
            raise S3FileNotDownloaded

    @typeguard.typechecked
    def generate_presigned_url(self, bucket: str, key: str, file_name: str):
        """
        This method generate presigned url for specific uploaded object, default 7 days
        :param bucket:'benchmark'
        :param key:'logs/test-data'
        :param file_name:'file.txt'
        :return:
        """
        try:
            return self.__s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket, 'Key': f'{key}/{file_name}'},
                                                    ExpiresIn=604800)
        # Todo add custom error
        except ClientError:
            raise
        except Exception:
            raise S3FailedCreatePresingedURL
