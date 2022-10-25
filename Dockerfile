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
ARG python_version=3.10
ARG python_full_version=3.10.8
RUN dnf install openssl-devel bzip2-devel wget -y

# Install Python
RUN wget https://www.python.org/ftp/python/${python_full_version}/Python-${python_full_version}.tgz \
    && tar -xzf Python-${python_full_version}.tgz \
    && cd Python-${python_full_version} \
    && ./configure --enable-optimizations \
    && make altinstall \
    && echo alias python=python${python_version} >> ~/.bashrc \
    && rm -rf Python-${python_full_version}.tgz

# install & run benchmark-runner (--no-cache-dir for take always the latest)
RUN python${python_version} -m pip --no-cache-dir install --upgrade pip && pip --no-cache-dir install benchmark-runner --upgrade

# install oc/kubectl client tools for OpenShift/Kubernetes
ARG oc_version=4.11.0-0.okd-2022-10-15-073651
RUN  curl -L https://github.com/openshift/okd/releases/download/${oc_version}/openshift-client-linux-${oc_version}.tar.gz -o  ~/openshift-client-linux-${oc_version}.tar.gz \
     && tar -xzvf  ~/openshift-client-linux-${oc_version}.tar.gz -C  ~/ \
     && rm -rf ~/openshift-client-linux-${oc_version}.tar.gz \
     && cp ~/kubectl /usr/local/bin/kubectl \
     && cp ~/oc /usr/local/bin/oc \
     && rm -rf ~/kubectl \
     && rm -rf ~/oc

# install virtctl for VNC
ARG virtctl_version=0.52.0
RUN curl -L https://github.com/kubevirt/kubevirt/releases/download/v${virtctl_version}/virtctl-v${virtctl_version}-linux-amd64 -o  ~/virtctl \
    && chmod +x ~/virtctl \
    && cp ~/virtctl /usr/local/bin/virtctl \
    && rm -rf ~/virtctl

# Activate root alias
RUN source ~/.bashrc

# Create folder for config file (kubeconfig)
RUN mkdir -p ~/.kube

# Create folder for provision private key file (ssh)
RUN mkdir -p ~/.ssh/

# Create folder for run artifacts
RUN mkdir -p /tmp/run_artifacts

# download benchmark-operator to /tmp default path
RUN git clone -b v1.0.1 https://github.com/cloud-bulldozer/benchmark-operator /tmp/benchmark-operator

# download clusterbuster to /tmp default path && install cluster-buster dependency
RUN git clone -b v1.1.7-kata-ci https://github.com/RobertKrawitz/OpenShift4-tools /tmp/OpenShift4-tools \
    && dnf install -y hostname bc procps-ng

# Add main
COPY benchmark_runner/main/main.py /benchmark_runner/main/main.py

CMD [ "python${python_version}", "/benchmark_runner/main/main.py"]

# oc: https://www.ibm.com/docs/en/fci/6.5.1?topic=steps-setting-up-installation-server
# sudo podman build -t quay.io/ebattat/benchmark-runner:latest . --no-cache
# sudo podman run --rm -it -v /root/.kube/:/root/.kube/ -v /etc/hosts:/etc/hosts --privileged quay.io/ebattat/benchmark-runner:latest /bin/bash
