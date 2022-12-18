
from benchmark_runner.common.assisted_installer.assisted_installer_latest_version import AssistedInstallerVersions


def test_get_release_latest_version():
    """
    This method returns the latest version
    @return:
    """
    assisted_installer_versions = AssistedInstallerVersions()
    assert len(assisted_installer_versions.get_latest_version(latest_version='4.11').split('.')) == 3


def test_get_release_candidate_latest_version():
    """
    This method returns the latest version
    @return:
    """
    assisted_installer_versions = AssistedInstallerVersions()
    assert len(assisted_installer_versions.get_latest_version(latest_version='4.11.0-rc').split('.')) == 4
