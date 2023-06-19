
## SECRETS

# flask
AWS_DEFAULT_REGION=""
ENDPOINT_URL=""
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
BUCKET=""
# Add separate ip for ci pod
POD_CI_IP=""
BASTION_IP=""

# Change in nginx/Dockerfile and jupyter
JUPYTERLAB_VERSION=""
MAINTAINER=""
USER=""
TOKEN=""
# Jupyterlab: oc/virtctl version
OC_VERSION=""
VIRTCTL_VERSION=""

# MUST replace MANUALLY in nginx/ibm_conf.conf
JUPYTERLAB_URL=""
RUN_ARTIFACTS_URL=""
GRAFANA_URL=""
KIBANA_URL=""
ELASTICSEARCH_URL=""
INTERNAL_URL=""

CI_POD_PATH=""
CI_LOGS_PATH=""

mkdir -p /tmp/"$CI_LOGS_PATH"
mkdir -p "$CI_POD_PATH"/elastic/
mkdir -p "$CI_POD_PATH"/grafana/
mkdir -p "$CI_POD_PATH"/windows/
mkdir -p "$CI_POD_PATH"/jupyterLab/

# chmod solved ci_pod degraded
chmod 775 -R "$CI_POD_PATH"/elastic/
chmod 775 -R "$CI_POD_PATH"/grafana/
chmod 775 -R "$CI_POD_PATH"/windows/
chmod 775 -R "$CI_POD_PATH"/jupyterLab/

cd "$CI_POD_PATH"/ci_pod
podman pod create --name ci_pod -p 80:80 -p "$POD_CI_IP":443:443
podman run --name elasticsearch --pod ci_pod -d -e "discovery.type=single-node" -e "xpack.security.enabled=false" -v "$CI_POD_PATH"/elastic:/usr/share/elasticsearch/data --privileged docker.elastic.co/elasticsearch/elasticsearch:7.16.0
podman run --name kibana --pod ci_pod -d -e "ELASTICSEARCH_HOSTS=http://localhost:9200" docker.elastic.co/kibana/kibana:7.16.0
podman run --name grafana --pod ci_pod -d -v "$CI_POD_PATH"/grafana:/var/lib/grafana quay.io/mimehta/custom-grafana:latest
cd "$CI_POD_PATH"/ci_pod/flask
podman build -t flaskci .
podman run --name flask --pod ci_pod -d -u root -e AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION" -e ENDPOINT_URL="$ENDPOINT_URL" -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" -e BUCKET="$BUCKET" localhost/flaskci
cd "$CI_POD_PATH"/ci_pod/nginx
podman build -t proxyci --build-arg USER="$USER" --build-arg TOKEN="$TOKEN" .
podman run -d --pod ci_pod --name cntproxy localhost/proxyci
cd "$CI_POD_PATH"/ci_pod/jupyterlab
podman build -t jupyterlab --build-arg JUPYTERLAB_VERSION="$JUPYTERLAB_VERSION" --build-arg MAINTAINER="$MAINTAINER" --build-arg OC_VERSION="$OC_VERSION" --build-arg VIRTCTL_VERSION="$VIRTCTL_VERSION" .
podman run --name jupyterlab --pod ci_pod -d --privileged -e JUPYTER_TOKEN="$TOKEN" -v "$CI_POD_PATH"/jupyterLab:/notebooks -v "$HOME"/.kube:"$HOME"/.kube localhost/jupyterlab

# share windows image
podman run -d --name win-nginx -v "$CI_POD_PATH"/windows:/usr/share/nginx/html:ro -p "$BASTION_IP":8083:80 docker.io/library/nginx:latest

echo "check pod ci status"
podman pod ls
