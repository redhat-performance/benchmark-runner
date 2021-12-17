
[![Actions Status](https://github.com/redhat-performance/benchmark-runner/workflows/CI/badge.svg)](https://github.com/redhat-performance/benchmark-runner/actions)
[![Coverage Status](https://coveralls.io/repos/github/redhat-performance/benchmark-runner/badge.svg?branch=main)](https://coveralls.io/github/redhat-performance/benchmark-runner?branch=main)

# Benchmark-Runner

This tool provides a lightweight and flexible framework for running benchmark workloads 
on Kubernetes/OpenShift Pod or VM.

This tool support the following workloads:

* [hammerdb](https://hammerdb.com/): running hammerdb workload on the following databases: MSSQL, Mariadb, Postgresql on Pod and VM with [Configuration](benchmark_runner/benchmark_operator/workload_flavors/func_ci/hammerdb)
* [stressng](https://wiki.ubuntu.com/Kernel/Reference/stress-ng): running stressng workload on Pod or VM with [Configuration](benchmark_runner/benchmark_operator/workload_flavors/func_ci/stressng)
* [uperf](http://uperf.org/): running uperf workload on Pod or VM with [Configuration](benchmark_runner/benchmark_operator/workload_flavors/func_ci/uperf)

** First Phase: supports [benchmark-operator workloads](https://github.com/cloud-bulldozer/benchmark-operator)

Benchmark-runner grafana dashboard example:
![](media/grafana.png)

Reference:
* The benchmark-runner package is located in [PyPi](https://pypi.org/project/benchmark-runner)
* The benchmark-runner container image is located in [Quay.io](https://quay.io/repository/ebattat/benchmark-runner)

## Documentation
Documentation is available at [benchmark-runner.readthedocs.io](https://benchmark-runner.readthedocs.io/en/latest/)

![](media/docker1.png)

_**Table of Contents**_

<!-- TOC -->
- [Run workload using Podman or Docker](#run-workload-using-podman-or-docker)
- [Run workload in Pod using Kubernetes or OpenShift](#run-workload-in-pod-using-kubernetes-or-openshift)
- [Grafana dashboards](#grafana-dashboards)
- [How to develop in benchmark-runner](#how-to-develop-in-benchmark-runner)

<!-- /TOC -->

## Run workload using Podman or Docker 

#### Environment variables description:

**mandatory:** WORKLOAD=$WORKLOAD

Choose one from the following list:

`['stressng_pod', 'stressng_vm', 'stressng_kata','uperf_pod', 'uperf_vm', 'uperf_kata', 'hammerdb_pod_mariadb', 'hammerdb_pod_mssql', 'hammerdb_pod_postgres', 'hammerdb_vm_mariadb', 'hammerdb_vm_mssql', 'hammerdb_vm_postgres', 'hammerdb_kata_mariadb', 'hammerdb_kata_mssql', 'hammerdb_kata_postgres']`

**auto:** NAMESPACE=benchmark-operator [ The default namespace is benchmark-operator ]

**auto:** OCS_PVC=True [ True=OCS PVC storage, False=Ephemeral storage, default True ]

**auto:** EXTRACT_PROMETHEUS_SNAPSHOT=True [ True=extract Prometheus snapshot into artifacts, false=don't, default True ]

**auto:** SYSTEM_METRICS=True [ True=collect metric, False=not collect metrics, default True ]

**auto:** RUNNER_PATH=/tmp [ The default work space is /tmp ]

**optional:** KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD

**optional:** PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR [node selector for benchmark operator pod]

**optional:** PIN_NODE1=$PIN_NODE1 [node1 selector for running the workload]

**optional:** PIN_NODE2=$PIN_NODE2 [node2 selector for running the workload, i.e. uperf server and client, hammerdb database and workload]

**optional:** ELASTICSEARCH=$ELASTICSEARCH [ elasticsearch service name]

**optional:** ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT

```sh
podman run --rm -e WORKLOAD=$WORKLOAD -e KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD -e PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR -e PIN_NODE1=$PIN_NODE1 -e PIN_NODE2=$PIN_NODE2 -e ELASTICSEARCH=$ELASTICSEARCH -e ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT -e log_level=INFO -v $KUBECONFIG:/root/.kube/config --privileged quay.io/ebattat/benchmark-runner:latest
```

![](media/demo.gif)

## Run workload in Pod using Kubernetes or OpenShift

[TBD]

## Grafana dashboards

There are 3 grafana dashboards templates:
1. [benchmark-runner-ci-status-report.json](grafana/benchmark-runner-ci-status-report.json)
![](media/benchmark-runner-ci-status.png)
2. [benchmark-runner-report.json](grafana/benchmark-runner-report.json)
![](media/benchmark-runner-report.png)
3. [benchmark-runner-compare-3-ci-dates-report.json](grafana/benchmark-runner-compare-3-ci-dates-report.json)
![](media/benchmark-runner-compare-3-ci-dates-report.png)
4. [benchmark-runner-compare-3-ocp-versions-report.json](grafana/benchmark-runner-compare-3-ocp-versions-report.json)
![](media/benchmark-runner-compare-3-ocp-versions-report.png)
5. [system-metrics-report.json](grafana/system-metrics-report.json)
![](media/system-metrics-report.png)

** After importing json in grafana, need to configure elasticsearch data source. (for more details: see [HOW_TO.md](HOW_TO.md))

## How to develop in benchmark-runner

see [HOW_TO.md](HOW_TO.md)
