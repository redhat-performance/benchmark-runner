#!/bin/bash

CMDFILE=$(cat <<'EOF'
#!/bin/bash
set -e
if [[ -f /usr/libexec/kata-containers/osbuilder/kata-osbuilder.sh ]] ; then
    sudo mount -o rw,remount /usr
    grep cpu /usr/lib/udev/rules.d/40-redhat.rules
    sudo sed -i  's/^SUBSYSTEM=="cpu"/#SUBSYSTEM=="cpu"/' /usr/lib/udev/rules.d/40-redhat.rules
    grep cpu /usr/lib/udev/rules.d/40-redhat.rules
    sudo /usr/libexec/kata-containers/osbuilder/kata-osbuilder.sh
    sudo mount -o ro,remount /usr
    grep cpu /usr/lib/udev/rules.d/40-redhat.rules
else
    echo "Kata does not appear to be installed on $(hostname)"
    exit 1
fi
EOF
)

declare -a oc_version
IFS=. read -r -a oc_version <<< "$(oc version -ojson |jq -r .openshiftVersion)"

if ((oc_version[0] > 4 || (oc_version[0] == 4 && oc_version[1] != 8) )) ; then
    echo "Openshift version ${oc_version[0]}.${oc_version[1]}.${oc_version[2]} does not need Kata workaround" 1>&2
elif [[ -z "$(oc get ns openshift-sandboxed-containers-operator -oname)" ]] ; then
    echo "openshift-sandboxed-containers-operator is not installed" 1>&2
elif [[ -z "$(oc get kataconfig 2>/dev/null)" ]] ; then
    echo "No Kata configuration available!" 1>&2
else
    for node in $(oc get node -lnode-role.kubernetes.io/worker= -oname --no-headers); do
	oc debug -T "$node" -- chroot /host sh -c 'cat > /tmp/fix-kata; chmod +x /tmp/fix-kata; /tmp/fix-kata; rm -f /tmp/fix-kata' <<< "$CMDFILE"
    done
fi
