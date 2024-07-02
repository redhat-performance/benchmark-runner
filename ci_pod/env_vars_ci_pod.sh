#!/bin/bash

# PerfCi environment variables

# flask
export AWS_DEFAULT_REGION=""
export ENDPOINT_URL=""
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export BUCKET=""
# Add separate ip for ci pod
export POD_CI_IP="10.26.8.107"
export BASTION_IP="10.26.8.107"

# Change in nginx/Dockerfile and jupyter
export JUPYTERLAB_VERSION="4.0.0"
export MAINTAINER=""
export USER=""
export TOKEN=""
# Jupyterlab: oc/virtctl version
export OCP_CLIENT_VERSION="4.16.0-rc.4"
export VIRTCTL_VERSION="1.2.0"

# MUST replace MANUALLY in nginx/ibm_conf.conf
export JUPYTERLAB_URL=""
export RUN_ARTIFACTS_URL=""
export GRAFANA_URL=""
export KIBANA_URL=""
export ELASTICSEARCH_URL=""
export INTERNAL_URL="http://localhost:9201"
export CI_PATH="/home/jenkins/perfci"
export CI_POD_PATH="$CI_PATH/ci_pod"
export CI_LOGS_PATH="benchmark-runner-run-artifacts"
export JENKINS_PATH="/home/jenkins"

mkdir -p /tmp/"$CI_LOGS_PATH"

# chmod solved ci_pod degraded- need to run only once
chmod 775 -R "$CI_PATH"/elastic/
chmod 777 -R "$CI_PATH"/grafana/
chmod 775 -R "$CI_PATH"/windows/
chmod 775 -R "$CI_PATH"/jupyterLab/
