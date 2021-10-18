FROM centos:centos8

# benchmark-runner latest version
ARG VERSION

# Update
RUN dnf update -y

# install make
Run dnf group install -y "Development Tools"

# install python 3.9 - take several minutes
RUN dnf install -y python3.9 \
    && echo alias python=python3.9 >> ~/.bashrc

# install & run benchmark-runner (--no-cache-dir for take always the latest)
RUN python3.9 -m pip --no-cache-dir install --upgrade pip && pip --no-cache-dir install benchmark-runner --upgrade

# install helm
RUN curl -fsSL -o ~/get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod 700 ~/get_helm.sh \
    && ~/./get_helm.sh

# install oc/kubectl client tools for OpenShift/Kubernetes
ARG oc_version=4.7.0-0.okd-2021-05-22-050008
RUN  curl -L https://github.com/openshift/okd/releases/download/${oc_version}/openshift-client-linux-${oc_version}.tar.gz -o  ~/openshift-client-linux-${oc_version}.tar.gz \
     && tar -xzvf  ~/openshift-client-linux-${oc_version}.tar.gz -C  ~/ \
     && rm ~/openshift-client-linux-${oc_version}.tar.gz \
     && cp ~/kubectl /usr/local/bin/kubectl \
     && cp ~/oc /usr/local/bin/oc

# install virtctl for VNC
ARG virtctl_version=0.34.2
RUN curl -L https://github.com/kubevirt/kubevirt/releases/download/v${virtctl_version}/virtctl-v${virtctl_version}-linux-amd64 -o  ~/virtctl \
    && chmod +x ~/virtctl \
    && cp ~/virtctl /usr/local/bin/virtctl

# Activate root alias
RUN source ~/.bashrc

# Create folder for config file (kubeconfig)
RUN mkdir -p ~/.kube

# Create folder for provision private key file (ssh)
RUN mkdir -p ~/.ssh/

# download benchmark-operator
RUN git clone https://github.com/cloud-bulldozer/benchmark-operator

# Add main
COPY benchmark_runner/main/main.py /benchmark_runner/main/main.py

CMD [ "python3.9", "/benchmark_runner/main/main.py"]

# oc: https://www.ibm.com/docs/en/fci/6.5.1?topic=steps-setting-up-installation-server
# sudo podman build -t quay.io/ebattat/benchmark-runner:latest . --no-cache
# sudo podman run --rm -it -v /root/.kube/:/root/.kube/ -v /etc/hosts:/etc/hosts --privileged quay.io/ebattat/benchmark-runner:latest /bin/bash
