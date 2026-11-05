#!/usr/bin/env sh

# Clean the LVMS devices and leftover LVMS volume groups on worker nodes
# before creating the LVMCluster.
# Arguments are consumed in pairs: <node> <cleanup_command>
while [ "$#" -ge 2 ]; do
    node="$1"
    cleanup_command="$2"

    echo "Executing LVMS disk cleanup on node: $node"

    oc debug "node/$node" -- chroot /host sh -c "$cleanup_command"

    shift 2
done
