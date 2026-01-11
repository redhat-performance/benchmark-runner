# VM Deployment Environment Setup

This project automates the deployment of Linux VMs on a per-node basis.

To run the VM deployment pipeline successfully, configure the required environment variables listed below.

- **Important:** Run the Jenkins agent on the bastion server.

---

## 🚨 Mandatory Environment Variables

| Variable                     | Description                                                                                     |
| ---------------------------- |-------------------------------------------------------------------------------------------------|
| `BOOTSTORM_SCALE`            | Number of VMs to scale during bootstorm (e.g., `120`).                                          |
| `DELETE_ALL`                 | Set to `'False'` to avoid deleting running VMs.                                                 |
| `KUBEADMIN_PASSWORD`         | Path to kubeadmin-password on bastion (e.g., `/home/jenkins/.kube/kubeadmin-password`).         |
| `KUBECONFIG_PATH`            | Path to kubeconfig on bastion (e.g., `/root/.kube/config`).                                     |
| `QUAY_BENCHMARK_RUNNER_REPOSITORY` | Benchmark-runner image from Quay.io (e.g., `quay.io/benchmark-runner/benchmark-runner:latest`). |
| `RUN_STRATEGY`               | Set to `'True'` to use `Always` runStrategy for NHC/FAR operators.                              |
| `RUN_TYPE`                   | Run type, typically `'chaos_ci'` for logs stamp.                                                |
| `SCALE_NODES`                | List of workload nodes to scale on (e.g., `["node-0", "node-1", "node-2"]`).                    |
| `THREADS_LIMIT`              | Maximum number of parallel threads, check bastion number of Physical CPUs (e.g., `20`).         |
| `TIMEOUT`                    | Timeout in seconds for operations (e.g., `7200`).                                               |
| `WORKLOAD`                   | `bootstorm_vm` for running Fedora37 VMs.                                                        |
| `WORKSPACE`                  | Jenkins workspace path on bastion (e.g., `/home/jenkins`).                                      |
| `WORKSPACE_PATH`             | Full Jenkins job workspace (e.g., `${env.WORKSPACE}/workspace/${env.JOB_NAME}/`).               |

---

## 🔧 Optional Environment Variables

| Variable                    | Description |
|-----------------------------|-------------|
| `CONTACT_EMAIL`             | Jenkins job notification email (on job pass or fail). |
| `ELASTICSEARCH`             | Elasticsearch URL. |
| `ELASTICSEARCH_PORT`        | Elasticsearch port. |

## 📌 Notes

- Use Jenkins credentials bindings to securely handle secret values.
- Ensure all paths and IPs are accessible from the Jenkins host.
- Always validate your environment variables before running the deployment pipeline.


---
