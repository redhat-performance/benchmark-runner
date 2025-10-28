#!/usr/bin/env sh

while (($# >= 2)); do
    node="$1"
    delete_disk_command="$2"

    echo "Executing deletion on node: $node"

    oc debug "node/$node" -- chroot /host sh -c "$delete_disk_command"

    shift 2
done
