from typing import Optional


class ConnectionData:
    """ This class contains server connection details"""
    def __init__(self,
                 host_name: str,
                 user_name: str,
                 port: int,
                 timeout: int,
                 password: Optional[str] = None,
                 ssh_key: Optional[str] = None
                 ):
        self.__host_name = host_name
        self.__user_name = user_name
        self.__password = password
        self.__ssh_key = ssh_key
        self.__port = port
        self.__timeout = timeout

    @property
    def host_name(self):
        """
        host name
        :return:
        """
        return self.__host_name

    @property
    def user_name(self):
        """
        user name
        :return:
        """
        return self.__user_name

    @property
    def password(self):
        """
        password
        :return:
        """
        return self.__password

    @property
    def ssh_key(self):
        """
        ssh key
        :return:
        """
        return self.__ssh_key

    @property
    def port(self):
        """
        port of ssh, default 22
        :return:
        """
        return self.__port

    @property
    def timeout(self):
        """
        timeout in seconds
        :return:
        """
        return self.__timeout
