#!/bin/bash

oc set image deployment.apps/controller-manager manager=registry.redhat.io/openshift-sandboxed-containers/osc-rhel9-operator:1.4.1 -n openshift-sandboxed-containers-operator