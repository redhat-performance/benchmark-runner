FROM quay.io/centos/centos:stream9

# Update and use not only best candidate packages (avoiding failures)
RUN dnf update -y --nobest

# Install development tools and necessary dependencies
RUN dnf group install -y "Development Tools" \
    && dnf install -y podman jq

# Prerequisite for Python installation
ARG python_full_version=3.12.3
RUN dnf install -y openssl-devel bzip2-devel wget libffi-devel

# Install Python
RUN wget https://www.python.org/ftp/python/${python_full_version}/Python-${python_full_version}.tgz \
    && tar -xzf Python-${python_full_version}.tgz \
    && cd Python-${python_full_version} \
    && ./configure --enable-optimizations \
    && make altinstall \
    && echo alias python=python3.12 >> ~/.bashrc \
    && rm -rf Python-${python_full_version}.tgz

# install & run benchmark-runner (--no-cache-dir for take always the latest)
RUN python3.12 -m pip install --upgrade pip && python3.12 -m pip install --upgrade benchmark-runner

# Passed dynamically
ARG OCP_CLIENT_VERSION
RUN  curl -L "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OCP_CLIENT_VERSION}/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" -o "/tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz" \
     && tar -xzvf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz -C /tmp/ \
     && mv /tmp/kubectl /usr/local/bin/kubectl \
     && mv /tmp/oc /usr/local/bin/oc \
     && rm -rf /tmp/openshift-client-linux-${OCP_CLIENT_VERSION}.tar.gz /tmp/kubectl /tmp/oc

# Passed dynamically
ARG VIRTCTL_VERSION
RUN curl -L "https://github.com/kubevirt/kubevirt/releases/download/v${VIRTCTL_VERSION}/virtctl-v${VIRTCTL_VERSION}-linux-amd64" -o /usr/local/bin/virtctl \
    && chmod +x /usr/local/bin/virtctl

# Activate root alias
RUN source ~/.bashrc

# Create necessary directories with the correct permissions
RUN mkdir -p ~/.kube ~/.ssh /tmp/run_artifacts

# download benchmark-operator to /tmp default path
RUN git clone -b v1.0.4 https://github.com/cloud-bulldozer/benchmark-operator /tmp/benchmark-operator

# download clusterbuster to /tmp default path && install cluster-buster dependency
RUN git clone -b v1.2.2-kata-ci https://github.com/RobertKrawitz/OpenShift4-tools /tmp/OpenShift4-tools \
    && dnf install -y hostname bc procps-ng

# Cleanup to reduce image size
RUN dnf clean all && rm -rf /var/cache/dnf

# Add main
COPY benchmark_runner/main/main.py /benchmark_runner/main/main.py

CMD [ "python3.12", "/benchmark_runner/main/main.py"]

# How to build the Dockerfile ?
# sudo podman build --build-arg OCP_CLIENT_VERSION=$OCP_CLIENT_VERSION--build-arg VIRTCTL_VERSION=$VIRTCTL_VERSION -t quay.io/benchmark-runner/benchmark-runner:latest . --no-cache
# sudo podman run --rm -it -v /root/.kube/:/root/.kube/ -v /etc/hosts:/etc/hosts --privileged quay.io/benchmark-runner/benchmark-runner:latest /bin/bash
