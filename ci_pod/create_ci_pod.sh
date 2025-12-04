#!/bin/bash

cd "$CI_POD_PATH"
sudo podman pod create --name ci_pod  -p 9200:9200 -p 5601:5601 -p 3000:3000 -p 8083:80 -p 8800:8888 -p 80:4004
# Elastic/ Kibana/ Grafana - 9200 / 5601 / 3000
sudo podman run --name elasticsearch --pod ci_pod -d -e "discovery.type=single-node" -e "xpack.security.enabled=false" -v "$CI_PATH"/elastic:/usr/share/elasticsearch/data --privileged docker.elastic.co/elasticsearch/elasticsearch:7.16.0
sudo podman run --name kibana --pod ci_pod -d -e "ELASTICSEARCH_HOSTS=http://localhost:9200" --privileged docker.elastic.co/kibana/kibana:7.16.0
sudo podman run --name grafana --pod ci_pod -d -v "$CI_PATH"/grafana/grafana.ini:/etc/grafana/grafana.ini  -v "$CI_PATH"/grafana:/var/lib/grafana  --privileged quay.io/mimehta/custom-grafana:latest
# docker.io/library/nginx:latest - cause to rate limit issue quay.io/benchmark-runner/nginx:latest
# nginx for Windows image - 8083
sudo podman run --name win-nginx --pod ci_pod -d -v "$CI_PATH"/windows:/usr/share/nginx/html:ro --privileged quay.io/benchmark-runner/nginx:latest
# flask for download logs from s3 - 4004
cd "$CI_POD_PATH"/flask
sudo podman build -t flaskci .
sudo podman run --name flask --pod ci_pod -d -u root -e AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION" -e ENDPOINT_URL="$ENDPOINT_URL" -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" -e BUCKET="$BUCKET" localhost/flaskci
#cd "$CI_POD_PATH"/nginx
#sudo podman build -t proxyci --build-arg USER="$USER" --build-arg TOKEN="$TOKEN" .
#sudo podman run -d --pod ci_pod --name cntproxy localhost/proxyci
# Jupyterlab for analyzing - 8800
cd "$CI_POD_PATH"/jupyterlab
sudo podman build -t jupyterlab --build-arg JUPYTERLAB_VERSION="$JUPYTERLAB_VERSION" --build-arg MAINTAINER="$MAINTAINER" --build-arg OCP_CLIENT_VERSION="$OCP_CLIENT_VERSION" --build-arg VIRTCTL_VERSION="$VIRTCTL_VERSION" .
sudo podman run --name jupyterlab --pod ci_pod -d -e JUPYTER_TOKEN="$TOKEN" -v "$CI_PATH"/jupyterLab:/notebooks -v /root/.kube:"$HOME"/.kube --privileged localhost/jupyterlab
sudo chown jenkins:jenkins "$CI_PATH"/jupyterLab/templates/summary_report/*.html

echo "pod ci status"
sudo podman pod ls
