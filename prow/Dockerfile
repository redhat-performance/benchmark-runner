FROM quay.io/centos/centos:stream9

ARG python_full_version=3.12.3
ARG OCP_CLIENT_VERSION=4.19.1
ARG VIRTCTL_VERSION=1.5.0

RUN dnf clean all && dnf --refresh update -y --nobest \
    && dnf group install -y "Development Tools" \
    && dnf install -y podman jq openssl-devel bzip2-devel wget libffi-devel hostname bc procps-ng \
    && wget https://www.python.org/ftp/python/${python_full_version}/Python-${python_full_version}.tgz \
    && tar -xzf Python-${python_full_version}.tgz \
    && cd Python-${python_full_version} \
    && ./configure --enable-optimizations \
    && make altinstall \
    && echo alias python=python3.12 >> ~/.bashrc \
    && cd .. \
    && rm -rf Python-${python_full_version} Python-${python_full_version}.tgz \
    && python3.12 -m pip install --upgrade pip \
    && python3.12 -m pip install --upgrade benchmark-runner \
    && curl -L "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_CLIENT_VERSION}/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" -o "/tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" \
    && tar -xzvf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz -C /tmp/ \
    && mv /tmp/kubectl /usr/local/bin/kubectl \
    && mv /tmp/oc /usr/local/bin/oc \
    && rm -rf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz /tmp/kubectl /tmp/oc \
    && curl -L "https://github.com/kubevirt/kubevirt/releases/download/v${VIRTCTL_VERSION}/virtctl-v${VIRTCTL_VERSION}-linux-amd64" -o /usr/local/bin/virtctl \
    && chmod +x /usr/local/bin/virtctl \
    && mkdir -p ~/.kube ~/.ssh /tmp/run_artifacts \
    && git clone -b v1.0.4 https://github.com/cloud-bulldozer/benchmark-operator /tmp/benchmark-operator \
    && git clone -b v1.2.2-kata-ci https://github.com/RobertKrawitz/OpenShift4-tools /tmp/OpenShift4-tools \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Add main
COPY benchmark_runner/main/main.py /benchmark_runner/main/main.py
