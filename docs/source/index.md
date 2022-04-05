
# Benchmark-Runner

## What is it?

**benchmark-runner** is a containerized Python lightweight and flexible framework for running benchmark workloads 
on Kubernetes/OpenShift runtype kinds Pod, kata and VM.

This framework support the following workloads:

* [hammerdb](https://hammerdb.com/): running hammerdb workload on the following databases: MSSQL, Mariadb, Postgresql on Pod, Kata or VM with [Configuration](benchmark_runner/templates/hammerdb)
* [stressng](https://wiki.ubuntu.com/Kernel/Reference/stress-ng): running stressng workload on Pod, Kata or VM with [Configuration](benchmark_runner/templates/stressng)
* [uperf](http://uperf.org/): running uperf workload on Pod, Kata or VM with [Configuration](benchmark_runner/templates/uperf)
* [vdbench](https://wiki.lustre.org/VDBench/): running vdbench workload on Pod, Kata or VM with [Configuration](benchmark_runner/templates/vdbench)

Benchmark-runner grafana dashboard example:
![](../../media/grafana.png)

Reference:
* The benchmark-runner package is located in [PyPi](https://pypi.org/project/benchmark-runner)
* The benchmark-runner container image is located in [Quay.io](https://quay.io/repository/ebattat/benchmark-runner)

![](../../media/docker2.png)

![](../../media/demo.gif)


<!-- Table of contents -->
```{toctree}
podman
grafana
prometheus
develop
```
