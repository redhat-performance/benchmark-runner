# Benchmark-runner: How to?

_**Table of Contents**_

<!-- TOC -->
**Table of Contents**

- [Benchmark-runner: How to?](#benchmark-runner-how-to)
    - [Add new workload, modify parameters to workload, or change parameters for any CI job](#add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job)
    - [Add new benchmark operator workload to benchmark runner](#add-new-benchmark-operator-workload-to-benchmark-runner)
    - [Add workload to grafana dashboard](#add-workload-to-grafana-dashboard)
        - [Data template](#data-template)
    - [Monitor and debug workload](#monitor-and-debug-workload)
    - [Determine the version of benchmark-runner in the current container image](#determine-the-version-of-benchmark-runner-in-the-current-container-image)

<!-- /TOC -->

## Add new workload, modify parameters to workload, or change parameters for any CI job

The unit tests include a check to ensure that the generated .yaml
files do not inadvertently change.  This check, located in
`tests/unittest/benchmark_runner/regression/test_golden_files.py`,
compares these files against expected files found in
`tests/unittest/benchmark_runner/regression/golden_files` and fails if
any golden files have been added, modified, or removed.

_*If you add or modify any YAML files, you must run the following commands:*_

```
PYTHONPATH=. python3 tests/unittest/benchmark_runner/regression/generate_golden_files.py
git add tests/unittest/benchmark_runner/regression/golden_files
git commit -m"Update golden files"
```

If you remove any YAML files, you must identify the changed files and
`git rm` them before committing the result.

The check is run automatically as part of the unit tests; if you want
to run it manually, you can do so as follows.  The test should take
only a few seconds to run.

```
$ PYTHONPATH=. python3 -m pytest -v
tests/unittest/benchmark_runner/regression/
============================== test session starts ===============================
platform linux -- Python 3.9.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/rkrawitz/sandbox/benchmark-runner
plugins: typeguard-2.10.0, venv-0.2
collected 1 item

tests/unittest/benchmark_runner/regression/test_golden_files.py::test_golden_files PASSED [100%]

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
4. Open [benchmark_operator_workloads.py](benchmark_runner/benchmark_operator/benchmark_operator_workloads.py)
5. Create new `workload method` for Pod and VM under `Workloads` section in [benchmark_operator_workloads.py](benchmark_runner/benchmark_operator/benchmark_operator_workloads.py).
   It can be duplicated from existing workload method: `def stressng_pod` or `def stressng_vm` and customized workload run steps accordingly
6. Add workload method name (workload_pod/workload_vm) to environment_variables_dict['workloads'] in [environment_variables.py](benchmark_runner/main/environment_variables.py)
7. Create workload folder in the [templates](benchmark_runner/benchmark_operator/workload_flavors/templates) directory.  Create the following files in that directory:
   1. workload_data_template for configuration parameters, e. g. [stressng_data_template.yaml](benchmark_runner/benchmark_operator/workload_flavors/templates/stressng/stressng_data_template.yaml).  The data template is structured as discussed [below](#data-template).
   2. workload pod and VM custom resource template inside [internal_data](benchmark_runner/benchmark_operator/workload_flavors/templates/stressng/internal_data)
8. Add workload folder path in [MANIFEST.in](MANIFEST.in), add 2 paths: the workload path to 'workload_data_template.yaml' and path to 'internal_data' Pod and VM template yaml files
9. Add tests for all new methods you write under `tests/integration`.
10. Update the golden unit test files as described [above](#add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job)
11. For test and debug workload, need to configure [environment_variables.py](benchmark_runner/main/environment_variables.py)
   1. Fill parameters: workload, kubeadmin_password, pin_node_benchmark_operator, pin_node1, pin_node2, elasticsearch, elasticsearch_port
   2. Run [main.py](/benchmark_runner/main/main.py)  and verify that the workload run correctly
   3. The workload can be monitored and checked through 'current run' folder inside the run workload flavor (default flavor: 'test_ci')
12. Open Kibana url and verify workload index populate with data:
   1. Create the workload index: Kibana -> Hamburger tab -> Stack Management -> Index patterns -> Create index pattern -> workload-results -> timestamp -> Done
   2. Verify workload-results index is populated: Kibana -> Hamburger tab -> Discover -> workload-results (index) -> verify that there is a new data

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
   2. Create(+) -> import -> paste [benchmark-runner-report.json](grafana/benchmark-runner-report.json) -> Load
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

Boilerplate data that is independent of workload has been moved to `common.yaml` at top level in the `templates` directory.

## Monitor and debug workload
You will need a copy of `benchmark-operator`, and RUNNER_PATH set in
the environment to point to the directory *above* the clone.

1. git clone https://github.com/redhat-performance/benchmark-runner
2. export RUNNER_PATH=$HOME
3. git clone https://github.com/cloud-bulldozer/benchmark-operator "$RUNNER_PATH/benchmark-operator"
4. cd benchmark-runner
5. *It is strongly recommended that you create a Python virtual
   environment for this work*:
```
   $ python3 -m venv venv
   $ . venv/bin/activate
   $ # For development purposes, you will need to install additional packages
   $ # This is not needed for production use and hence is not in requirements.txt
   $ pip3 install setuptools_rust pytest moto mock flake8 pytest-cov
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
6. There are 2 options to run workload:
   1. Run workload through [main.py](/benchmark_runner/main/main.py)
	  1. Configure mandatory parameters.  You may do so by use of
         command line arguments (by means of `-Dvariable=value`) or environment variables.  The
         following parameters must be configured.
		 1. `workload` = name of the workload (`-Dworkload` on the commandline,
            or `$WORKLOAD` in the environment)
         2. `runner_path` = path to parent of local cloned
            benchmark-operator (e.g. `/home/user` if the actual clone
            is `/home/user/benchmark-operator`).  (`-Drunner_path` or `$RUNNER_PATH`)
            1. `cd $RUNNER_PATH && git clone https://github.com/cloud-bulldozer/benchmark-operator`  (inside 'runner_path')
         3. `elasticsearch` - elasticsearch url without http prefix or
            port (`-Delasticsearch` or `$ELASTICSEARCH`).  This is
            required unless you choose not to use metrics (see
            `system_metrics` below).
         4. `elasticsearch_port` - elasticsearch port
            (`-Delasticsearch_port` or `$ELASTICSEARCH_PORT`).  Needed
            unless you choose not to use system metrics.
         5. `kubeadmin_password` = password (if required) to access
            your cluster.  This is required in most cases; if your
            cluster was installed via the UPI installer, it may not
            be (`-Dkubeadmin_password` or `$KUBEADMIN_PASSWORD`)
	  2. Configure any optional parameters
         1. `pin_node_benchmark_operator` - benchmark-operator node
            selector (`-Dpin_node_benchmark_operator` or `$PIN_NODE_BENCHMARK_OPERATOR`)
         2. `pin_node1` - workload first node selector (`-Dpin_node1`
            or `$PIN_NODE1`)
         3. `pin_node2` - workload second node selector, for
            client-server workloads such as uperf (`-Dpin_node1`
            or `$PIN_NODE1`)
		 4. `ocs_pvc` - Boolean, whether to use OCS or
            ephemeral storage, for workloads using storage
            (e. g. hammerdb).  Must be either `true` or `false`
            (`-Docs_pvc` or `$OCS_PVC`).  Default `true` (use OCS).
		 5. `system_metrics` - Boolean, whether to store system
            metrics in Elasticsearch (`-Dsystem_metrics`,
            `$SYSTEM_METRICS`).  Default `true`.
      3. Run [main.py](/benchmark_runner/main/main.py)
      4. Verify that benchmark-runner run the workload
   2. Run workload through integration/unittest tests [using pytest]
      1. Configure all parameters
      2. Run the selected test using pytest [test_oc.py](/tests/integration/benchmark_runner/common/oc/test_oc.py)
         1. Enable pytest in Pycharm: Configure pytest in Pycharm -> File -> settings -> tools -> Python integrated tools -> Testing -> pytest -> ok), and run the selected test
         2. Run pytest through terminal: `python3 -m pytest -v tests/`
            (`pip3 install pytest` if not already installed)
7. There are three separate flavors of test: `test-ci`, `func-ci`, and
   `perf-ci`.  These are intended for testing, automated functional
   testing of benchmark-runner itself, and the performance measurement
   itself.  The default is `test-ci`.  These are distinct from any
   particular test environments; as noted above under
   [#Add-new-benchmark-operator-workload-to-benchmark-runner](adding
   new workloads), they also use different template files.  The flavor
   can be selected via `-Drun_type` on the command line or the environment variable `$RUN_TYPE`.

   *When using a shared ElasticSearch instance (not documented here),
   it's important not to use the `perf-ci` run type*.  This will
   contaminate the index of the shared ElasticSearch database.  There
   are two ways to use the `perf-ci` flavor safely:

   1. Set `system_metrics` to `false` when running the workload.
   2. Use a different, private ElasticSearch instance.

## Determine the version of benchmark-runner in the current container image

The version of [benchmark-runner on
PyPi](https://pypi.org/project/benchmark-runner/) should match the
version in `setup.py`, and the [container
image version](https://quay.io/repository/ebattat/benchmark-runner?tab=tags)
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
# podman rmi quay.io/ebattat/benchmark-runner
# podman rmi quay.io/ebattat/benchmark-runner
Untagged: quay.io/ebattat/benchmark-runner:latest
# podman run --rm -it quay.io/ebattat/benchmark-runner:latest /bin/bash
Trying to pull quay.io/ebattat/benchmark-runner:latest...
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
