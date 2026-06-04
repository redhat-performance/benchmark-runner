# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AI Attribution

All AI-generated or AI-assisted contributions must be marked per project policy:

- **Commit messages**: Include `Assisted-by: Claude Code` as a trailer
- **PR review replies**: Prefix with `[Claude Code]` when replying to reviewer comments (CodeRabbit, human reviewers)
- **PR descriptions**: Include `🤖 Assisted-by: Claude Code` at the bottom of the description
- **No internal links**: Do not include internal Jira URLs in upstream public PRs — use issue key only if needed (e.g., `PERFSCALE-1234`)

## Build and Test Commands

```bash
# Run golden file tests (primary test suite)
make test_golden_files

# Regenerate golden files after template changes
make golden_files

# Run both
make all

# Run all unit tests (required before pushing any commit)
PYTHONPATH=. python3 -m pytest -v tests/unittest/

# Run specific test
PYTHONPATH=. python3 -m pytest -v tests/unittest/benchmark_runner/common/template_operations/test_golden_files.py

# Run the benchmark workload
python -m benchmark_runner.main.main
```

**Important**: Always run `PYTHONPATH=. python3 -m pytest -v tests/unittest/` before pushing any commit. All unit tests must pass.

Pre-commit hooks run automatically on commit (rh-pre-commit, YAML/JSON validation, trailing whitespace, private key detection).

**Important**: Any change to files under `benchmark_runner/common/template_operations/` (templates, data files, or the template engine itself) requires running `make golden_files` followed by `make test_golden_files` before committing.

**Integration test environment**: The CI integration test cluster does not have ODF installed. Integration tests must use ephemeral storage (emptyDir/emptyDisk) only. ODF-dependent tests should be marked with `@pytest.mark.skip(reason="Disable ODF")`.

## Architecture

### Entry Point

`benchmark_runner/main/main.py` dispatches to:
- `Workloads().run()` — standard workloads (hammerdb, vdbench, stressng, uperf, bootstorm, windows, winmssql)
- `ClusterBusterWorkloads().run()` — clusterbuster
- `KrknHubWorkloads().run()` — krknhub chaos testing

### Workload Class Hierarchy

```
WorkloadsOperations (base — ES upload, Prometheus, OC client, template generation)
├── BootstormVM (parallel VM lifecycle, _finalize_vm pattern)
│   ├── WindowsVM
│   └── WinMSSQLVM (parallel HammerDB on Windows MSSQL VMs)
├── HammerdbPod / HammerdbVm
├── StressngPod / StressngVm
├── UperfPod / UperfVm
└── VdbenchPod / VdbenchVm
```

### Workload Dispatch

`workloads/workloads.py` dynamically imports the workload module from the `WORKLOAD` env var name (e.g., `hammerdb_vm_mssql_lso` → `hammerdb_vm` module), finds the matching class via `inspect.getmembers()`, and calls `.run()`.

### Template System

- Templates live in `common/template_operations/templates/<workload>/internal_data/`
- `*_data_template.yaml` — configuration params (shared, per-run_type)
- `*_vm_template.yaml` / `*_pod_template.yaml` — Kubernetes resource templates (Jinja2)
- `TemplateOperations.generate_yamls()` renders templates into `run_artifacts_path/`
- After changing templates, regenerate golden files: `make golden_files`

### Configuration

`benchmark_runner/main/environment_variables.py` — all config via env vars or `--cli-args`. Key vars: `WORKLOAD`, `SCALE`, `SCALE_NODES`, `ELASTICSEARCH`, `ENABLE_PROMETHEUS_SNAPSHOT`, `DELETE_ALL`, `RUN_TYPE`.

For local development, edit defaults in `environment_variables.py` (do NOT commit local defaults like kubeadmin passwords, ES hosts, scale nodes).

## Key Constraints

### Multiprocessing and SSL

Workloads using `multiprocessing.Process` (e.g., `WinMSSQLVM`, `BootstormVM` scale) must not make HTTPS calls (Elasticsearch, Prometheus) in the main process before spawning child processes that also need HTTPS. OpenSSL state corrupts across process boundaries causing SIGSEGV (exitcode=-11).

**Safe pattern**: Either do all HTTPS in child processes (like `BootstormVM._finalize_vm`), or do all HTTPS in the main process after child processes complete (like `WinMSSQLVM._upload_results`).

### Golden Files

Any change to templates or environment variables that affects generated YAMLs will break golden file tests. Always run `make golden_files` to regenerate, then `make test_golden_files` to verify.
