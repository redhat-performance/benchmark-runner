|Actions Status| |Coverage Status|

Benchmark-Runner
================

This tool provides a lightweight and flexible framework for running
benchmark workloads on Kubernetes/OpenShift Pod or VM.

This tool support the following workloads:

-  `hammerdb <https://hammerdb.com/>`__: running hammerdb workload on
   the following databases: MSSQL, Mariadb, Postgresql on Pod and VM
   with
   `Configuration <benchmark_runner/common/templates/hammerdb>`__
-  `stressng <https://wiki.ubuntu.com/Kernel/Reference/stress-ng>`__:
   running stressng workload on Pod or VM with
   `Configuration <benchmark_runner/common/templates/stressng>`__
-  `uperf <http://uperf.org/>`__: running uperf workload on Pod or VM
   with
   `Configuration <benchmark_runner/common/templates/uperf>`__

\*\* First Phase: supports `benchmark-operator
workloads <https://github.com/cloud-bulldozer/benchmark-operator>`__

Benchmark-runner grafana dashboard example: |image2|

Reference: \* The benchmark-runner package is located in
`PyPi <https://pypi.org/project/benchmark-runner>`__ \* The
benchmark-runner container image is located in
`Quay.io <https://quay.io/repository/ebattat/benchmark-runner>`__

Documentation
-------------

Documentation is available at
`benchmark-runner.readthedocs.io <benchmark-runner.readthedocs.io>`__

.. figure:: ../media/docker1.png
   :alt: 

***Table of Contents***

.. raw:: html

   <!-- TOC -->

-  `Run workload using Podman or
   Docker <#run-workload-using-podman-or-docker>`__
-  `Run workload in Pod using Kubernetes or
   OpenShift <#run-workload-in-pod-using-kubernetes-or-openshift>`__
-  `Grafana dashboards <#grafana-dashboards>`__
-  `How to add new workload <#how-to-add-new-workload>`__

.. raw:: html

   <!-- /TOC -->

Run workload using Podman or Docker
-----------------------------------

Environment variables description:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**mandatory:** WORKLOAD=$WORKLOAD

Choose one from the following list:

``['stressng_pod', 'stressng_vm','uperf_pod', 'uperf_vm', 'hammerdb_pod_mariadb', 'hammerdb_pod_mssql', 'hammerdb_pod_postgres', 'hammerdb_vm_mariadb', 'hammerdb_vm_mssql', 'hammerdb_vm_postgres']``

**auto:** NAMESPACE=benchmark-operator [ The default namespace is
benchmark-operator ]

**auto:** OCS\_PVC=True [ True=OCS PVC storage, False=Ephemeral storage,
default True ]

**auto:** SYSTEM\_METRICS=True [ True=collect metric, False=not collect
metrics, default True ]

**auto:** RUNNER\_PATH=/ [ The default work space is / ]

**optional:** KUBEADMIN\_PASSWORD=$KUBEADMIN\_PASSWORD

**optional:**
PIN\_NODE\_BENCHMARK\_OPERATOR=$PIN\_NODE\_BENCHMARK\_OPERATOR [node
selector for benchmark operator pod]

**optional:** PIN\_NODE1=$PIN\_NODE1 [node1 selector for running the
workload]

**optional:** PIN\_NODE2=$PIN\_NODE2 [node2 selector for running the
workload, i.e. uperf server and client, hammerdb database and workload]

**optional:** ELASTICSEARCH=$ELASTICSEARCH [ elasticsearch service name]

**optional:** ELASTICSEARCH\_PORT=$ELASTICSEARCH\_PORT

.. code:: sh

    podman run --rm -e WORKLOAD=$WORKLOAD -e KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD -e PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR -e PIN_NODE1=$PIN_NODE1 -e PIN_NODE2=$PIN_NODE2 -e ELASTICSEARCH=$ELASTICSEARCH -e ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT -e log_level=INFO -v $KUBECONFIG:/root/.kube/config --privileged quay.io/ebattat/benchmark-runner:latest

.. figure:: ../media/demo.gif
   :alt: 

Run workload in Pod using Kubernetes or OpenShift
-------------------------------------------------

[TBD]

How to add new workload
-----------------------

see `HOW\_TO.md <HOW_TO.md>`__

.. |Actions Status| image:: https://github.com/redhat-performance/benchmark-runner/workflows/CI/badge.svg
   :target: https://github.com/redhat-performance/benchmark-runner/actions
.. |Coverage Status| image:: https://coveralls.io/repos/github/redhat-performance/benchmark-runner/badge.svg?branch=main
   :target: https://coveralls.io/github/redhat-performance/benchmark-runner?branch=main
.. |image2| image:: ../media/grafana.png
.. |image3| image:: ../media/benchmark-runner-ci-status.png

