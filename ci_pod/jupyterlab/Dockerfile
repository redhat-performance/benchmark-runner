FROM fedora:38

ARG JUPYTERLAB_VERSION
ENV JUPYTERLAB_VERSION=$JUPYTERLAB_VERSION
ARG MAINTAINER
ENV MAINTAINER=$MAINTAINER
LABEL maintainer="Your Name <$MAINTAINER>"
ARG OC_VERSION
ENV OC_VERSION="$OC_VERSION"
ARG VIRTCTL_VERSION
ENV VIRTCTL_VERSION="$VIRTCTL_VERSION"

# Install system dependencies
RUN dnf update -y && \
    dnf install -y wget podman curl python3 python3-pip python3-devel nodejs npm && \
    dnf clean all && \
    rm -rf /var/cache/dnf && \
    pip3 install --no-cache-dir jupyterlab=="$JUPYTERLAB_VERSION" benchmark-runner bokeh && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
    # install oc/kubectl client tools for OpenShift/Kubernetes
    curl -L https://github.com/openshift/okd/releases/download/"$OC_VERSION"/openshift-client-linux-"$OC_VERSION".tar.gz -o  "$HOME"/openshift-client-linux-"$OC_VERSION".tar.gz && \
    tar -xzvf  "$HOME"/openshift-client-linux-"$OC_VERSION".tar.gz -C  "$HOME"/ && \
    rm -f "$HOME"/openshift-client-linux-"$OC_VERSION".tar.gz && \
    cp "$HOME"/kubectl /usr/local/bin/kubectl && \
    cp "$HOME"/oc /usr/local/bin/oc && \
    rm -f "$HOME"/kubectl && \
    rm -f "$HOME"/oc && \
    # install virtctl for VNC
    curl -L https://github.com/kubevirt/kubevirt/releases/download/v"$VIRTCTL_VERSION"/virtctl-v"$VIRTCTL_VERSION"-linux-amd64 -o  "$HOME"/virtctl && \
    chmod +x "$HOME"/virtctl && \
    cp "$HOME"/virtctl /usr/local/bin/virtctl && \
    rm -f "$HOME"/virtctl

WORKDIR /notebooks
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
