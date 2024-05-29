
from benchmark_runner.common.assisted_installer.assisted_installer_latest_version import AssistedInstallerVersions


def test_get_release_latest_version():
    """
    This method returns the latest version
    @return:
    """
    RELEASE_VERSION_LENGTH = 3
    assisted_installer_versions = AssistedInstallerVersions()
    assert len(assisted_installer_versions.get_latest_version(latest_version='4.11').split('.')) == RELEASE_VERSION_LENGTH


def test_get_release_candidate_latest_version():
    """
    This method returns the latest version
    @return:
    """
    RELEASE_CANDIDATE_VERSION_LENGTH = 4
    assisted_installer_versions = AssistedInstallerVersions()
    assert len(assisted_installer_versions.get_latest_version(latest_version='4.11.0-rc').split('.')) == RELEASE_CANDIDATE_VERSION_LENGTH


def test_get_several_latest_versions():
    """
    This method returns several latest versions
    @return:
    """
    actual_latest_versions = ['4.14', '4.15', '4.16.0-rc']
    assisted_installer_versions = AssistedInstallerVersions()
    assert len(assisted_installer_versions.get_several_latest_versions(latest_versions=actual_latest_versions)) == len(actual_latest_versions)
