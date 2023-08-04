# grafonnet generator
FROM quay.io/centos/centos:stream9

WORKDIR /app

RUN dnf update -y && \
    dnf install -y git go wget unzip && \
    go install github.com/google/go-jsonnet/cmd/jsonnet@latest && \
    go install -a github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb@latest

ENV PATH="/root/go/bin:${PATH}"

CMD ["/bin/sh", "-c", "rm -rf jsonnetfile*; jb init; jb install github.com/grafana/grafonnet/gen/grafonnet-latest@main; jsonnet -J vendor main.libsonnet > /app/output.json; rm -rf jsonnetfile*; rm -rf vendor"]