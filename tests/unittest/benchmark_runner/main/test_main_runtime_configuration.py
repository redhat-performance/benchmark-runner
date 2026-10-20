"""
Verify that main() evaluates configuration at invocation time so
TemporaryEnvironmentVariables overrides affect dispatch, and that workload
construction happens only on workload dispatch branches.
"""
import importlib
import os
from unittest.mock import MagicMock, patch

import pytest

from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.main.temporary_environment_variables import TemporaryEnvironmentVariables


@pytest.fixture
def main_module():
    """Import the entry-point module; tests isolate env via TemporaryEnvironmentVariables."""
    return importlib.import_module('benchmark_runner.main.main')


@pytest.fixture
def isolated_env():
    """
    Isolate environment_variables from ambient WORKLOAD / local defaults.

    Clears early main() dispatch keys so ambient AZURE_CLUSTER_OPERATION,
    INSTALL_OCP_VERSION, UPGRADE_OCP_VERSION, INSTALL_OCP_RESOURCES, or
    CI_STATUS cannot divert mocked tests into real Azure/install/CI paths.
    Also clears runner_type so ambient RUNNER_TYPE cannot override workload
    namespace selection (e.g. force clusterbuster for windows_vm).
    Clears NAMESPACE so ambient NAMESPACE cannot override workload_namespaces
    (Option A: explicit NAMESPACE wins when set).
    Yields the temporary dict with workload cleared.
    """
    with patch.dict(os.environ, {'NAMESPACE': ''}, clear=False):
        with TemporaryEnvironmentVariables():
            temporary = environment_variables.environment_variables_dict
            temporary['workload'] = ''
            temporary['runner_type'] = ''
            temporary['azure_cluster_operation'] = ''
            temporary['install_ocp_version'] = ''
            temporary['upgrade_ocp_version'] = ''
            temporary['install_ocp_resources'] = False
            temporary['ci_status'] = ''
            yield temporary


def test_import_does_not_capture_workload_state(main_module):
    """Import must not bind a stale workload/dispatch snapshot for later main() use."""
    for stale_name in (
        'workload',
        'run_type',
        'environment_variables_dict',
        'is_benchmark_runner_workload',
        'is_clusterbuster_workload',
        'is_krknhub_workload',
        'benchmark_runner_workload',
        'clusterbuster_workload',
        'krknhub_workload',
    ):
        assert not hasattr(main_module, stale_name), f'import-time capture still present: {stale_name}'


def test_evaluate_runtime_configuration_reads_temporary_overrides(main_module, isolated_env):
    """_evaluate_runtime_configuration must see TemporaryEnvironmentVariables values."""
    temporary = isolated_env
    temporary['workload'] = 'windows_vm'
    temporary['run_type'] = 'test_ci'

    with patch.object(main_module, 'Workloads') as mock_workloads:
        runtime = main_module._evaluate_runtime_configuration()

    assert runtime['workload'] == 'windows_vm'
    assert runtime['run_type'] == 'test_ci'
    assert runtime['is_benchmark_runner_workload'] is True
    assert 'benchmark_runner_workload' not in runtime
    # Evaluation must not construct workloads (side effects deferred to dispatch)
    mock_workloads.assert_not_called()


def test_evaluate_refreshes_workload_derived_fields(main_module, isolated_env):
    """Temporary workload override must refresh namespace/storage/artifacts, not only dispatch."""
    temporary = isolated_env
    # Stale derived values that must be recomputed from the temporary workload
    temporary['workload'] = 'clusterbuster'
    temporary['run_type'] = 'test_ci'
    temporary['namespace'] = 'benchmark-runner'
    temporary['storage_type'] = 'odf'
    temporary['odf_pvc'] = True
    temporary['run_artifacts_path'] = '/tmp/stale-empty-workload-path'

    main_module._evaluate_runtime_configuration()

    assert temporary['namespace'] == 'clusterbuster'
    assert 'storage_type' not in temporary  # not derived for clusterbuster; stale value cleared
    assert temporary['run_artifacts_path'].startswith(
        os.path.join(temporary['run_artifacts'], 'clusterbuster-')
    )


def test_evaluate_refreshes_ephemeral_storage_from_workload(main_module, isolated_env):
    """Workload suffix _ephemeral must recompute storage_type and odf_pvc."""
    temporary = isolated_env
    temporary['workload'] = 'vdbench_pod_ephemeral'
    temporary['run_type'] = 'test_ci'
    temporary['namespace'] = 'wrong'
    temporary['odf_pvc'] = True
    temporary['storage_type'] = 'odf'

    main_module._evaluate_runtime_configuration()

    assert temporary['namespace'] == 'benchmark-runner'
    assert temporary['storage_type'] == 'ephemeral'
    assert temporary['odf_pvc'] is False


