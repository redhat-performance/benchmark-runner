
from typeguard import typechecked

from github import Github
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp
from benchmark_runner.main.environment_variables import environment_variables


class GitHubOperations:
    """
    This class responsible for GitHub operations
    """

    def __init__(self):
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self._git_token = self.__environment_variables_dict.get('git_token', '')
        self._github_repository_short = self.__environment_variables_dict.get('github_repository_short', '')
        self.g = None
        self.repo = None

    def _ensure_repo(self):
        if self.repo is None:
            if not self._git_token:
                raise ValueError('GIT_TOKEN must be set to use GitHub operations')
            self.g = Github(self._git_token)
            self.repo = self.g.get_repo(self._github_repository_short)

    @typechecked
    def create_secret(self, secret_name: str, unencrypted_value: str):
        """
        This method create a new secret
        :return:
        """
        self._ensure_repo()
        self.repo.create_secret(secret_name=secret_name, unencrypted_value=unencrypted_value)

    @typechecked
    def delete_secret(self, secret_name: str):
        """
        This method delete exist secret
        :return:
        """
        self._ensure_repo()
        self.repo.delete_secret(secret_name=secret_name)
