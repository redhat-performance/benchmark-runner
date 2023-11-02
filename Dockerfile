FROM quay.io/centos/centos:stream8

# benchmark-runner latest version
ARG VERSION

# Update and use not only best candidate packages (avoiding failures)
RUN dnf update -y --nobest

# install make
Run dnf group install -y "Development Tools"

# install podman and jq
Run dnf config-manager --set-enabled powertools \
    && dnf install -y @container-tools \
    && dnf install -y jq

# Prerequisite for Python installation
ARG python_full_version=3.10.8
RUN dnf install openssl-devel bzip2-devel wget libffi-devel -y

# Install Python
RUN wget https://www.python.org/ftp/python/${python_full_version}/Python-${python_full_version}.tgz \
    && tar -xzf Python-${python_full_version}.tgz \
    && cd Python-${python_full_version} \
    && ./configure --enable-optimizations \
    && make altinstall \
    && echo alias python=python3.10 >> ~/.bashrc \
    && rm -rf Python-${python_full_version}.tgz

# install & run benchmark-runner (--no-cache-dir for take always the latest)
RUN python3.10 -m pip --no-cache-dir install --upgrade pip && pip --no-cache-dir install benchmark-runner --upgrade

# install oc/kubectl client tools for OpenShift/Kubernetes
ARG OCP_CLIENT_VERSION="4.14.1"
RUN  curl -L "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_CLIENT_VERSION}/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" -o "/tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" \
     && tar -xzvf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz -C /tmp/ \
     && mv /tmp/kubectl /usr/local/bin/kubectl \
     && mv /tmp/oc /usr/local/bin/oc \
     && rm -rf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz /tmp/kubectl /tmp/oc

# Install virtctl for VNC
ARG virtctl_version="1.0.0"
RUN curl -L "https://github.com/kubevirt/kubevirt/releases/download/v${virtctl_version}/virtctl-v${virtctl_version}-linux-amd64" -o /usr/local/bin/virtctl \
    && chmod +x /usr/local/bin/virtctl

# Activate root alias
RUN source ~/.bashrc

# Create folder for config file (kubeconfig)
RUN mkdir -p ~/.kube

# Create folder for provision private key file (ssh)
RUN mkdir -p ~/.ssh/

# Create folder for run artifacts
RUN mkdir -p /tmp/run_artifacts

# download benchmark-operator to /tmp default path
RUN git clone -b v1.0.2 https://github.com/cloud-bulldozer/benchmark-operator /tmp/benchmark-operator

# download clusterbuster to /tmp default path && install cluster-buster dependency
RUN git clone -b v1.2.2-kata-ci https://github.com/RobertKrawitz/OpenShift4-tools /tmp/OpenShift4-tools \
    && dnf install -y hostname bc procps-ng

# Add main
COPY benchmark_runner/main/main.py /benchmark_runner/main/main.py

CMD [ "python3.10", "/benchmark_runner/main/main.py"]

# oc: https://www.ibm.com/docs/en/fci/6.5.1?topic=steps-setting-up-installation-server
# sudo podman build -t quay.io/ebattat/benchmark-runner:latest . --no-cache
# sudo podman run --rm -it -v /root/.kube/:/root/.kube/ -v /etc/hosts:/etc/hosts --privileged quay.io/ebattat/benchmark-runner:latest /bin/bash
