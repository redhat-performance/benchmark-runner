#!/bin/bash
# run as Jenkins user
HOME_PATH="/root"
JETLAG_PATH="$HOME_PATH"/jetlag
CI_POD_PATH="/home/jenkins/perfci/ci_pod"
# This script run jetlag installer
echo "Update version: ansible/vars/all.yml"
source "$HOME_PATH/jetlag/bootstrap.sh"
sudo rm -rf "$HOME_PATH/jetlag/jetlag.log"
sudo rm -rf "$JETLAG_PATH/ci_pod.log"

# Cleanup: Already done in jenkinsfile for avoiding false errors and delete existing container
# sudo podman ps | awk '{print $1}' | xargs -I % sudo podman stop %; sudo podman ps -a | awk '{print $1}' | xargs -I % sudo podman rm %; sudo podman pod ps | awk '{print $1}' | xargs -I % sudo podman pod rm %
#restart haproxy
sudo systemctl start haproxy

echo "fetch jetlag latest version"
git checkout main && git pull origin main

# Setup bastion
ansible-playbook -i ansible/inventory/byol.local ansible/setup-bastion.yml > "$JETLAG_PATH/jetlag.log" 2>&1

echo "Wait 120 seconds until the assisted-service pod is running"
sleep 120

# MNO deploy
ansible-playbook -i ansible/inventory/byol.local ansible/mno-deploy.yml >> "$JETLAG_PATH/jetlag.log" 2>&1

# Run CI_POD
sudo -u jenkins "$CI_POD_PATH/run_ci_pod.sh"

# Temporary - update grafana
sudo -u jenkins /home/jenkins/perfci/grafana_perf_ci/update_data.sh

# Update OCP credentials & verification
cp -f "$HOME_PATH/mno/kubeconfig" "$HOME_PATH/.kube/config"
cp -f "$HOME_PATH/mno/kubeadmin-password" "$HOME_PATH/.kube/kubeadmin-password"
cp -f "$HOME_PATH/mno/kubeconfig" /home/jenkins/.kube/config
cp -f "$HOME_PATH/mno/kubeadmin-password" /home/jenkins/.kube/kubeadmin-password
chown jenkins:jenkins /usr/local/bin/oc
oc login -u kubeadmin -p "$(cat "$HOME_PATH/bm/kubeadmin-password")" | tee -a "$JETLAG_PATH/jetlag.log"
