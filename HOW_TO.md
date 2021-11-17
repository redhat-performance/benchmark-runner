# Benchmark-runner: How to?

_**Table of Contents**_

<!-- TOC -->
**Table of Contents**

- [Benchmark-runner: How to?](#benchmark-runner-how-to)
    - [Add new workload, modify parameters to workload, or change parameters for any CI job](#add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job)
    - [Add new benchmark operator workload to benchmark runner](#add-new-benchmark-operator-workload-to-benchmark-runner)
    - [Add workload to grafana dashboard](#add-workload-to-grafana-dashboard)
    - [Monitor and debug workload](#monitor-and-debug-workload)

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

You should never need to modify the golden files manually.

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
7. Create workload folder in each workload flavor [func_ci](benchmark_runner/benchmark_operator/workload_flavors/func_ci), [perf_ci](benchmark_runner/benchmark_operator/workload_flavors/perf_ci), [test_ci](benchmark_runner/benchmark_operator/workload_flavors/test_ci)
   1. For each workload folder:
      1. Add 'workload_data_template' for configured parameters and configure workload index name 'es_index_name' e.g. [stressng_data_template.yaml](benchmark_runner/benchmark_operator/workload_flavors/func_ci/stressng/stressng_data_template.yaml)
      2. Add workload Pod and VM CRD template inside [internal_data](benchmark_runner/benchmark_operator/workload_flavors/func_ci/stressng/internal_data)
8. Add workload folder path in [MANIFEST.in](MANIFEST.in), for each flavor 'func_ci', 'perf_ci', 'test_ci' add 2 paths: the workload path to 'workload_data_template.yaml' and path to 'internal_data' Pod and VM template yaml files
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
   1. Run workload through [main.py](/benchmark_runner/main/main.py)
      1. Need to configure all mandatory parameters in [environment_variables.py](benchmark_runner/main/environment_variables.py)
         1. `workloads` = e.g. stressng_pod
         2. `runner_path` = path to local cloned benchmark-operator (e.g. /home/user/)
            1. git clone https://github.com/cloud-bulldozer/benchmark-operator  (inside 'runner_path')
         3. `kubeadmin_password`
         4. `pin_node_benchmark_operator` - benchmark-operator node selector
         5. `pin_node1` - workload first node selector
         6. `pin_node2` - workload second node selector (for workload with client server e.g. uperf)
         7. `elasticsearch` - elasticsearch url without http prefix
         8. `elasticsearch_port` - elasticsearch port
      2. Run [main.py](/benchmark_runner/main/main.py)
      3. Verify that benchmark-runner run the workload
   2. Run workload through integration/unittest tests [using pytest]
      1. Need to configure all mandatory parameters [test_environment_variables.py](tests/integration/benchmark_runner/test_environment_variables.py)
         1. `runner_path` = path to local cloned benchmark-operator (e.g. /home/user/)
            1. git clone https://github.com/cloud-bulldozer/benchmark-operator (inside 'runner_path')
         2. `kubeadmin_password`
         3. `pin_node1` - workload first node selector
         4. `elasticsearch` - elasticsearch url without http prefix
         5. `elasticsearch_port` - elasticsearch port
      2. Run the selected test using pytest [test_oc.py](/tests/integration/benchmark_runner/common/oc/test_oc.py)
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
