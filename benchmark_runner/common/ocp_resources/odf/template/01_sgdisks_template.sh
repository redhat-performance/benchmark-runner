#!/usr/bin/env sh

while (($# >= 2)) ; do
    node=$1
    sgdisk_command=$2
    oc debug "node/$node"  -- chroot /host sh -c "$sgdisk_command"
    shift 2
done
