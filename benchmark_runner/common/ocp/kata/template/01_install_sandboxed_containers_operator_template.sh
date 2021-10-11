#!/bin/sh
# install kata operator
curl https://raw.githubusercontent.com/openshift/sandboxed-containers-operator/master/deploy/deploy.sh | bash
oc apply -f https://raw.githubusercontent.com/openshift/sandboxed-containers-operator/master/config/samples/kataconfiguration_v1_kataconfig.yaml