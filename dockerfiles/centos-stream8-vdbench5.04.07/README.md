# base on https://github.com/bbenshab/vdpod
# vdbench-pod
how I ran it
podman build -t quay.io/ebattat/centos-stream8-vdbench5.04.07-pod:latest . --no-cache
podman push quay.io/ebattat/centos-stream8-vdbench5.04.07-pod:latest

run container for testing:
podman run -v /workload:/workload -e BLOCK_SIZES=4,64,128  -e IO_OPERATION=write,write,write -e IO_THREADS=1,1,1  -v /root/vdbench-pod:/vdbench/config -it quay.io/ebattat/centos-stream8-vdbench5.04.07-pod:latest