def test_explicit_namespace_overrides_workload_mapping(main_module, isolated_env):
    """Option A: NAMESPACE env/CLI wins over hard-coded workload_namespaces."""
    temporary = isolated_env
    temporary['workload'] = 'clusterbuster'
    temporary['run_type'] = 'test_ci'
    temporary['namespace'] = 'clusterbuster'

    with patch.dict(os.environ, {'NAMESPACE': 'my-custom-ns'}, clear=False):
        main_module._evaluate_runtime_configuration()

    assert temporary['namespace'] == 'my-custom-ns'


def test_main_dispatch_uses_temporary_workload_override(main_module, isolated_env):
    """
    Override via TemporaryEnvironmentVariables, then invoke main() — Workloads
    must be constructed and run for the temporary workload.
    """
    temporary = isolated_env
    temporary['workload'] = 'windows_vm'
    temporary['run_type'] = 'test_ci'

    with patch.object(main_module, 'Workloads') as mock_workloads:
        mock_instance = MagicMock()
        mock_instance.run.return_value = True
        mock_workloads.return_value = mock_instance

        main_module.main()

        mock_workloads.assert_called_once()
        mock_instance.run.assert_called_once()


def test_main_empty_workload_exits_without_temporary_override(main_module, isolated_env):
    """Empty workload still fails at main() invocation."""
    # isolated_env already clears workload
    with pytest.raises(SystemExit) as exc_info:
        main_module.main()
    assert exc_info.value.code == main_module.SYSTEM_EXIT_UNKNOWN_EXECUTION_TYPE


def test_main_empty_workload_with_runner_type_does_not_call_run_on_none(main_module, isolated_env):
    """runner_type alone must not dispatch .run() when workload is empty."""
    temporary = isolated_env
    temporary['runner_type'] = 'benchmark-runner'

    with patch.object(main_module, 'Workloads') as mock_workloads:
        with pytest.raises(SystemExit) as exc_info:
            main_module.main()
        assert exc_info.value.code == main_module.SYSTEM_EXIT_UNKNOWN_EXECUTION_TYPE
        mock_workloads.assert_not_called()


def test_evaluate_flags_false_when_ci_status_skips_workload_dispatch(main_module, isolated_env):
    """Non-empty ci_status must not set workload dispatch flags."""
    temporary = isolated_env
    temporary['workload'] = 'windows_vm'
    temporary['run_type'] = 'test_ci'
    temporary['ci_status'] = 'running'

    with patch.object(main_module, 'Workloads') as mock_workloads:
        runtime = main_module._evaluate_runtime_configuration()

    assert runtime['is_benchmark_runner_workload'] is False
    assert 'benchmark_runner_workload' not in runtime
    mock_workloads.assert_not_called()


def test_main_install_branch_does_not_construct_workload(main_module, isolated_env):
    """Non-workload branches must not construct Workloads (no ES/OC/LSO side effects)."""
    temporary = isolated_env
    temporary['workload'] = 'windows_vm'
    temporary['run_type'] = 'test_ci'
    temporary['install_ocp_version'] = '4.16.0'
    temporary['install_step'] = 'run_bare_metal_ocp_installer'

    with patch.object(main_module, 'Workloads') as mock_workloads:
        with patch.object(main_module, 'install_ocp_bare_metal') as mock_install:
            main_module.main()
            mock_install.assert_called_once_with(step='run_bare_metal_ocp_installer')
        mock_workloads.assert_not_called()


def test_main_azure_branch_does_not_construct_workload(main_module, isolated_env):
    """Azure cluster operation must not construct Workloads before that branch."""
    temporary = isolated_env
    temporary['workload'] = 'windows_vm'
    temporary['run_type'] = 'test_ci'
    temporary['azure_cluster_operation'] = 'START'

    with patch.object(main_module, 'Workloads') as mock_workloads:
        with patch.object(main_module, 'azure_cluster_operations') as mock_azure:
            main_module.main()
            mock_azure.assert_called_once_with('START')
        mock_workloads.assert_not_called()


def test_main_constructs_clusterbuster_for_temporary_override(main_module, isolated_env):
    """Temporary clusterbuster workload must construct ClusterBusterWorkloads at main() time."""
    temporary = isolated_env
    temporary['workload'] = 'clusterbuster'
    temporary['run_type'] = 'test_ci'

    with patch.object(main_module, 'ClusterBusterWorkloads') as mock_cb:
        mock_instance = MagicMock()
        mock_instance.run.return_value = True
        mock_cb.return_value = mock_instance

        with patch.object(main_module, 'Workloads') as mock_workloads:
            main_module.main()
            mock_workloads.assert_not_called()

        mock_cb.assert_called_once()
        mock_instance.run.assert_called_once()
