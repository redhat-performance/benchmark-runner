#!/usr/bin/env sh

oc get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" | \
  xargs -I{} oc label node {} cluster.ocs.openshift.io/openshift-storage=''
