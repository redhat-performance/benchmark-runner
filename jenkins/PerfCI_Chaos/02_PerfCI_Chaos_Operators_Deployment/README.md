# PerfCI Chaos Operators Deployment Environment Setup

This project automates the deployment of operators on OpenShift clusters.

To run the deployment pipeline successfully, configure the required environment variables listed below.

- **Important:** Run the Jenkins agent on the bastion server.

---

## 🚨 Mandatory Environment Variables

| Variable                           | Description                                                                                                                                                                                             |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `INSTALL_OCP_RESOURCES`            | `'True'` for install operators                                                                                                                                                                          |
| `CNV_NIGHTLY_CHANNEL`              | Set to `'False'/'True'` to install cnv nightly, false for install stable cnv                                                                                                                            |
| `CNV_VERSION`                      | CNV version (e.g., `4.20`).                                                                                                                                                                             |
| `LSO_VERSION`                      | LSO version (e.g., `4.20`).                                                                                                                                                                             |
| `ODF_VERSION`                      | ODF version (e.g., `4.20`).                                                                                                                                                                             |
| `PROVISION_USER`                   | bastion server user  (e.g., `root`).                                                                                                                                                                    |
| `PROVISION_IP`                     | bastion server ip.                                                                                                                                                                                      |
| `WORKER_DISK_IDS`                  | List of ODF disks per worker node  (e.g., ` { "worker-0": ["62cea7f08e1581002d419c2310a03225" ], "worker-1": ["62cea7f05dfe4c002d419952a27cb38e"], "worker-2": ["62cea7f08df680002d419bc00c5b7bad"]}`). |
| `EXPECTED_NODES`                   | expected nodes for cluster nodes verification (e.g., `{ "master": ["master-0", "master-1", "master-2"], "worker": ["worker-0", "worker-1", "worker-2" ] }`).                                            |
| `QUAY_BENCHMARK_RUNNER_REPOSITORY` | Default benchmark-runner quay.io image `quay.io/benchmark-runner/benchmark-runner:latest` .                                                                                                             |
| `BMC_USER`                         | bastion server bmc user                                                                                                                                                                                 |
| `BMC_IPS`                          | bastion ips dictionary {} for 'nhc_far' operator                                                                                                                                                        |
| `KUBEADMIN_PASSWORD`               | kubeadmin password ( e.g. `/home/jenkins/.kube/kubeadmin-password`)                                                                                                                                     |
| `KUBEADMIN_PASSWORD_PATH`          | kubeadmin password path ( e.g. `/home/jenkins/.kube/kubeadmin-password`)                                                                                                                                |
| `KUBECONFIG_PATH`                  | kubeaconfig path ( e.g. `/root/.kube/config`)                                                                                                                                                           |
| `PRIVATE_KEY_PATH`                 | provision private key path ( e.g. `/home/jenkins/.ssh/provision_private_key`)                                                                                                                           |
| `CONFIG_PATH`                      | provision config path ( e.g. `/home/jenkins/.ssh/config`)                                                                                                                                               |
| `WORKSPACE`                        | provision workspace path ( e.g. `/home/jenkins`)                                                                                                                                                        |
| `CONTAINER_PRIVATE_KEY_PATH`       | benchmark-runner container private key path ( e.g. `/root/.ssh/provision_private_key`)                                                                                                                  |
| `WORKER_DISK_IDS_PREFIX`           | disk id prefix  (e.g., `wwn-0x`)                                                                                                                                                                        |
| `PROVISION_PORT`                   | provision part  (e.g., `22`)                                                                                                                                                                            |
| `NUM_ODF_DISK`                     | number of odf disks per worker node  (e.g., `6`)                                                                                                                                                        |
| `PROVISION_TIMEOUT`                | provision timeout (e.g., `3600`)                                                                                                                                                                        |
---
** For more environment details, refer to:
https://github.com/redhat-performance/benchmark-runner/blob/main/benchmark_runner/main/environment_variables.py
---

## 🔧 Optional Environment Variables

| Variable                    | Description |
|-----------------------------|-------------|
| `CONTACT_EMAIL`             | Jenkins job notification email (on job pass or fail). |

## 📌 Notes

- Use Jenkins credentials bindings to securely handle secret values.
- Ensure all paths and IPs are accessible from the Jenkins host.
- Always validate your environment variables before running the deployment pipeline.


---
