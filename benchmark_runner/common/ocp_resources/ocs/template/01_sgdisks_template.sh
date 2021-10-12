#!/usr/bin/env sh

sgdisk_list = $1
oc get nodes -l cluster.ocs.openshift.io/openshift-storage= -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" |  xargs -I{} oc debug node/{} -- chroot /host sh -c "$sgdisk_list"