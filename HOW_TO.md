# Benchmark-runner: How to?

_**Table of Contents**_

<!-- TOC -->
- [Add new benchmark operator workload to benchmark runner](#add-new-benchmark-operator-workload-to-benchmark-runner)
- [Add workload to grafana dashboard](#add-workload-to-grafana-dashboard)
- [Monitor and debug workload](#monitor-and-debug-workload)

<!-- /TOC -->

## Add new benchmark operator workload to benchmark runner
1. git clone https://github.com/redhat-performance/benchmark-runner
2. cd benchmark-runner
3. Open [benchmark_operator_workloads.py](benchmark_runner/benchmark_operator/benchmark_operator_workloads.py)
4. Create new `workload method` for Pod and VM under `Workloads` section in [benchmark_operator_workloads.py](benchmark_runner/benchmark_operator/benchmark_operator_workloads.py).
   It can be duplicated from existing workload method: `def stressng_pod` or `def stressng_vm` and customized workload run steps accordingly
5. Add workload method name (workload_pod/workload_vm) to environment_variables_dict['workloads'] in [environment_variables.py](benchmark_runner/main/environment_variables.py)
6. Create workload folder in each workload flavor [func_ci](benchmark_runner/benchmark_operator/workload_flavors/func_ci), [perf_ci](benchmark_runner/benchmark_operator/workload_flavors/perf_ci), [test_ci](benchmark_runner/benchmark_operator/workload_flavors/test_ci)
   1. For each workload folder:
      1. Add 'workload_data_template' for configured parameters and configure workload index name 'es_index_name' e.g. [stressng_data_template.yaml](benchmark_runner/benchmark_operator/workload_flavors/func_ci/stressng/stressng_data_template.yaml)
      2. Add workload Pod and VM CRD template inside [internal_data](benchmark_runner/benchmark_operator/workload_flavors/func_ci/stressng/internal_data)
7. Add workload folder path in [MANIFEST.in](MANIFEST.in), for each flavor 'func_ci', 'perf_ci', 'test_ci' add 2 paths: the workload path to 'workload_data_template.yaml' and path to 'internal_data' Pod and VM template yaml files
8. For test and debug workload, need to configure [environment_variables.py](benchmark_runner/main/environment_variables.py)
   1. Fill parameters: workload, kubeadmin_password, pin_node_benchmark_operator, pin_node1, pin_node2, elasticsearch, elasticsearch_port 
   2. Run [main.py](/benchmark_runner/main/main.py)  and verify that the workload run correctly
   3. The workload can be monitored and checked through 'current run' folder inside the run workload flavor (default flavor: 'test_ci')
9. Open Kibana url and verify workload index populate with data:
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
3. There are 2 options to run workload: 
   1. Run workload through [main.py](/benchmark_runner/main/main.py) 
      1. Need to configure all mandatory parameters in [environment_variables.py](benchmark_runner/main/environment_variables.py)
         1. `workloads` = e.g. stressng_pod
         2. `runner_path` = path to local cloned benchmark-operator (e.g. /home/user/)
         3. `kubeadmin_password`
         4. `pin_node_benchmark_operator` - benchmark-operator node selector
         5. `pin_node1` - workload first node selector
         6. `pin_node2` - workload second node selector (for workload with client server e.g. uperf)
         7. `elasticsearch` - elasticsearch url without http prefix
         8. `elasticsearch_port`
      2. Run [main.py](/benchmark_runner/main/main.py) 
      3. Verify that benchmark-runner run the workload
   2. Run workload through integration/unittest tests [using pytest]
      1. Need to configure all mandatory parameters [test_environment_variables.py](tests/integration/benchmark_runner/test_environment_variables.py)
         1. `runner_path` = path to local cloned benchmark-operator (e.g. /home/user/)
         2. `kubeadmin_password`
         3. `pin_node1` - workload first node selector
         4. `elasticsearch` - elasticsearch url without http prefix
         5. `elasticsearch_port`
      2. Run the selected test using pytest [test_oc.py](/tests/integration/benchmark_runner/common/oc/test_oc.py)
         1. Enable pytest in Pycharm: Configure pytest in Pycharm -> File -> settings -> tools -> Python integrated tools -> Testing -> pytest -> ok), and run the selected test 
         2. Run pytest through terminal: python -m pytest -v tests/ (pip install pytest) 
