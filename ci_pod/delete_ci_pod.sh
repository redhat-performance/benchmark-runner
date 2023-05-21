podman pod rm -f ci_pod
echo "delete images"
podman rmi -f quay.io/mimehta/custom-grafana:latest
podman rmi -f docker.elastic.co/elasticsearch/elasticsearch:7.16.0
podman rmi -f docker.elastic.co/kibana/kibana:7.16.0
podman rmi -f docker.io/library/alpine:3.14
podman rmi -f docker.io/library/ubuntu:20.04
podman rmi -f localhost/flaskci
podman rmi -f localhost/proxyci
podman rmi -f docker.io/library/nginx:latest
podman rmi -f localhost/jupyterlab
podman pod ls
