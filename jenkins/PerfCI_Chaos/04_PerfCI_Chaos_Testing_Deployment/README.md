# VM Deployment Environment Setup

This project run chaos testing.
To run the deployment pipeline successfully, configure the following environment variables.
Important:
1. Run Jenkins slave on bastion server
---

## 🚨 Mandatory Environment Variables
| Variable                                              | Description                                                                                                                                                                                                                                      |
|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `BOOTSTORM_SCALE/SACLE`                               | Number of VMs to scale during bootstorm (e.g., `120`).                                                                                                                                                                                           |
| `DELETE_ALL`                                          | Set to `'False'` to retain running VMs.                                                                                                                                                                                                          |
| `EXPECTED_NODES`                                      | JSON defining expected master and worker node names, e.g., `{ "master": ["node-0", "node-1", "node-2"], "worker": ["node-0", "node-1", "node-2"] }`.                                                                                             |
| `KRKNHUB_MASTER_0_NODE_FAILURE_ENVIRONMENT_VARIABLES` | Environment variables for master node failure using krkn-hub:<br>[https://krkn-chaos.dev/docs/scenarios/node-scenarios/](https://krkn-chaos.dev/docs/scenarios/node-scenarios/)                                                                  |
| `KRKNHUB_MASTER_1_CPU_HOG_ENVIRONMENT_VARIABLES`      | Environment variables for master CPU hog using krkn-hub:<br>[https://krkn-chaos.dev/docs/scenarios/hog-scenarios/cpu-hog-scenario/cpu-hog-scenario-krkn-hub/](https://krkn-chaos.dev/docs/scenarios/hog-scenarios/cpu-hog-scenario/cpu-hog-scenario-krkn-hub/) |
| `KRKNHUB_WORKER_0_NODE_FAILURE_ENVIRONMENT_VARIABLES` | Environment variables for worker node failure using krkn-hub:<br>[https://krkn-chaos.dev/docs/scenarios/node-scenarios/](https://krkn-chaos.dev/docs/scenarios/node-scenarios/)                                                                  |
| `KRKNHUB_WORKER_1_CPU_HOG_ENVIRONMENT_VARIABLES`      | Environment variables for worker CPU hog using krkn-hub:<br>[https://krkn-chaos.dev/docs/scenarios/hog-scenarios/cpu-hog-scenario/cpu-hog-scenario-krkn-hub/](https://krkn-chaos.dev/docs/scenarios/hog-scenarios/cpu-hog-scenario/cpu-hog-scenario-krkn-hub/) |
| `KUBEADMIN_PASSWORD`                                  | Path to `kubeadmin-password` on the bastion host (e.g., `/home/jenkins/.kube/kubeadmin-password`).                                                                                                                                               |
| `KUBECONFIG_PATH` / `PROVISION_KUBECONFIG_PATH`       | Path to `kubeconfig` on the bastion host (e.g., `/root/.kube/config`).                                                                                                                                                                           |
| `LOCAL_LOG_PATH`                                      | Local log path on bastion server for debugging, must set `SAVE_ARTIFACTS_LOCAL = 'True'`  (e.g. default '/tmp/benchmark-runner-run-artifacts')                                                                                                   |
| `MUST_GATHER_LOG`                                     | `'True'` or `'False'`; when `'True'`, collects must gather for cnv/odf operators in vm verification failure (default is `'False'`).                                                                                                              |
| `QUAY_BENCHMARK_RUNNER_REPOSITORY`                    | Benchmark-runner image from Quay.io (e.g., `quay.io/benchmark-runner/benchmark-runner:latest`).                                                                                                                                                  |
| `RUN_STRATEGY`                                        | Set to `'True'` to apply `Always` runStrategy for NHC/SNR operators.                                                                                                                                                                             |
| `RUN_TYPE`                                            | Run type identifier, typically `'chaos_ci'` for log stamping.                                                                                                                                                                                    |
| `SAVE_ARTIFACTS_LOCAL`                                | `'True'` or `'False'` to save logs locally (default is `'False'`).                                                                                                                                                                               |
| `SCALE_NODES`                                         | List of workload nodes to scale on (e.g., `["node-0", "node-1", "node-2"]`).                                                                                                                                                                     |
| `THREADS_LIMIT`                                       | Maximum number of parallel threads; based on the number of physical CPUs on bastion, to verify VM status in parallel (e.g., `20`).                                                                                                               |
| `TIMEOUT`                                             | Timeout for operations in seconds (e.g., `7200`).                                                                                                                                                                                                |
| `VERIFICATION_ONLY`                                   | `'True'` or `'False'`; when `'True'`, only verification is performed (default is `'True'`).                                                                                                                                                      |
| `WORKLOAD`                                            | Workload type; use `bootstorm_vm` to run Fedora 37 VMs.                                                                                                                                                                                          |
| `WORKSPACE`                                           | Jenkins workspace path on the bastion host (e.g., `/home/jenkins`).                                                                                                                                                                              |
| `WORKSPACE_PATH`                                      | Full Jenkins job workspace path (e.g., `${env.WORKSPACE}/workspace/${env.JOB_NAME}/`).                                                                                                                                                           |

## 🔧 Optional Environment Variables
| Variable                         | Description                                                                            |
|----------------------------------| -------------------------------------------------------------------------------------- |
| `CONTACT_EMAIL`                  | Jenkins job notification email (sent on job success or failure).                       |
| `ELASTICSEARCH`                  | Elasticsearch server URL.                                                              |
| `ELASTICSEARCH_PORT`             | Port number used by the Elasticsearch server.                                          |
| `GOOGLE_DRIVE_PATH`              | Base URL of the Google Drive folder (e.g., `https://drive.google.com/drive/folders/`). |
| `GOOGLE_DRIVE_CREDENTIALS_FILE`  | Content of the Google Drive service account credentials JSON file.                     |
| `GOOGLE_DRIVE_TOKEN_FILE`        | Content of the Google Drive OAuth token JSON file.                                     |
| `GOOGLE_CREDENTIALS_FILE`        | File name of the credentials JSON (e.g., `credentials.json`).                          |
| `GOOGLE_TOKEN_FILE`              | File name of the token JSON (e.g., `token.json`).                                      |
| `GOOGLE_DESTINATION_PATH`        | Local path where logs or files are temporarily stored (e.g., `/tmp`).                  |
| `GOOGLE_DRIVE_SHARED_DRIVE_ID`   | ID of the root Google Drive folder (Shared Drive) where all logs are saved.            |

---

## 📌 Notes

- Use Jenkins credentials bindings to securely handle secret values.
- Ensure all paths and IPs are accessible from the Jenkins host.
- Always validate your environment variables before running the deployment pipeline.


---

