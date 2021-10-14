import paramiko
import os
import socket

from benchmark_runner.common.remote_ssh.connection_data import ConnectionData
from benchmark_runner.common.remote_ssh.ssh_remote_exceptions import SshConnectionError, SshConnectionFailure, \
    RunCommandError, \
    SshConnectionTimedOut, PathNotExist, FileNotExist, SFTPException, IllegalFilename


class RemoteSsh:
    """
    This class is running remote ssh commands
    """

    def __init__(self, connection_data: ConnectionData):
        self.__p_client = paramiko.SSHClient()
        self.__p_client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())  # This script doesn't work for me unless this line is added!

        self.__p_sftp = None
        # remote host connection data
        self.__hostname = connection_data.host_name
        self.__port = connection_data.port
        self.__username = connection_data.user_name
        self.__key_file = connection_data.ssh_key
        self.__password = connection_data.password
        self.__cmd_timeout = connection_data.timeout

    def connect(self):
        """ This method connect to remote machine """
        try:
            # For connection with ssh key
            if self.__key_file:
                key = paramiko.RSAKey.from_private_key_file(self.__key_file)
                self.__p_client.connect(hostname=self.__hostname, port=self.__port, username=self.__username,
                                        pkey=key, timeout=self.__cmd_timeout)
            # For password
            elif self.__password:
                self.__p_client.connect(hostname=self.__hostname, port=self.__port, username=self.__username,
                                        password=self.__password, timeout=self.__cmd_timeout)
            else:
                raise SshConnectionError

            self.__p_sftp = self.__p_client.open_sftp()

        except socket.timeout as err:
            raise SshConnectionTimedOut(err)

        except Exception as err:
            raise SshConnectionFailure(err)

    def disconnect(self):
        """ This method disconnect from remote machine """
        self.__p_client.close()
        self.__p_sftp.close()

    def run_command(self, command: str):
        """
        This method run command
        :param command:
        :return: command response or Exception
        """
        try:
            pre_command = '. ~/.bash_profile;'
            stdin, stdout, stderr = self.__p_client.exec_command(f'{pre_command}\n {command}')
            opt = stdout.readlines()
            message = "".join(opt)
            return message
        except Exception as err:
            raise RunCommandError(err)

    def mkdir(self, remote_path):
        """
        This method mkdir on remote path
        :param remote_path:
        :return:
        """
        try:
            self.__p_sftp.chdir(remote_path)  # Test if remote path exists
        except IOError:
            self.__p_sftp.mkdir(remote_path)  # Create remote path
            self.__p_sftp.chdir(remote_path)

    def put_remote_dir(self, local, remote):
        """
        This method uploads the contents of the local directory to the remote path. The
        local directory needs to exists. All subdirectories in py_perf-code are
        created under target.
        :param local: local path
        :param remote: remote path
        :return:
        """
        if os.path.isdir(local):
            for file_name in os.listdir(local):
                if os.path.isfile(os.path.join(local, file_name)):
                    self.put_remote_file(local, remote, file_name)
                else:
                    self.mkdir(remote, ignore_existing=True)
                    self.put_remote_file(local, remote, file_name)
        else:
            raise PathNotExist(f'Local path does not exist: {local}')

    def get_remote_dir(self, remote, local):
        """
        This method downloads the contents of the remote directory to the local path. The
        remote directory needs to exists. All subdirectories in py_perf-code are
        created under target.
        :param local: local path
        :param remote: remote path
        :return:
        """

        if self.exist(remote_path=remote):
            for file_name in os.listdir(local):
                if os.path.isfile(os.path.join(local, file_name)):
                    self.get_remote_file(remote, local, file_name)
                else:
                    self.mkdir(remote, ignore_existing=True)
                    self.get_remote_file(remote, local, file_name)
        else:
            raise PathNotExist(f'remote path does not exist: {remote}')

    def put_remote_file(self, local, remote, file_name):
        """
        This method upload file name from local to remote path
        :param local:
        :param remote:
        :param file_name:
        :return:
        """
        if os.path.isfile(f'{local}/{file_name}'):
            if self.exist(remote_path=f'{remote}/{file_name}'):
                try:
                    self.__p_sftp.put(f'{local}/{file_name}', f'{remote}/{file_name}')
                except Exception as err:
                    raise SFTPException(err)
            else:
                raise FileNotExist(f'Remote file does not exist: {remote}/{file_name}')
        else:
            raise FileNotExist(f'Local file does not exist: {local}/{file_name}')

    def get_remote_file(self, remote, local, file_name):
        """
        This method download file name from remote to local path
        :param local:
        :param remote:
        :param file_name:
        :return:
        """
        if self.exist(remote_path=f'{remote}/{file_name}'):
            if os.path.isfile(os.path.join(local, file_name)):
                self.__p_sftp.get(f'{remote}/{file_name}', f'{local}/{file_name}')
            else:
                raise FileNotExist(f'Local file does not exist: {local}/{file_name}')
        else:
            raise FileNotExist(f'Remote file does not exist: {remote}/{file_name}')

    def replace_parameter(self, remote_path, file_name, parameter, value, all_line=False):
        """
        This method is replace parameter in remote file (sed "s@home/test=.@home/test=8@g" test.txt)
        :param remote_path: path to file
        :param file_name: file name
        :param parameter: the parameter
        :param value: the new value
        :param all_line: replace all the line that contains the parameter with value
        :return:
        """
        if all_line:
            res = False
            # This finds a safe delimiter character for sed
            for c in ['/', '@', '#', '$', '%', '^', '&', '*', '-', '<', '>', '!', '~', '+', '-']:
                if c not in parameter:
                    res = True
                    self.run_command(f'sed -i \'s{c}{parameter}{c}{value}{c}g\' {remote_path}/{file_name}')
                    break
            if not res:
                raise RunCommandError
        else:
            if os.path.splitext(file_name)[1] == '.xml':
                self.run_command(f'sed -i \'s/{parameter}[^ ]*"/{parameter}{value}/g\' {remote_path}/{file_name}')
            else:
                self.run_command(f'sed -i \'s/{parameter}[^ ]*/{parameter}{value}/g\' {remote_path}/{file_name}')

    def exist(self, remote_path):
        """
        This method check if file or dir exists on remote
        :param: remote_path to file or dir:
        :return: True if exists otherwise False
        """
        try:
            self.__p_sftp.stat(remote_path)
            return True
        except IOError:
            return False

    def rename(self, old_remote_path, new_remote_path):
        """
        This method rename remote dir
        :param old_remote_path:
        :param new_remote_path:
        """
        if self.exist(old_remote_path):
            self.__p_sftp.rename(old_remote_path, new_remote_path)
        else:
            raise PathNotExist(f'remote path does not exist: {old_remote_path}')

    def rmdir(self, remote_path):
        """
        This method delete entire remote file
        """
        if self.exist(remote_path):
            remote_path_files = self.__p_sftp.listdir(path=remote_path)
            for file in remote_path_files:
                self.__p_sftp.remove(f'{remote_path}/{file}')

    def copy(self, remote_source, remote_target):
        """
        This method copy from remote source to target folder
        """
        if self.exist(remote_source):
            if "'" in remote_source or "'" in remote_target:
                raise IllegalFilename("File name with ' ")
            self.run_command(f"cp -arf -- {remote_source}' '{remote_target}'")


