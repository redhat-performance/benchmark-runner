|Actions Status| |Coverage Status|

Benchmark-Runner
================

This tool provides a lightweight and flexible framework for running
benchmark workloads on Kubernetes/OpenShift Pod or VM.

This tool support the following workloads:

-  `hammerdb`_: running hammerdb workload on the following databases:
   MSSQL, Mariadb, Postgresql on Pod and VM with `Configuration`_
-  `stressng`_: running stressng workload on Pod or VM with
   `Configuration <benchmark_runner/templates/stressng>`__
-  `uperf`_: running uperf workload on Pod or VM with
   `Configuration <benchmark_runner/templates/uperf>`__
-  `vdbench`_: running vdbench workload in a pod with
   `Configuration <benchmark_runner/templates/vdbench>`__

Benchmark-runner grafana dashboard example: |image1|

Reference: \* The benchmark-runner package is located in `PyPi`_ \* The
benchmark-runner container image is located in `Quay.io`_

Documentation
-------------

Documentation is available at `benchmark-runner.readthedocs.io`_

.. image:: media/docker2.png

**Table of Contents**

.. raw:: html

   <!-- TOC -->

-  `Benchmark-Runner`_

   -  `Documentation`_
   -  `Run workload using Podman or Docker`_
   -  `Run workload in Pod using Kubernetes or OpenShift`_
   -  `Grafana dashboards`_
   -  `Inspect Prometheus Metrics`_
   -  `How to develop in benchmark-runner`_

.. raw:: html

   <!-- /TOC -->

Run workload using Podman or Docker
-----------------------------------

Environment variables description:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**mandatory:** WORKLOAD=$WORKLOAD

Choose one from the following list:

``['stressng_pod', 'stressng_vm', 'stressng_kata','uperf_pod', 'uperf_vm', 'uperf_kata', 'hammerdb_pod_mariadb', 'hammerdb_pod_mssql', 'hammerdb_pod_postgres', 'hammerdb_vm_mariadb', 'hammerdb_vm_mssql', 'hammerdb_vm_postgres', 'hammerdb_kata_mariadb', 'hammerdb_kata_mssql', 'hammerdb_kata_postgres', 'vdbench_pod', 'vdbench_kata', 'vdbench_vm']``

**auto:** NAMESPACE=benchmark-operator [ The default namespace is
benchmark-operator ]

**auto:** ODF_PVC=True [ True=ODF PVC storage, False=Ephemeral storage,
default True ]

**auto:** EXTRACT_PROMETHEUS_SNAPSHOT=True [ True=extract Prometheus
snapshot into artifacts, false=don’t, default True ]

**auto:** SYSTEM_METRICS=True [ True=collect metric, False=not collect
metri

.. _hammerdb: https://hammerdb.com/
.. _Configuration: benchmark_runner/templates/hammerdb
.. _stressng: https://wiki.ubuntu.com/Kernel/Reference/stress-ng
.. _uperf: http://uperf.org/
.. _vdbench: https://wiki.lustre.org/VDBench/
.. _PyPi: https://pypi.org/project/benchmark-runner
.. _Quay.io: https://quay.io/repository/ebattat/benchmark-runner
.. _benchmark-runner.readthedocs.io: https://benchmark-runner.readthedocs.io/en/latest/
.. _Benchmark-Runner: #benchmark-runner
.. _Documentation: #documentation
.. _Run workload using Podman or Docker: #run-workload-using-podman-or-docker
.. _Run workload in Pod using Kubernetes or OpenShift: #run-workload-in-pod-using-kubernetes-or-openshift
.. _Grafana dashboards: #grafana-dashboards
.. _Inspect Prometheus Metrics: #inspect-prometheus-metrics
.. _How to develop in benchmark-runner: #how-to-develop-in-benchmark-runner

.. |Actions Status| image:: https://github.com/redhat-performance/benchmark-runner/workflows/CI/badge.svg
   :target: https://github.com/redhat-performance/benchmark-runner/actions
.. |Coverage Status| image:: https://coveralls.io/repos/github/redhat-performance/benchmark-runner/badge.svg?branch=main
   :target: https://coveralls.io/github/redhat-performance/benchmark-runner?branch=main
.. |image1| image:: media/grafana.png