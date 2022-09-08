#!/usr/bin/env bash
# This script run jetlag installer
echo "Update version: ansible/vars/ibmcloud.yml"
source /root/jetlag/bootstrap.sh
rm -rf /root/jetlag/jelag.log
echo "CLEANUP >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
podman ps | awk '{print $1}' | xargs -I % podman stop %; podman ps -a | awk '{print $1}' | xargs -I % podman rm %; podman pod ps | awk '{print $1}' | xargs -I % podman pod rm %
echo "create ci pod"
/PerfDisk/ci_pod/./create_ci_pod.sh 1>/dev/null 2>&1
echo "SETUP BASTION >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
ansible-playbook -i ansible/inventory/ibmcloud.local ansible/ibmcloud-setup-bastion.yml 2>&1 | tee jetlag.log
echo "INSTALLATION START >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
ansible-playbook -i ansible/inventory/ibmcloud.local ansible/ibmcloud-bm-deploy.yml 2>&1 | tee -a jetlag.log
echo "INSTALLATION END >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
yes | cp -rf /root/bm/kubeconfig /root/.kube/config
