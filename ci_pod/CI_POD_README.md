Instructions for ci_pod deployment:

1. Run `dnf install -y podman`
2. Fill all the secrets in create_ci_pod.sh
3. replace MANUALLY the following URLs in nginx/ibm_conf.conf
     ```sh
     JUPYTERLAB_URL=""
     RUN_ARTIFACTS_URL=""
     GRAFANA_URL=""
     KIBANA_URL=""
     ELASTICSEARCH_URL=""
     INTERNAL_URL=""
     ```
4. Add ibm certificate files under ci_pod/nginx/:
     ```sh
     ibm_crt.crt;
     ibm_private.key;
    ```
5. Create separate public ip for ci pod and update POD_CI_IP in create_ci_pod.sh
6. Run `cp -rp ci_pod "$CI_POD_PATH"`
7. Run `"$CI_POD_PATH"/ci_pod/create_ci_pod.sh`
