#!/usr/bin/env sh

sgdisk_list=$1
oc get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" |  xargs -I{} oc debug node/{} -- chroot /host sh -c "$sgdisk_list"
