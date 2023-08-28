FROM quay.io/centos/centos:stream9

WORKDIR /app

ENV TERRAFORM_VERSION=1.5.4

RUN dnf update -y && \
    dnf install -y git go wget unzip && \
    go install github.com/google/go-jsonnet/cmd/jsonnet@latest && \
    go install -a github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb@latest && \
    wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

ENV PATH="/root/go/bin:${PATH}"

CMD ["/bin/sh", "-c", "terraform init; make; terraform destroy -auto-approve > /dev/null 2>&1"]
