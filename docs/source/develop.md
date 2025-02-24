
## Benchmark-runner: How to develop ?

_**Table of Contents**_

<!-- TOC -->
- [Benchmark-runner: How to?](#benchmark-runner-how-to)
    - [Add any new Python code](#add-any-new-python-code)
    - [Run Benchmark runner from terminal](#run-benchmark-runner-from-terminal)
    - [Add new benchmark operator workload to benchmark runner](#add-new-benchmark-operator-workload-to-benchmark-runner)
    - [Add workload to grafana dashboard](#add-workload-to-grafana-dashboard)
        - [Data template](#data-template)
    - [Monitor and debug workload](#monitor-and-debug-workload)
    - [Determine the version of benchmark-runner in the current container image](#determine-the-version-of-benchmark-runner-in-the-current-container-image)

<!-- /TOC -->

## Add any new Python code

If you need to add any new Python  code in any directory, you *must*
create an `__init__.py` file in that directory if it does not already
exist.  If you don't, that code will not be propagated into the
release package.

To check this, run the following command:

```
$ ls -l $(git ls-files |grep '\.py$' |grep -v '/__init__\.py$' | xargs dirname | sort -n |uniq | sed 's,$,/__init__.py,') 2>&1 >/dev/null
```

If there is any output, e.g.

```
ls: cannot access 'tests/unittest/benchmark_runner/common/template_operations/__init__.py': No such file or directory
```

you need to create an empty file by that name and `git add` it.

## Run Benchmark runner from terminal

```
PYTHONPATH=. python benchmark_runner/main/main.py
```

## Add new workload, modify parameters to workload, or change parameters for any CI job

The unit tests include a check to ensure that the generated .yaml
files do not inadvertently change.  This check, located in
`tests/unittest/benchmark_runner/common/templates/test_golden_files.py`,
compares these files against expected files found in
`tests/unittest/benchmark_runner/common/workloads_flavors/golden_files` and fails if
any golden files have been added, modified, or removed.

_*If you add or modify any YAML files, you must run the following commands:*_

```
PYTHONPATH=. python3 tests/unittest/benchmark_runner/common/template_operations/generate_golden_files.py
git add tests/unittest/benchmark_runner/common/templates/golden_files
git commit -m "Update golden files"
```

If you remove any YAML files, you must identify the changed files and
`git rm` them before committing the result.

The check is run automatically as part of the unit tests; if you want
to run it manually, you can do so as follows.  The test should take
only a few seconds to run.

```
$ PYTHONPATH=. python3 -m pytest -v tests/unittest/benchmark_runner/common/template_operations/
============================== test session starts ===============================
platform linux -- Python 3.9.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/rkrawitz/sandbox/benchmark-runner
plugins: typeguard-2.10.0, venv-0.2
collected 1 item

tests/unittest/benchmark_runner/common/templates/test_golden_files.py::test_golden_files PASSED [100%]

=============================== 1 passed in 1.85s ================================
```

This test uses synthetic environment variables that you do not need to
modify, and you should never have to manually modify the golden files
except to manually remove any that are no longer required.

Examples of changes that require updating the golden files:

* Adding, removing, or changing any YAML file or template under `benchmark_runner`
* Adding new workload or removing an existing one
* Adding new CI flavor or removing an existing one

If the test fails, it will report lists for files that failed
comparison check, missing, unexpected files that are present, or files
that could not be compared for some reason.  If files have been
changed and you verify that the changes are correct, you need to `git
add` the appropriate files as discussed above (usually you can just
`git add` the golden_files directory).  If you have remove .yaml
files, you must manually `git rm` them.

You should /never/ modify the golden files manually.

## Add new benchmark operator workload to benchmark runner
This section also applies to modifying an existing workload, including
any template .yaml files.

1. git clone https://github.com/redhat-performance/benchmark-runner
2. cd benchmark-runner
3. Install prerequisites (these commands assume RHEL/CentOS/Fedora):
    - dnf install make
    - dnf install python3-pip
4. Open [benchmark_runner/benchmark_operator/benchmark_operator_workloads.py](benchmark_runner/benchmark_operator/benchmark_operator_workloads.py)
5. Create new `workload method` for Pod and VM under `BenchmarkOperatorWorkloads class` section in [benchmark_runner/benchmark_operator/benchmark_operator_workloads.py](benchmark_runner/benchmark_operator/benchmark_operator_workloads.py).
   It can be duplicated from existing workload method: `def stressng_pod` or `def stressng_vm` and customized workload run steps accordingly
6. Create dedicated `<workload> class` WorkloadPod or WorkloadVM in dedicated module `<workload>_pod.py` or `<workload>_vm.py` and customized workload run steps accordingly e.g. [benchmark_runner/benchmark_operator/stressng_pod.py](benchmark_runner/benchmark_operator/stressng_pod.py)
7. Add workload method name (workload_pod/workload_vm) to environment_variables_dict['workloads'] in [benchmark_runner/main/environment_variables.py](benchmark_runner/main/environment_variables.py)
8. Create workload folder in the [benchmark_runner/common/template_operations/templates](benchmark_runner/common/template_operations/templates) directory.  Create the following files in that directory:
    1. Add workload_data_template for configuration parameters, e.g. [benchmark_runner/common/template_operations/templates/stressng/stressng_data_template.yaml](benchmark_runner/common/template_operations/templates/stressng/stressng_data_template.yaml).
    2. The data template is structured as discussed [below](#data-template).
    3. Add workload pod and VM custom resource template inside [benchmark_runner/common/template_operations/templates/stressng/internal_data](benchmark_runner/common/template_operations/templates/stressng/internal_data)
9. Add workload folder path in [MANIFEST.in](MANIFEST.in), add 2 paths: the workload path to 'workload_data_template.yaml' and path to 'internal_data' Pod and VM template yaml files. e.g.
   ```
     include benchmark_runner/common/template_operations/templates/stressng/*.yaml
     include benchmark_runner/common/template_operations/templates/stressng/internal_data/*.yaml
   ```
10. Add tests for all new methods you write under `tests/integration`.
11. Update the golden unit test files as described [above](#add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job)
12. For test and debug workload, need to configure [benchmark_runner/main/environment_variables.py](benchmark_runner/main/environment_variables.py).  You may alternatively set these variables in the environment or pass command line options, which in all cases are `--lowercase-option` where the name of the environment variable is lower cased.  For example:
   ```
   python3 benchmark_runner/main/main.py --runner-path=/parent/of/benchmark-runner --workload=stressng_pod --kubeadmin-password=password --pin-node-benchmark-operator=worker-0 --pin-node1=worker-1 --pin-node2=worker-2 --elasticsearch=elasticsearch_port --elasticsearch-port=80
   ```
   or
   ```
	RUNNER_PATH=/parent/of/benchmark-runner WORKLOAD=stressng_pod KUBEADMIN_PASSWORD=password PIN_NODE_BENCHMARK_OPERATOR=worker-0 PIN_NODE1=worker-1 PIN_NODE2=worker-2 ELASTICSEARCH=elasticsearch_port ELASTICSEARCH_PORT=80 python3 benchmark_runner/main/main.py
   ```
13. Fill parameters: workload, kubeadmin_password, pin_node_benchmark_operator, pin_node1, pin_node2, elasticsearch, elasticsearch_port
14. Run [/benchmark_runner/main/main.py](/benchmark_runner/main/main.py)  and verify that the workload runs correctly.
15. The workload can be monitored and checked through 'current run' folder inside the run workload flavor (default flavor: 'test_ci')
16. Open Kibana url and verify workload index populate with data:
17. Create the workload index: Kibana -> Hamburger tab -> Stack Management -> Index patterns -> Create index pattern -> workload-results -> timestamp -> Done
18. Verify workload-results index is populated: Kibana -> Hamburger tab -> Discover -> workload-results (index) -> verify that there is a new data

## Add workload to grafana dashboard
1. Create Elasticsearch data source
    1. Grafana -> Configuration(setting icon) -> Data source -> add data source -> Elasticsearch
        1. Name: Elasticsearch-workload-results
        2. URL: http://elasticsearch.com:port
        3. Index name: workload-results
        4. Time field name: timestamp (remove @)
        5. Version: 7.10+
        6. Save & test
2. Open grafana dashboard benchmark-runner-report:
    1. Open grafana
    2. Create(+) -> import -> paste [grafana/benchmark-runner-report.json](grafana/benchmark-runner-report.json) -> Load
    3. Create panel from scratch or duplicate existing on (stressng/uperf)
    4. Configure the workload related metrics
    5. Save dashboard -> share -> Export -> view json -> Copy to clipboard -> override existing one [benchmark-runner-report.json](grafana/benchmark-runner-report.json)

### Data template

The data template is a structured YAML file, organized as follows:
```
shared_data:
  <shared_data>
run_type_data:
  perf_ci:
    <perf_ci_data>
  func_ci:
    <func_ci_data>
  default:
    <data for other run types>
kind_data:
  vm:
    <vm_data>
	run_type_data:
	  perf_ci:
	    <vm_data_for_perf_ci>
	  default:
	    <vm_data_for_other_run_types>
  default:
    <data_for_other_kinds>
	run_type_data:
	  perf_ci:
	    <other_kind_data_for_perf_ci>
	  default:
	    <other_kind_data_for_other_run_types>
```

The `shared_data` section is mandatory, but all other sections are optional.  Generally, the `run_type` data for `func_ci` and `test_ci` is identical, so only `perf_ci` data need be specified, and the otherwise shared data under `default`.  Similarly, the `kata` and `pod` kinds use identical data, and only vm data need be specified separately.

Boilerplate data that is independent of workload has been moved to `common_template.yaml` at top level in the `templates` directory.

## Monitor and debug workload
1. git clone https://github.com/redhat-performance/benchmark-runner
2. cd benchmark-runner
3. *It is strongly recommended that you create a Python virtual
   environment for this work*:
```
   $ python3 -m venv venv
   $ . venv/bin/activate
   $ pip3 install -r requirements.txt
```
When you are finished working, you should deactivate your virtual
environment:
```
   $ deactivate
```
If you wish to resume work, you merely need to reactivate your
virtual environment:
```
   $ . venv/bin/activate
```
4. There are 2 options to run workload:
    1. Run workload through [/benchmark_runner/main/main.py](/benchmark_runner/main/main.py)
        1. Need to configure all mandatory parameters in [benchmark_runner/main/environment_variables.py](benchmark_runner/main/environment_variables.py)
            1. `workloads` = e.g. stressng_pod
            2. `runner_path` = path to local cloned benchmark-operator (e.g. /home/user/)
                1. git clone -b v1.0.3 https://github.com/cloud-bulldozer/benchmark-operator  (inside 'runner_path')
            3. `kubeadmin_password`
            4. `pin_node_benchmark_operator` - benchmark-operator node selector
            5. `pin_node1` - workload first node selector
            6. `pin_node2` - workload second node selector (for workload with client server e.g. uperf)
            7. `elasticsearch` - elasticsearch url without http prefix
            8. `elasticsearch_port` - elasticsearch port
        2. Run [/benchmark_runner/main/main.py](/benchmark_runner/main/main.py)
        3. Verify that benchmark-runner run the workload
    2. Run workload through integration/unittest tests [using pytest]
        1. Need to configure all mandatory parameters [tests/integration/benchmark_runner/test_environment_variables.py](tests/integration/benchmark_runner/test_environment_variables.py)
            1. `runner_path` = path to local cloned benchmark-operator (e.g. /home/user/)
                1. git clone -b v1.0.3 https://github.com/cloud-bulldozer/benchmark-operator (inside 'runner_path')
            2. `kubeadmin_password`
            3. `pin_node1` - workload first node selector
            4. `elasticsearch` - elasticsearch url without http prefix
            5. `elasticsearch_port` - elasticsearch port
        2. Run the selected test using pytest [/tests/integration/benchmark_runner/common/oc/test_oc.py](/tests/integration/benchmark_runner/common/oc/test_oc.py)
            1. Enable pytest in Pycharm: Configure pytest in Pycharm -> File -> settings -> tools -> Python integrated tools -> Testing -> pytest -> ok), and run the selected test
            2. Run pytest through terminal: python -m pytest -v tests/ (pip install pytest)
5. There are three separate flavors of test: `test-ci`, `func-ci`, and
   `perf-ci`.  These are intended for testing, automated functional
   testing of benchmark-runner itself, and the performance measurement
   itself.  The default is `test-ci`.  These are distinct from any
   particular test environments; as noted above under
   [#Add-new-benchmark-operator-workload-to-benchmark-runner](adding
   new workloads), they also use different template files.  The flavor
   can be selected via the environment variable `RUN_TYPE`.

   *When using a shared ElasticSearch instance (not documented here),
   it's important not to use the `perf-ci` run type*.  This will
   contaminate the index of the shared ElasticSearch database.  There
   are two ways to use the `perf-ci` flavor safely:

    1. Set `STOP_WHEN_WORKLOAD_FINISH=True` in the environment when
       running the workload.  This is case sensitive.
    2. Use a different, private ElasticSearch instance.

## Determine the version of benchmark-runner in the current container image

The version of [https://pypi.org/project/benchmark-runner/](https://pypi.org/project/benchmark-runner/) should match the
version in `setup.py`, and the [https://quay.io/repository/benchmark-runner/benchmark-runner?tab=tags](https://quay.io/repository/benchmark-runner/benchmark-runner?tab=tags)
should also match that version.  However, if the version on PyPi is
not updated quickly enough, the container image may remain stale.
This may result in unexpected errors.

To check the version of benchmark-runner in the container image, it's
necessary to exec into the latest container image and check the
version with pip:

```
# # If the command below results in an error, you may need to
# # podman ps -a |grep benchmark-runner
# # podman rm $(podman ps -a |grep benchmark-runner |awk '{print $1}')
# # and repeat the command
# podman rmi quay.io/benchmark-runner/benchmark-runner
# podman rmi quay.io/benchmark-runner/benchmark-runner
Untagged: quay.io/benchmark-runner/benchmark-runner:latest
# podman run --rm -it quay.io/benchmark-runner/benchmark-runner:latest /bin/bash
Trying to pull quay.io/benchmark-runner/benchmark-runner:latest...
Getting image source signatures
...
[root@ede12c01460d /]# pip show benchmark-runner
Name: benchmark-runner
Version: 1.0.195
Summary: Benchmark Runner Tool
...
[root@ede12c01460d /]# cd /usr/local/lib/python3.9/site-packages/benchmark_runner
```

_* If the version reported via pip does not match the expected version, the image build did not happen correctly.  Please contact the development team for assistance. *_
