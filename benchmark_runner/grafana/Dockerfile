FROM quay.io/centos/centos:stream9

WORKDIR /app

ENV TERRAFORM_VERSION=1.5.4
# Pre-seeded provider directory: terraform init at runtime uses -plugin-dir so
# CI does not depend on registry.terraform.io being reachable.
ENV TF_PLUGIN_DIR=/terraform-plugins

RUN dnf update -y && \
    dnf install -y git go wget unzip && \
    go install github.com/google/go-jsonnet/cmd/jsonnet@latest && \
    go install -a github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb@latest && \
    wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Warm the jsonnet provider into TF_PLUGIN_DIR at build time so the runtime
# never has to query the provider registry for packages or checksums.
RUN mkdir -p ${TF_PLUGIN_DIR} /tmp/warm && \
    printf 'terraform {\n  required_providers {\n    jsonnet = {\n      source  = "alxrem/jsonnet"\n      version = ">= 2.2.0"\n    }\n  }\n}\n' > /tmp/warm/main.tf && \
    cd /tmp/warm && \
    terraform init -backend=false && \
    cp -r /tmp/warm/.terraform/providers/* ${TF_PLUGIN_DIR}/ && \
    cd / && rm -rf /tmp/warm

ENV PATH="/root/go/bin:${PATH}"

# -e plus && so a terraform init failure fails the run with its real error
# instead of a misleading downstream "Dashboard JSON content not found".
CMD ["/bin/sh", "-ec", "terraform init -backend=false -plugin-dir=${TF_PLUGIN_DIR} && make && terraform destroy -auto-approve > /dev/null 2>&1"]
