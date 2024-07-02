#!/bin/bash

export CI_POD_PATH="/home/jenkins/perfci/ci_pod"
## Import ci pod environment variable
source "$CI_POD_PATH"/./env_vars_ci_pod.sh

sudo -E -u jenkins "$CI_POD_PATH"/./deploy_ci_pod.sh >  "$CI_POD_PATH"/ci_pod.log
