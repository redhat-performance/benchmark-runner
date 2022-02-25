
oc get nodes -l node-role.kubernetes.io/worker= -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{end}" |  xargs -I{} oc debug node/{} -- chroot /host sh -c "sed -i '/bufsize 512/d' /etc/coredns/Corefile"
