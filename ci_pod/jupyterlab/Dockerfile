FROM fedora:38

ARG JUPYTERLAB_VERSION
ENV JUPYTERLAB_VERSION=$JUPYTERLAB_VERSION
ARG MAINTAINER
ENV MAINTAINER=$MAINTAINER

LABEL maintainer="Your Name <$MAINTAINER>"

# Install system dependencies
RUN dnf update -y && \
    dnf install -y wget podman curl python3 python3-pip python3-devel nodejs npm && \
    dnf clean all && \
    rm -rf /var/cache/dnf && \
    pip3 install --no-cache-dir jupyterlab=="$JUPYTERLAB_VERSION" benchmark-runner && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager

WORKDIR /notebooks
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
