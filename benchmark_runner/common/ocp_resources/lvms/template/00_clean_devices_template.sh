#!/usr/bin/env sh

# Clean the LVMS devices and leftover LVMS volume groups on worker nodes
# before creating the LVMCluster.
# Arguments are consumed in pairs: <node> <cleanup_command>
while [ "$#" -ge 2 ]; do
    node="$1"
    cleanup_command="$2"

    echo "Executing LVMS disk cleanup on node: $node"

    # Abort on the first node that cannot be debugged: creating the LVMCluster over
    # partially cleaned devices would leave it Degraded
    oc debug "node/$node" -- chroot /host sh -c "$cleanup_command" || exit 1

    shift 2
done
