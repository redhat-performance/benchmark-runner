# How to use pre-commit

## Install pre-commit

If your distribution packages pre-commit, you can use the package
manager to install it; e. g. on RHEL/Fedora:

```
$ sudo dnf install pre-commit
$ pre-commit install
```

If not:

```
$ pip install pre-commit
$ pre-commit install
```

## Run on every commit

```
pre-commit run --all-files
```

### How to fix errors:

The list of checks run may be found [at top level in `.pre-commit-config.yaml`](../.pre-commit-config.yaml).

Some of the checks fix issues on their own, while others require
manual intervention to fix. If anything is fixed automatically, you
should review the changes and then commit them.

The one check that requires special consideration is
`check-yaml`. This check cannot check the template files that are the
source of truth, as those template files contain jinja2 constructs
that by themselves are not valid YAML. This check does test the [golden
files](../tests/unittest/benchmark_runner/common/workloads_flavors/golden_files). You
will need to determine which template file(s) is/are responsible for
the errors encountered and fix those, following the instructions in [../HOW_TO.md](../HOW_TO.md#add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job)
