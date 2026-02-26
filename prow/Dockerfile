FROM quay.io/centos/centos:stream10

ARG python_version=3.14
ARG OCP_CLIENT_VERSION=4.21.2
ARG VIRTCTL_VERSION=1.7.0
ARG BENCHMARK_OPERATOR_VERSION=v1.0.4
ARG OPENSHIFT4_TOOLS_VERSION=v1.2.2-kata-ci

ENV PYTHON_VERSION=${python_version}

COPY hack/get_latest_python_patch.py /tmp/get_latest_python_patch.py
RUN python_patch=$(python3 /tmp/get_latest_python_patch.py ${python_version}) \
    && python_full_version=${python_version}.${python_patch} \
    && dnf update -y --nobest \
    && dnf group install -y "Development Tools" \
    && dnf install -y podman jq openssl-devel bzip2-devel wget libffi-devel hostname bc procps-ng \
    && wget https://www.python.org/ftp/python/${python_full_version}/Python-${python_full_version}.tgz \
    && tar -xzf Python-${python_full_version}.tgz \
    && cd Python-${python_full_version} \
    && ./configure --enable-optimizations \
    && make altinstall \
    && echo alias python=python${python_version} >> ~/.bashrc \
    && cd .. \
    && rm -rf Python-${python_full_version} Python-${python_full_version}.tgz \
    && python${python_version} -m pip install --upgrade pip \
    && python${python_version} -m pip install --upgrade benchmark-runner \
    && curl -L "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_CLIENT_VERSION}/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" -o "/tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" \
    && tar -xzf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz -C /usr/local/bin kubectl oc \
    && rm /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz \
    && curl -L "https://github.com/kubevirt/kubevirt/releases/download/v${VIRTCTL_VERSION}/virtctl-v${VIRTCTL_VERSION}-linux-amd64" -o /usr/local/bin/virtctl \
    && chmod +x /usr/local/bin/virtctl \
    && mkdir -p ~/.kube ~/.ssh /tmp/run_artifacts \
    && git clone -b ${BENCHMARK_OPERATOR_VERSION} https://github.com/cloud-bulldozer/benchmark-operator /tmp/benchmark-operator \
    && git clone -b ${OPENSHIFT4_TOOLS_VERSION} https://github.com/RobertKrawitz/OpenShift4-tools /tmp/OpenShift4-tools \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Add main
COPY benchmark_runner/main/main.py /benchmark_runner/main/main.py
