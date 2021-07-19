FROM centos:centos8

# benchmark-runner latest version
ARG VERSION

# Update
RUN dnf update -y

# install python 3.9 - take several minutes
RUN dnf install -y python3.9 \
    && echo alias python=python3.9 >> ~/.bashrc

# install & run benchmark-runner
RUN python3.9 -m pip --no-cache-dir  install --upgrade pip && pip --no-cache-dir install benchmark-runner==$VERSION

# install oc/kubectl Client tools for OpenShift/Kubernetes
ARG oc_version=4.7.0-0.okd-2021-05-22-050008
RUN  curl -L https://github.com/openshift/okd/releases/download/${oc_version}/openshift-client-linux-${oc_version}.tar.gz -o ~/openshift-client-linux-${oc_version}.tar.gz \
     && tar -xzvf ~/openshift-client-linux-${oc_version}.tar.gz -C ~/ \
     && rm ~/openshift-client-linux-${oc_version}.tar.gz \
     && echo alias oc=~/./oc >> ~/.bashrc \
     && echo alias kubectl=~/./kubectl >> ~/.bashrc

# install virtctl for VNC
ARG virtctl_version=0.34.2
RUN curl -L https://github.com/kubevirt/kubevirt/releases/download/v${virtctl_version}/virtctl-v${virtctl_version}-linux-amd64 -o ~/virtctl \
    && chmod +x ~/virtctl \
    && echo alias virtctl=~/./virtctl >> ~/.bashrc

# Activate alias
RUN . ~/.bashrc

# Create folder for config file (kubeconfig)
RUN mkdir -p ~/.kube

# benchmark-operator
# install helm
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh

# download benchmark-operator
RUN dnf install -y git \
    && git clone https://github.com/cloud-bulldozer/benchmark-operator
#   && cd benchmark-operator/charts/benchmark-operator \
#    && helm install benchmark-operator . -n my-ripsaw --create-namespace
#    && oc adm policy -n my-ripsaw add-scc-to-user privileged -z benchmark-operator

# Add main
ADD benchmark_runner/benchmark_operator/templates /usr/local/benchmark_runner/benchmark_operator/templates/
COPY benchmark_runner/main/main.py /usr/local/benchmark_runner/main.py

CMD [ "python3.9", "/usr/local/benchmark_runner/main.py"]


# oc: https://www.ibm.com/docs/en/fci/6.5.1?topic=steps-setting-up-installation-server
# sudo podman build -t quay.io/ebattat/benchmark-runner:latest . --no-cache
# sudo podman run --rm -it -v /root/.kube/:/root/.kube/ -v /etc/hosts:/etc/hosts --privileged quay.io/ebattat/benchmark-runner:latest /bin/bash
