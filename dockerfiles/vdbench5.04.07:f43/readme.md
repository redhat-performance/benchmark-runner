$ git clone https://github.com/ebattat/vdpod
cp Dockerfile vdpod/Dockerfile
$ cd vdpod
podman build -t quay.io/benchmark-runner/vdbench5.04.07:f43 . --no-cache
