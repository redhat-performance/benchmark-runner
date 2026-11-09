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

    create_lvms._CreateLVMS__clean_devices(clean_devices_script=CLEAN_DEVICES_SCRIPT)

    calls = oc.run.call_args_list
    # the script is made executable once, then every step runs as its own invocation
    assert calls[0].kwargs['cmd'] == f'chmod +x "{CLEAN_DEVICES_SCRIPT}"'
    for node in ('worker-0', 'worker-1'):
        node_commands = [call.kwargs['cmd'] for call in calls[1:] if f'"{node}"' in call.kwargs['cmd']]
        vg_commands = [command for command in node_commands
                       if 'vgchange -an' in command or 'vgremove -ff' in command]
        assert len(vg_commands) == 2
        for command in vg_commands:
            assert CLEAN_DEVICES_SCRIPT in command
            assert f'"{node}"' in command
            assert 'xargs -r' in command
            # no command substitution: an empty list must not expand to a bare command
            assert '\\$(' not in command
            assert 'vgchange -an $(vgs' not in command
        assert any('wipefs -a /dev/nvme0n1' in command for command in node_commands)
        assert any('wipefs -a /dev/nvme1n1' in command for command in node_commands)
    # every step is checked, so a failure names the step and stops the run before the LVMCluster exists
    assert all(call.kwargs['is_check'] is True for call in calls)


def test_clean_devices_guards_every_device_before_wiping():
    """
    A wrong LVMS_DEVICE_PATHS entry must stop the run instead of wiping an
    unrelated disk: each device is checked to be a block device, unmounted and
    outside any volume group before pvremove/wipefs touch it.
    """
    oc = MagicMock()
    oc.get_worker_nodes.return_value = 'worker-0'
    create_lvms = _create_lvms(oc=oc)

    create_lvms._CreateLVMS__clean_devices(clean_devices_script=CLEAN_DEVICES_SCRIPT)

    commands = [call.kwargs['cmd'] for call in oc.run.call_args_list]
    for device in DEVICES:
        checks = [command for command in commands if f'test -b {device}' in command]
        assert len(checks) == 1
        assert f'findmnt -rn -S {device}' in checks[0]
        assert f'pvs --noheadings -o vg_name --select pv_name={device}' in checks[0]
        assert f"echo '{device} is not a block device'" in checks[0]
        assert f"echo '{device} is mounted'" in checks[0]
        assert f"echo '{device} belongs to a volume group'" in checks[0]
        # the guard runs before pvremove and wipefs are reached on that device
        guard_index = commands.index(checks[0])
        pvremove_index = next(i for i, command in enumerate(commands) if f'pvremove -ff {device}' in command)
        wipefs_index = next(i for i, command in enumerate(commands) if f'wipefs -a {device}' in command)
        assert guard_index < pvremove_index < wipefs_index


def test_clean_devices_skips_when_no_worker_nodes():
    oc = MagicMock()
    oc.get_worker_nodes.return_value = ''
    create_lvms = _create_lvms(oc=oc)

    create_lvms._CreateLVMS__clean_devices(clean_devices_script=CLEAN_DEVICES_SCRIPT)

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


@pytest.mark.parametrize('device', ['/dev/nvme0n1 /dev/sdb', '/dev/nvme0n1;reboot', '-/dev/nvme0n1', 'nvme0n1',
                                    '/dev/nvme0n1$(id)'])
@mock.patch.object(CreateLVMS, '_CreateLVMS__delete_lvmcluster')
def test_create_lvms_rejects_unsafe_device_paths(mock_delete, device):
    """
    Device paths reach pvremove/wipefs unquoted as root on each node: anything
    but a plain /dev path must be rejected before the destructive cleanup.
    """
    create_lvms = _create_lvms(devices=[device])

    with pytest.raises(ValueError, match='Invalid LVMS device path'):
        create_lvms.create_lvms(upgrade_version='')
    mock_delete.assert_not_called()


def test_wait_for_lvmcluster_delete_raises_when_object_remains():
    """
    must_be_deleted: a stuck finalizer must be reported by name instead of
    applying the LVMCluster and timing out on its Ready wait.
    """
    oc = MagicMock()
    oc.run.return_value = 'lvmcluster.lvm.topolvm.io/lvms-nvme\n'
    create_lvms = _create_lvms(oc=oc)

    with pytest.raises(RuntimeError, match='was not deleted'):
        create_lvms._CreateLVMS__wait_for_lvmcluster_delete(must_be_deleted=True)


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
