
from typeguard import typechecked

from github import Github
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.main.environment_variables import environment_variables


class GitHubOperations:
    """
    This class resposible for GitHub operations
    """

    def __init__(self):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        github_token = self.__environment_variables_dict.get('github_token', '')
        self.g = Github(github_token)
        self.repo = self.g.get_repo(self.__environment_variables_dict.get('github_repository_short', ''))

    @typechecked
    def create_secret(self, secret_name: str, unencrypted_value: str):
        """
        This method create a new secret
        :return:
        """
        self.repo.create_secret(secret_name=secret_name, unencrypted_value=unencrypted_value)

    @typechecked
    def delete_secret(self, secret_name: str):
        """
        This method delete exist secret
        :return:
        """
        self.repo.delete_secret(secret_name=secret_name)
