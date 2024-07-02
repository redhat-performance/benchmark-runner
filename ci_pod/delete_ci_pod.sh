#!/bin/bash

sudo podman pod rm -f ci_pod
echo "delete images"
sudo podman rmi -f quay.io/mimehta/custom-grafana:latest
sudo podman rmi -f docker.elastic.co/elasticsearch/elasticsearch:7.16.0
sudo podman rmi -f docker.elastic.co/kibana/kibana:7.16.0
sudo podman rmi -f docker.io/library/alpine:3.14
sudo podman rmi -f docker.io/library/ubuntu:20.04
sudo podman rmi -f localhost/flaskci
sudo podman rmi -f localhost/proxyci
sudo podman rmi -f docker.io/library/nginx:latest
sudo podman rmi -f localhost/jupyterlab
sudo podman rmi -f win-nginx
sudo podman rmi -f grafana_perfci
sudo podman pod ls
