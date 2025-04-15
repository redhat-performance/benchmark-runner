# 🖥️ Scale Fedora & Windows VMs with Benchmark Runner

This document provides automated scripts and configuration to **scale Fedora and Windows VMs** on OpenShift clusters. It verifies the VM login page and measures **bootstorm time**—the time it takes for VMs to become fully operational.

---

## 🚀 Features

- Scale Fedora VMs using **ephemeral storage**
- Scale Windows VMs using **ODF-backed storage** (via DataVolume)
- Parallel VM loading across specified worker nodes
- Optional metrics collection via **Elasticsearch**
- Logs and artifacts are stored locally for post-run analysis

---

## 🧪 Prerequisites

- OpenShift cluster with kubeadmin access
- [`podman`](https://podman.io) installed

---

## ⚙️ Parameters

### Common Parameters
| Variable                    | Description                                                                                                                                                                                                                                                                 |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `KUBEADMIN_PASSWORD`        | *(Optional, if already login)* OpenShift admin password                                                                                                                                                                                                                     |
| `KUBECONFIG_PATH`           | Path to your kubeconfig (e.g., `$HOME/.kube/config`)                                                                                                                                                                                                                        |
| `SCALE_NODES`               | List of target worker nodes (e.g., `["worker-0", "worker-1"]`)                                                                                                                                                                                                              |
| `THREADS_LIMIT`             | Number of physical CPUs to use for parallelism (e.g., `20`)                                                                                                                                                                                                                 |
| `TIMEOUT`                   | Maximum duration (in seconds) for the run; `0` or a negative value means no timeout                                                                                                                                                                                         |
| `LOGS_PATH`                 | *(Optional)* Path for logs (YAML files and `benchmark_runner.log`); default is `/tmp/benchmark-runner-run-artifacts`                                                                                                                                                        |
| `RUN_ARTIFACTS_URL`         | *(Optional, default: `False`)* If `True`, Remote URL for saving logs                                                                                                                                                                                                        |
| `SAVE_ARTIFACTS_LOCAL`      | *(Optional, default: `False`)* If `True`, saves logs locally to `/tmp/benchmark-runner-run-artifacts`                                                                                                                                                                       |
| `ENABLE_PROMETHEUS_SNAPSHOT` | *(Optional, default: `False`)* If `True`, saves and collects a Prometheus snapshot (`promdb_*.tar`) and query results. See [metrics-default.yaml](https://github.com/redhat-performance/benchmark-runner/blob/main/benchmark_runner/common/prometheus/metrics-default.yaml) |
| `RUN_STRATEGY` | *(Optional, default: `False`)* If `True`, when `RUN_STRATEGY` is defined, it injects `runStrategy: Always` into the YAML.                                                                                                                                                   |

### Results in `benchmark_runner.log` (can be distributed into ElasticSearch):
- `vm_name`: Name of the VM  
- `node`: The node the VM ran on  
- `bootstorm_time` (milliseconds): Time taken to boot the VM  
- `vm_ssh`: `1` = success, `0` = failure; indicates whether the VM is reachable via SSH  

## 🧰 Fedora VM BootStorm (Ephemeral Storage)

This mode loads Fedora VMs using ephemeral storage and verifies their readiness via the login page.

### Fedora-Specific Parameters

| Variable | Description                                                                                      |
|----------|--------------------------------------------------------------------------------------------------|
| `BOOTSTORM_SCALE` | Number of Fedora VMs per worker node, e.g. 10                                                    |
| `FEDORA_CONTAINER_DISK` | (Optional) Fedora .qcow2 image from quay.io (e.g.: quay.io/openshift-cnv/qe-cnv-tests-fedora:37) |

🔧 Example Configuration:
```bash
# OpenShift admin password
export KUBEADMIN_PASSWORD=xxxxx-xxxxx-xxxxx-xxxxx
# Number of Windows VMs per worker node
export BOOTSTORM_SCALE=10
# container disk image
export FEDORA_CONTAINER_DISK="quay.io/openshift-cnv/qe-cnv-tests-fedora:37"
# List of target worker nodes
export SCALE_NODES="[ 'worker-0', 'worker-1', 'worker-2' ]"
# Number of physical CPUs to use for parallelism
export THREADS_LIMIT=20
# Path to kubeconfig
export KUBECONFIG_PATH=/root/.kube/config
# Timeout in seconds (0 or negative means no timeout)
export TIMEOUT=7200
# Path for logs (YAML files and benchmark_runner.log)
export LOGS_PATH=/tmp/benchmark-runner-run-artifacts
```

### Example Script for scaling Fedora VMs

```bash
#!/bin/bash

# Load Fedora VMs including verification (verify login page)
sudo podman run --rm -it \
  -e WORKLOAD='bootstorm_vm' \
  -e KUBEADMIN_PASSWORD="${KUBEADMIN_PASSWORD}" \
  -e RUN_ARTIFACTS_URL="${RUN_ARTIFACTS_URL}" \
  -e SAVE_ARTIFACTS_LOCAL=True \
  -e SCALE="${BOOTSTORM_SCALE}" \
  -e FEDORA_CONTAINER_DISK="${FEDORA_CONTAINER_DISK}" \
  -e SCALE_NODES="${SCALE_NODES}" \
  -e THREADS_LIMIT="${THREADS_LIMIT}" \
  -e RUN_STRATEGY=True \
  -e TIMEOUT="${TIMEOUT}" \
  -e log_level="INFO" \
  -v "${LOGS_PATH}:${LOGS_PATH}" \
  -v "${KUBECONFIG_PATH}:${KUBECONFIG_PATH}" \
  quay.io/ebattat/benchmark-runner:latest
```
Verify the running VMs and get bootstorm_time(millisecond):
```
$ oc get vmi -n benchmark-runner
$ grep bootstorm_time benchmark_runner.log
{'vm_name': 'bootstorm-vm-cd2a4395-1', 'node': 'worker-2', 'bootstorm_time': 577.893, 'vm_ssh': 1}
```

## 🧰 Windows VM Bootstorm (ODF Storage)

This mode loads Windows VMs using ODF persistent volumes and validates successful login.

### Windows-Specific Parameters

| Variable | Description                                                                                                                     |
|----------|---------------------------------------------------------------------------------------------------------------------------------|
| `WINDOWS_SCALE` | Number of Windows VMs per worker node, e.g. 10                                                                                  |
| `WINDOWS_URL` | *(No default, must be provided by the user)* URL to the Windows `.qcow2` image shared via NGINX (e.g., `http://<host>:8083/windows.qcow2`) |

### Example Script for scaling Window VMs

```bash
#!/bin/bash

# Load Windows VMs including verification (verify login home page)
sudo podman run --rm -t \
  -e WORKLOAD='windows_vm' \
  -e KUBEADMIN_PASSWORD="${KUBEADMIN_PASSWORD}" \
  -e SAVE_ARTIFACTS_LOCAL=True \
  -e SCALE="${WINDOWS_SCALE}" \
  -e SCALE_NODES="${SCALE_NODES}" \
  -e THREADS_LIMIT="${THREADS_LIMIT}" \
  -e WINDOWS_URL="${WINDOWS_URL}" \
  -e RUN_STRATEGY=True \
  -e TIMEOUT="${TIMEOUT}" \
  -e log_level="INFO" \
  -v "${LOGS_PATH}:${LOGS_PATH}" \
  -v "${KUBECONFIG_PATH}:${KUBECONFIG_PATH}" \
  quay.io/ebattat/benchmark-runner:latest
```

Verify the running VMs and get bootstorm_time(millisecond):
```
$ oc get vmi -n benchmark-runner
$ grep bootstorm_time benchmark_runner.log
{'vm_name': 'bootstorm-vm-cd2a4395-1', 'node': 'worker-2', 'bootstorm_time': 577.893, 'vm_ssh': 1}
```

# 📊 [Optional]: Elasticsearch Integration for Metrics Collection

This document explains how to integrate **Elasticsearch** into your VM scaling process to collect and store performance metrics, including **bootstorm time** and `virtctl` access status. 

---

## 🚀 Features

- Collects performance metrics like **bootstorm time** (the time it takes for a VM to boot and become reachable) and `virtctl_vm` status.
- Optional Elasticsearch integration with the benchmark runner.
- Allows central storage and analysis of metrics for better performance insights.

---

## 🧪 Prerequisites

- A running **Elasticsearch** instance (can be self-hosted or cloud-based).
- Proper access to Elasticsearch from the system running the benchmark runner.
- Ensure that the `ELASTICSEARCH` and `ELASTICSEARCH_PORT` environment variables are configured correctly in your benchmarking scripts.

---

## ⚙️ Parameters for Elasticsearch

| Variable | Description |
|----------|-------------|
| `ELASTICSEARCH` | Hostname or IP address of the Elasticsearch server (e.g., `http://localhost`) |
| `ELASTICSEARCH_PORT` | Port on which Elasticsearch is running (e.g., `9200`) |

---

## 🧰 Integrating Elasticsearch with Benchmark Runner

To enable Elasticsearch integration, simply pass the following environment variables when running the benchmark runner container:

### Example Script with Elasticsearch Integration

```bash
#!/bin/bash

# Example run with Elasticsearch integration for metrics collection
sudo podman run --rm -t \
  -e WORKLOAD='windows_vm' \
  -e KUBEADMIN_PASSWORD="${KUBEADMIN_PASSWORD}" \
  -e SAVE_ARTIFACTS_LOCAL=True \
  -e SCALE="${WINDOWS_SCALE}" \
  -e SCALE_NODES="${SCALE_NODES}" \
  -e THREADS_LIMIT="${THREADS_LIMIT}" \
  -e WINDOWS_URL="${WINDOWS_URL}" \
  -e RUN_STRATEGY=True \
  -e TIMEOUT="${TIMEOUT}" \
  -e log_level="INFO" \
  -e ELASTICSEARCH="${ELASTICSEARCH}" \
  -e ELASTICSEARCH_PORT="${ELASTICSEARCH_PORT}" \
  -v "${LOGS_PATH}:${LOGS_PATH}" \
  -v "${KUBECONFIG_PATH}:${KUBECONFIG_PATH}" \
  quay.io/ebattat/benchmark-runner:latest
```

Verify the running VMs and get bootstorm_time(millisecond):
```
$ oc get vmi -n benchmark-runner
$ grep bootstorm_time benchmark_runner.log
{'vm_name': 'bootstorm-vm-cd2a4395-1', 'node': 'worker-2', 'bootstorm_time': 577.893, 'vm_ssh': 1}
```
