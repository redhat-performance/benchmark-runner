
## How to add new custom workload to benchmark-runner ?

This section also applies to modifying an existing workload, including
any template .yaml files.
1. git clone https://github.com/redhat-performance/benchmark-runner
2. cd benchmark-runner
3. Install prerequisites (these commands assume RHEL/CentOS/Fedora):
    - dnf install python3-pip
4. Create workload Dockerfile, example:
   ```
   FROM quay.io/centos/centos:stream8
   Shell/Python that run workload
   Result in Json (redirect to stdout)
   Wrap Json output with begin/end workload stamp
   start_stamp='@@~@@START-WORKLOAD@@~@@'
   end_stamp='@@~@@END-WORKLOAD@@~@@'
   ```
5. Upload image to quay.io
6. Create workload pod yaml, example:
   ```
   kind: Pod
   apiVersion: v1
   metadata:
   name: vdbench-pod
   namespace: default
   spec:
   containers:
   - name: vdbench-pod
     namespace: default
     image: quay.io/ebattat/centos-stream8-vdbench5.04.07-pod:latest
     imagePullPolicy: "Always"
     volumeMounts:
      - name: vdbench-pvc
        mountPath: "/workload"
        env:
      - name: BLOCK_SIZES
   ```
   output pod example:
   ```
   '@@~@@START-WORKLOAD@@~@@'
   {
   "workload": "Name",
   "Run": "1",
   "Thread": 1,
   "IOPS": "30"
   }
   '@@~@@END-WORKLOAD@@~@@'
   ```
7. Benchmark-runner - add workload Template in [benchmark_runner/common/template_operations/templates](benchmark_runner/common/template_operations/templates)
    1. Create workload directory for example [benchmark_runner/common/template_operations/templates/vdbench](benchmark_runner/common/template_operations/templates/vdbench)
    2. Create custom_data_template.yaml for example [benchmark_runner/common/template_operations/templates/vdbench/vdbench_data_template.yaml](benchmark_runner/common/template_operations/templates/vdbench/vdbench_data_template.yaml).  This should include all data that should be replaced by Jinja2 in the internal file below.
    3. Create custom pod template [benchmark_runner/common/template_operations/templates/vdbench/internal_data/vdbench_pod_template.yaml](benchmark_runner/common/template_operations/templates/vdbench/internal_data/vdbench_pod_template.yaml)
8. Create Workload class [benchmark_runner/workloads/workloads.py](benchmark_runner/workloads/workloads.py)
    1. Add custom workload method, example:
   ```
      @typechecked
      @logger_time_stamp
      def vdbench_pod(self, name: str = ''):
      """
      This method run vdbench pod workload
      :return:
      """
      if name == '':
      name = self.vdbench_pod.__name__
      run = VdbenchPod()
      run.vdbench_pod(name=name)
   ```
    2. Add custom workload class, [benchmark_runner/workloads/vdbench_pod.py](benchmark_runner/workloads/vdbench_pod.py):
       Please copy the whole class and functionality
9. Add workload method name (workload_pod/workload_vm) to environment_variables_dict['workloads'] in [benchmark_runner/main/environment_variables.py](benchmark_runner/main/environment_variables.py)
10. Add workload folder path in [MANIFEST.in](MANIFEST.in), add 2 paths: the workload path to 'workload_data_template.yaml' and path to 'internal_data' Pod and VM template yaml files
   ```
   include benchmark_runner/common/template_operations/templates/vdbench/*.yaml
   include benchmark_runner/common/template_operations/templates/vdbench/internal_data/*.yaml
   ```
11. Add tests for all new methods you write under `tests/integration`.
12. Update the golden unit test files as described [above](#add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job)
13. For test and debug workload, need to configure [benchmark_runner/main/environment_variables.py](benchmark_runner/main/environment_variables.py).  You may alternatively set these variables in the environment or pass command line options, which in all cases are `--lowercase-option` where the name of the environment variable is lower cased.  For example:
   ```
   python3 benchmark_runner/main/main.py --runner-path=/parent/of/benchmark-runner --workload=stressng_pod --kubeadmin-password=password --pin-node-benchmark-operator=worker-0 --pin-node1=worker-1 --pin-node2=worker-2 --elasticsearch=elasticsearch_port --elasticsearch-port=80
   ```
   or
   ```
	RUNNER_PATH=/parent/of/benchmark-runner WORKLOAD=stressng_pod KUBEADMIN_PASSWORD=password PIN_NODE_BENCHMARK_OPERATOR=worker-0 PIN_NODE1=worker-1 PIN_NODE2=worker-2 ELASTICSEARCH=elasticsearch_port ELASTICSEARCH_PORT=80 python3 benchmark_runner/main/main.py
   ```
14. Fill parameters: workload, kubeadmin_password, pin_node_benchmark_operator, pin_node1, pin_node2, elasticsearch, elasticsearch_port
15. Run [/benchmark_runner/main/main.py](/benchmark_runner/main/main.py)  and verify that the workload run correctly
16. The workload can be monitored and checked through 'current run' folder inside the run workload flavor (default flavor: 'test_ci')
17. Open Kibana url and verify workload index populate with data:
18. Create the workload index: Kibana -> Hamburger tab -> Stack Management -> Index patterns -> Create index pattern -> workload-results -> timestamp -> Done
19. Verify workload-results index is populated: Kibana -> Hamburger tab -> Discover -> workload-results (index) -> verify that there is a new data
