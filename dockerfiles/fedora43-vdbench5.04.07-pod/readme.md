$ git clone https://github.com/ebattat/vdpod
cp Dockerfile vdpod/Dockerfile
cp state_signals_responder.py vdpod/state_signals_responder.py
$ cd vdpod
podman build -t quay.io/ebattat/centos-stream9-vdbench5.04.07-pod:latest . --no-cache
