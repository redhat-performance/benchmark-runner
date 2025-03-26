#!/usr/bin/env sh

while (($# >= 2)); do
    node="$1"
    delete_disk_command="$2"

    echo "Executing deletion on node: $node"

    set -x  # Enable debug mode to print the command being executed
    oc debug "node/$node" -- chroot /host sh -c "$delete_disk_command"
    set +x  # Disable debug mode

    shift 2
done
