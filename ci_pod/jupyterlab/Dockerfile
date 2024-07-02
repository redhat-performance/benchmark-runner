FROM fedora:38

ARG JUPYTERLAB_VERSION
ENV JUPYTERLAB_VERSION=$JUPYTERLAB_VERSION
ARG MAINTAINER
ENV MAINTAINER=$MAINTAINER
LABEL maintainer="Your Name <$MAINTAINER>"
ARG OCP_CLIENT_VERSION
ENV OCP_CLIENT_VERSION="$OCP_CLIENT_VERSION"
ARG VIRTCTL_VERSION
ENV VIRTCTL_VERSION="$VIRTCTL_VERSION"

# Install system dependencies
RUN dnf update -y && \
    dnf install -y wget podman curl python3 python3-pip python3-devel nodejs npm jq && \
    dnf clean all && \
    rm -rf /var/cache/dnf && \
    # benchmark-runner should run before jupyterlab due to dependency conflicts with it
    pip3 install --no-cache-dir --upgrade --force-reinstall benchmark-runner && \
    # Install JupyterLab and other Python dependencies
    pip3 install --no-cache-dir jupyterlab=="$JUPYTERLAB_VERSION" bokeh  && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
    # Install oc/kubectl client tools for OpenShift/Kubernetes
    curl -L "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$OCP_CLIENT_VERSION/openshift-client-linux-$OCP_CLIENT_VERSION.tar.gz" -o "/tmp/openshift-client-linux-$OCP_CLIENT_VERSION.tar.gz" && \
    tar -xzvf "/tmp/openshift-client-linux-$OCP_CLIENT_VERSION.tar.gz" -C /tmp/ && \
    cp /tmp/kubectl /usr/local/bin/kubectl && \
    cp /tmp/oc /usr/local/bin/oc && \
    rm -rf /tmp/* && \
    # Install virtctl for VNC
    curl -L "https://github.com/kubevirt/kubevirt/releases/download/v$VIRTCTL_VERSION/virtctl-v$VIRTCTL_VERSION-linux-amd64" -o "/usr/local/bin/virtctl" && \
    chmod +x /usr/local/bin/virtctl

WORKDIR /notebooks
EXPOSE 8888

#CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
# Copy script into the container
COPY generate_summary_report.sh /usr/local/bin/generate_summary_report.sh
RUN chmod +x /usr/local/bin/generate_summary_report.sh
# Run JupyterLab and generate summary report
CMD ["sh", "/usr/local/bin/generate_summary_report.sh"]
