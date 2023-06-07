
## Run workload using Podman or Docker

The following options may be passed via command line flags or set in the environment:

**mandatory:** WORKLOAD=$WORKLOAD

**mandatory:** KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD

**mandatory:** $KUBECONFIG [ kubeconfig file path]

Choose one from the following list:

`['stressng_pod', 'stressng_vm', 'stressng_kata', 'uperf_pod', 'uperf_vm', 'uperf_kata', 'hammerdb_pod_mariadb', 'hammerdb_vm_mariadb', 'hammerdb_kata_mariadb', 'hammerdb_pod_mariadb_lso', 'hammerdb_vm_mariadb_lso', 'hammerdb_kata_mariadb_lso', 'hammerdb_pod_postgres', 'hammerdb_vm_postgres', 'hammerdb_kata_postgres', 'hammerdb_pod_postgres_lso', 'hammerdb_vm_postgres_lso', 'hammerdb_kata_postgres_lso', 'hammerdb_pod_mssql', 'hammerdb_vm_mssql', 'hammerdb_kata_mssql', 'hammerdb_pod_mssql_lso', 'hammerdb_vm_mssql_lso', 'hammerdb_kata_mssql_lso', 'vdbench_pod', 'vdbench_kata', 'vdbench_vm', 'clusterbuster', 'bootstorm_vm']`

** For hammerdb mssql must run only once [permission](https://github.com/redhat-performance/benchmark-runner/blob/main/benchmark_runner/common/ocp_resources/custom/template/02_mssql_patch_template.sh)

** clusterbuster workloads: cpusoaker, files, fio, uperf.  For more details [see](https://github.com/RobertKrawitz/OpenShift4-tools)

**auto:** NAMESPACE=benchmark-operator [ The default namespace is benchmark-operator ]

**auto:** ODF_PVC=True [ True=ODF PVC storage, False=Ephemeral storage, default True ]

**auto:** EXTRACT_PROMETHEUS_SNAPSHOT=True [ True=extract Prometheus snapshot into artifacts, false=don't, default True ]

**auto:** SYSTEM_METRICS=False [ True=collect metric, False=not collect metrics, default False ]

**auto:** RUNNER_PATH=/tmp [ The default work space is /tmp ]

**optional:** KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD

**optional:** PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR [node selector for benchmark operator pod]

**optional:** PIN_NODE1=$PIN_NODE1 [node1 selector for running the workload]

**optional:** PIN_NODE2=$PIN_NODE2 [node2 selector for running the workload, i.e. uperf server and client, hammerdb database and workload]

**optional:** ELASTICSEARCH=$ELASTICSEARCH [ elasticsearch service name]

**optional:** ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT

**optional:** CLUSTER=$CLUSTER [ set CLUSTER='kubernetes' to run workload on a kubernetes cluster, default 'openshift' ]

**optional:scale** SCALE=$SCALE [For Vdbench/Bootstorm: Scale in each node]

**optional:scale** SCALE_NODES=$SCALE_NODES [For Vdbench/Bootstorm: Scale's node]

**optional:scale** REDIS=$REDIS [For Vdbench only: redis for scale synchronization]

**optional:** LSO_DISK_ID=$LSO_DISK_ID [LSO_DISK_ID='scsi-<replace_this_with_your_actual_disk_id>' For using LSO Operator in hammerdb]

**optional:** WORKER_DISK_IDS=$WORKER_DISK_IDS [WORKER_DISK_IDS For ODF/LSO workloads hammerdb/vdbench]

For example:

```sh
podman run --rm --workload=$WORKLOAD --kubeadmin-password=$KUBEADMIN_PASSWORD --pin-node-benchmark-operator=$PIN_NODE_BENCHMARK_OPERATOR --pin-node1=$PIN_NODE1 --pin-node2=$PIN_NODE2 --elasticsearch=$ELASTICSEARCH --elasticsearch-port=$ELASTICSEARCH_PORT -v $KUBECONFIG:/root/.kube/config --privileged quay.io/ebattat/benchmark-runner:latest
```
or
```sh
podman run --rm -e WORKLOAD=$WORKLOAD -e KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD -e PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR -e PIN_NODE1=$PIN_NODE1 -e PIN_NODE2=$PIN_NODE2 -e ELASTICSEARCH=$ELASTICSEARCH -e ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT -e log_level=INFO -v $KUBECONFIG:/root/.kube/config --privileged quay.io/ebattat/benchmark-runner:latest
```
SAVE RUN ARTIFACTS LOCAL:
1. add `-e SAVE_ARTIFACTS_LOCAL='True'` or `--save-artifacts-local=true`
2. add `-v /tmp:/tmp`
3. git clone -b v1.0.2 https://github.com/cloud-bulldozer/benchmark-operator /tmp/benchmark-operator
