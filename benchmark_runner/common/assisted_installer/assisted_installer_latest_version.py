
import json
# import urllib library
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger


class AssistedInstallerVersions:
    """
    This class get the latest assisted installer version from https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/graph
    """

    OCP_VERSIONS_URL = "https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/graph"
    # MAJOR.MINOR.PATCH.BUILD
    IND_MAJOR = 0
    IND_MINOR = 1
    IND_PATCH = 2
    IND_BUILD = 3

    def __init__(self):
        self.__url = self.OCP_VERSIONS_URL

    def __get_versions(self):
        """
        This method get the OCP versions from url and return json data
        :return: versions in json
        """
        response = {}
        # store the response of URL
        try:
            response = urlopen(self.__url)
        except HTTPError as err:
            logger.error('HTTPError code: ', err.code)
        except URLError as err:
            logger.error('URLError code: ', err.reason)
        # Storing the JSON response from url in data
        if response:
            return json.loads(response.read())
        else:
            raise Exception(f'Error reading OCP versions from url: {self.__url}')

    def get_several_latest_versions(self, latest_versions: list):
        """
        The method returns list of latest versions
        @param latest_versions: list of required latest versions
        @return:
        """
        result = []
        for latest_version in latest_versions:
            latest = self.get_latest_version(latest_version)
            result.append(latest)
        return result

    def get_latest_version(self, latest_version: str):
        """
        This method returns the latest version from json data
        :param latest_version: 4.XX or 4.XX.0-rc/ec/fc
        rc=release candidate| ec=engineering candidate| fc=feature candidate
        :return:
        """
        release_list = []
        release_candidate_list = []
        release_version = ''  # Version=4.X.X
        release_candidate_version = ''  # Version=4.X.0-rc.X
        latest_version = latest_version.split('.')
        for version in self.__get_versions()['nodes']:
            version_data = str(version['version']).split('.')
            if f"{latest_version[self.IND_MAJOR]}.{latest_version[self.IND_MINOR]}" == f'{version_data[self.IND_MAJOR]}.{version_data[self.IND_MINOR]}':
                # Release version=4.X.X
                if len(version_data) == self.IND_PATCH + 1:
                    release_version = f'{version_data[self.IND_MAJOR]}.{version_data[self.IND_MINOR]}'
                    release_list.append(int(version_data[self.IND_PATCH]))
                # Release candidate version=4.X.0-rc.X and skip 4.X.X-0.nightly-2022-09-06-225330
                if len(version_data) == self.IND_BUILD + 1 and len(version_data[self.IND_BUILD]) <= 2:
                    # Specific Release candidate version=4.X.0-rc
                    if len(latest_version) == self.IND_BUILD:
                        if latest_version[self.IND_PATCH] == version_data[self.IND_PATCH]:
                            release_candidate_version = '.'.join([version_data[self.IND_MAJOR], version_data[self.IND_MINOR], version_data[self.IND_PATCH]])
                            release_candidate_list.append(int(version_data[self.IND_BUILD]))
                    else:
                        release_candidate_version = '.'.join(
                            [version_data[self.IND_MAJOR], version_data[self.IND_MINOR], version_data[self.IND_PATCH]])
                        release_candidate_list.append(int(version_data[self.IND_BUILD]))

        # Priority to release version
        if release_list and len(latest_version) == self.IND_PATCH:
            return f'{release_version}.{max(release_list)}'.strip()
        elif release_candidate_list:
            return f'{release_candidate_version}.{max(release_candidate_list)}'.strip()
