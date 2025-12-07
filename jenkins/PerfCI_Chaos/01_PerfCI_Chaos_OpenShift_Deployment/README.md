# PerfCI Chaos OpenShift Deployment Environment Setup

This project automates the deployment of OpenShift cluster.

To run the deployment pipeline successfully, configure the required environment variables listed below.
1. Clone the Jetlag repository on the bastion server under `/root`. [https://github.com/redhat-performance/jetlag]
2. Copy run_jetlag.sh to the bastion server `/root/jetlag/` directory. [https://github.com/redhat-performance/benchmark-runner/blob/main/benchmark_runner/common/assisted_installer/jetlag/run_jetlag.sh]
3. Ensure the Jenkins agent has access to the bastion server with the necessary SSH keys and configurations.
4. Set up the environment variables as specified in the sections below.
5. Run first Jetlag installation using run_jetlag.sh and verify that no issues occur during installation.
6. All the steps including 'ansible-playbook ansible/create-inventory.yml' should be done manually for the first time.
- **Important:** Run the Jenkins agent on the bastion server.

---

## 🚨 Mandatory Environment Variables

| Variable                           | Description                                                                                                               |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| `INSTALL_OCP_VERSION`              | Install OCP version, constant version `4.20.0` or latest-4.20.0-ec (dev)/ latest-4.20/ latest-4.20.0-rc (ga)              |
| `OCP_BUILD`                        | Set to `'ga'/'dev'`.                                                                                                      |
| `PROVISION_PRIVATE_KEY_FILE`       | provision private key path (e.g. `/root/.ssh/id_rsa` )                                                                    |
| `PROVISION_IP`                     | provision ip                                                                                                              |
| `PROVISION_USER`                   | provision user                                                                                                            |
| `CLUSTER_TYPE`                     | cluster type `SNO` or MNO (default '' for MNO)                                                                            |
| `EXPECTED_NODES`                   | expected nodes (e.g. { "master": ["master-0", "master-1", "master-2"], "worker": ["worker-0", "worker-1", "worker-2" ] }) |
| `OCP_CLIENT_VERSION`               | ocp client version  (e.g., `4.20.0`).                                                                                     |
| `QUAY_BENCHMARK_RUNNER_REPOSITORY` | benchmark-runner quay.io container (quay.io/benchmark-runner/benchmark-runner:latest)                                     |
| `WORKSPACE`                        | Jenkins workspace `/home/jenkins`                                                                                         |
| `PROVISION_PORT`                   | provision port  (e.g., `22`).                                                                                             |
| `KUBEADMIN_PASSWORD_PATH`          | kubeadmin password path (e.g., `/root/.kube/kubeadmin-password`)                                                          |
| `KUBECONFIG_PATH`                  | kubeconfig path  (e.g.,`/root/.kube/config`).                                                                             |
| `PROVISION_INSTALLER_PATH`         | provision installer path (e.g.,`/root/jetlag/./run_jetlag.sh`).                                                           |
| `PROVISION_INSTALLER_CMD`          | provision installer cmd (e.g.,`pushd /root/jetlag;/root/jetlag/./run_jetlag.sh 1>/dev/null 2>&1;popd`).                   |
| `PROVISION_INSTALLER_LOG`          | provision installer log for identify pass/fail installation (e.g.,`tail -100 /root/jetlag/jetlag.log`).                   |
| `INSTALLER_VAR_PATH`               | provision installer vars (e.g.,`/root/jetlag/ansible/vars`).                                                              |
| `PRIVATE_KEY_PATH`                 | provision private key path (e.g.,`/home/jenkins/.ssh/provision_private_key`).                                             |
| `CONFIG_PATH`                      | provision config path for remote connection (e.g.,`/home/jenkins/.ssh/config`).                                           |
| `CONTAINER_PRIVATE_KEY_PATH`       | benchmark-runner container private key path (e.g.,`/root/.ssh/provision_private_key`).                                    |
| `CONTAINER_CONFIG_PATH`            | benchmark-runner container config path (e.g.,`/root/.ssh/config`).                                                        |
| `ANSIBLE_TMP_PATH`                 | ansible tmp path for jetlag (e.g.,`/root/.ansible/tmp/`).                                                                 |
| `PROVISION_TIMEOUT`                | provision timeout  (e.g.,`7200`).                                                                                         |
---
** For more environment details, refer to:
https://github.com/redhat-performance/benchmark-runner/blob/main/benchmark_runner/main/environment_variables.py---

## 🔧 Optional Environment Variables

| Variable                    | Description |
|-----------------------------|-------------|
| `CONTACT_EMAIL`             | Jenkins job notification email (on job pass or fail). |

## 📌 Notes

- Use Jenkins credentials bindings to securely handle secret values.
- Ensure all paths and IPs are accessible from the Jenkins host.
- Always validate your environment variables before running the deployment pipeline.


---
