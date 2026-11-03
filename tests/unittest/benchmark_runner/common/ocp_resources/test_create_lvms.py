"""
Unit tests for the LVMS (LVM Storage) operator installer.

The OC client is mocked: these tests cover command construction and control
flow only, not a live cluster.
"""
from unittest import mock
from unittest.mock import MagicMock

import pytest

from benchmark_runner.common.ocp_resources.create_lvms import CreateLVMS

PATH = '/tmp/lvms'
CLEAN_DEVICES_SCRIPT = f'{PATH}/00_clean_devices.sh'
DEVICES = ['/dev/nvme0n1', '/dev/nvme1n1']


def _create_lvms(oc=None, version='4.22', devices=None, resource_list=None, cluster_name='lvms-nvme'):
    return CreateLVMS(oc=oc if oc is not None else MagicMock(),
                      path=PATH,
                      resource_list=resource_list or [],
                      lvms_version=version,
                      lvms_device_paths=list(DEVICES if devices is None else devices),
                      lvms_cluster_name=cluster_name)


def test_clean_devices_pipes_tagged_vgs_through_xargs():
    """
    An empty @lvms VG list must not turn into a bare 'vgchange -an', which
    targets every volume group on the node.
    """
    oc = MagicMock()
    oc.get_worker_nodes.return_value = 'worker-0 worker-1'
    create_lvms = _create_lvms(oc=oc)

    create_lvms._CreateLVMS__clean_devices(resource_path=CLEAN_DEVICES_SCRIPT)

    commands = [call.kwargs['cmd'] for call in oc.run.call_args_list]
    assert len(commands) == 2
    for node, command in zip(('worker-0', 'worker-1'), commands):
        assert CLEAN_DEVICES_SCRIPT in command
        assert f'"{node}"' in command
        assert 'xargs -r vgchange -an' in command
        assert 'xargs -r vgremove -ff' in command
        assert 'wipefs -a /dev/nvme0n1' in command
        assert 'wipefs -a /dev/nvme1n1' in command
        # no command substitution: an empty list must not expand to a bare command
        assert '\\$(' not in command
        assert 'vgchange -an $(vgs' not in command


def test_clean_devices_skips_when_no_worker_nodes():
    oc = MagicMock()
    oc.get_worker_nodes.return_value = ''
    create_lvms = _create_lvms(oc=oc)

    create_lvms._CreateLVMS__clean_devices(resource_path=CLEAN_DEVICES_SCRIPT)

    oc.run.assert_not_called()


@mock.patch.object(CreateLVMS, 'wait_for_ocp_resource_create')
def test_wait_for_lvms_csv_upgrade_requires_succeeded_phase(mock_wait):
    """
    During an upgrade the new CSV carries the target version while still
    Pending/Installing, so the wait must also require the Succeeded phase.
    """
    create_lvms = _create_lvms()

    create_lvms._CreateLVMS__wait_for_lvms_csv(upgrade_version='4.22')

    kwargs = mock_wait.call_args.kwargs
    assert kwargs['operator'] == 'lvms'
    assert kwargs['status'] == '4.22'
    assert '.status.phase == "Succeeded"' in kwargs['verify_cmd']


@mock.patch.object(CreateLVMS, 'wait_for_ocp_resource_create')
def test_wait_for_lvms_csv_install_waits_for_succeeded(mock_wait):
    create_lvms = _create_lvms()

    create_lvms._CreateLVMS__wait_for_lvms_csv()

    kwargs = mock_wait.call_args.kwargs
    assert kwargs['operator'] == 'lvms'
    assert kwargs['status'] == 'Succeeded'
    assert '.status.phase == "Succeeded"' in kwargs['verify_cmd']


def test_create_lvms_requires_version():
    create_lvms = _create_lvms(version='')

    with pytest.raises(ValueError, match='LVMS_VERSION'):
        create_lvms.create_lvms(upgrade_version='')


def test_create_lvms_requires_device_paths():
    create_lvms = _create_lvms(devices=[])

    with pytest.raises(ValueError, match='LVMS_DEVICE_PATHS'):
        create_lvms.create_lvms(upgrade_version='')


@mock.patch.object(CreateLVMS, '_CreateLVMS__wait_for_lvms_csv')
@mock.patch.object(CreateLVMS, '_CreateLVMS__delete_lvmcluster')
def test_create_lvms_upgrade_only_applies_subscription(mock_delete, mock_wait):
    oc = MagicMock()
    create_lvms = _create_lvms(oc=oc,
                               resource_list=['00_clean_devices.sh', '03_catalogsource.yaml',
                                              '04_subscription.yaml', '05_lvmcluster.yaml'])

    assert create_lvms.create_lvms(upgrade_version='4.22') is True

    oc.apply_async.assert_called_once_with(yaml=f'{PATH}/04_subscription.yaml')
    mock_wait.assert_called_once_with(upgrade_version='4.22')
    mock_delete.assert_not_called()
