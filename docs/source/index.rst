|Actions Status| |Coverage Status|

Benchmark Runner
================

This tool provides a lightweight and flexible framework for running
benchmark workloads on Kubernetes/OpenShift Pod or VM.

This tool support the following workloads:

-  `hammerdb <https://hammerdb.com/>`__: running hammerdb workload on
   the following databases: MSSQL, Mariadb, Postgresql on Pod and VM
   with `Configuration <benchmark_runner/templates/hammerdb>`__
-  `stressng <https://wiki.ubuntu.com/Kernel/Reference/stress-ng>`__:
   running stressng workload on Pod or VM with
   `Configuration <benchmark_runner/templates/stressng>`__
-  `uperf <http://uperf.org/>`__: running uperf workload on Pod or VM
   with `Configuration <benchmark_runner/templates/uperf>`__
-  `vdbench <https://wiki.lustre.org/VDBench/>`__: running vdbench
   workload in a pod with
   `Configuration <benchmark_runner/templates/vdbench>`__

Benchmark-runner grafana dashboard example: |image2|

Reference: \* The benchmark-runner package is located in
`PyPi <https://pypi.org/project/benchmark-runner>`__ \* The
benchmark-runner container image is located in
`Quay.io <https://quay.io/repository/ebattat/benchmark-runner>`__

Documentation is available at
`benchmark-runner.readthedocs.io <https://benchmark-runner.readthedocs.io/en/latest/>`__

|image3|

**Table of Contents**

.. raw:: html

   <!-- TOC -->

   -  `Run workload using Podman or Docker <#run-workload-using-podman-or-docker>`__
   -  `Run workload in Pod using Kubernetes or OpenShift <#run-workload-in-pod-using-kubernetes-or-openshift>`__
   -  `Grafana dashboards <#grafana-dashboards>`__
   -  `Inspect Prometheus Metrics <#inspect-prometheus-metrics>`__
   -  `How to develop in benchmark-runner <#how-to-develop-in-benchmark-runner>`__

.. raw:: html

   <!-- /TOC -->

Run workload using Podman or Docker
-----------------------------------

Environment variables description:

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
metrics, default True ]

**auto:** RUNNER_PATH=/tmp [ The default work space is /tmp ]

**optional:** KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD

**optional:** PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR
[node selector for benchmark operator pod]

**optional:** PIN_NODE1=$PIN_NODE1 [node1 selector for running the
workload]

**optional:** PIN_NODE2=$PIN_NODE2 [node2 selector for running the
workload, i.e. uperf server and client, hammerdb database and workload]

**optional:** ELASTICSEARCH=$ELASTICSEARCH [ elasticsearch service name]

**optional:** ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT

.. code:: sh

   podman run --rm -e WORKLOAD=$WORKLOAD -e KUBEADMIN_PASSWORD=$KUBEADMIN_PASSWORD -e PIN_NODE_BENCHMARK_OPERATOR=$PIN_NODE_BENCHMARK_OPERATOR -e PIN_NODE1=$PIN_NODE1 -e PIN_NODE2=$PIN_NODE2 -e ELASTICSEARCH=$ELASTICSEARCH -e ELASTICSEARCH_PORT=$ELASTICSEARCH_PORT -e log_level=INFO -v $KUBECONFIG:/root/.kube/config --privileged quay.io/ebattat/benchmark-runner:latest

|image4|

Run workload in Pod using Kubernetes or OpenShift
-------------------------------------------------

[TBD]

Grafana dashboards
------------------

There are 3 grafana dashboards templates: 1.
`benchmark-runner-ci-status-report.json <grafana/benchmark-runner-ci-status-report.json>`__
|image5| 2.
`benchmark-runner-report.json <grafana/benchmark-runner-report.json>`__
|image6|

\*\* After importing json in grafana, you need to configure
elasticsearch data source. (for more details: see
`HOW_TO.md <HOW_TO.md>`__)

Inspect Prometheus Metrics
--------------------------

The CI jobs store snapshots of the Prometheus database for each run as
part of the artifacts. Within the artifact directory is a Prometheus
snapshot directory named:

::

   promdb-YYYY_MM_DDTHH_mm_ss+0000_YYYY_MM_DDTHH_mm_ss+0000.tar

The timestamps are for the start and end of the metrics capture; they
are stored in UTC time (``+0000``). It is possible to run containerized
Prometheus on it to inspect the metrics. *Note that Prometheus requires
write access to its database, so it will actually write to the
snapshot.* So for example if you have downloaded artifacts for a run
named ``hammerdb-vm-mariadb-2022-01-04-08-21-23`` and the Prometheus
snapshot within is named
``promdb_2022_01_04T08_21_52+0000_2022_01_04T08_45_47+0000``, you could
run as follows:

::

   $ local_prometheus_snapshot=/hammerdb-vm-mariadb-2022-01-04-08-21-23/promdb_2022_01_04T08_21_52+0000_2022_01_04T08_45_47+0000
   $ chmod -R g-s,a+rw "$local_prometheus_snapshot"
   $ sudo podman run --rm -p 9090:9090 -uroot -v "$local_prometheus_snapshot:/prometheus" --privileged prom/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --storage.tsdb.retention.time=100000d --storage.tsdb.retention.size=1000PB

and point your browser at port 9090 on your local system, you can run
queries against it, e. g.

::

   sum(irate(node_cpu_seconds_total[2m])) by (mode,instance) > 0

It is important to use the ``--storage.tsdb.retention.time`` option to
Prometheus, as otherwise Prometheus may discard the data in the
snapshot. And note that you must set the time bounds on the Prometheus
query to fit the start and end times as recorded in the name of the
promdb snapshot.

How to develop in benchmark-runner
----------------------------------

see `HOW_TO.md <HOW_TO.md>`__

.. |Actions Status| image:: https://github.com/redhat-performance/benchmark-runner/workflows/CI/badge.svg
   :target: https://github.com/redhat-performance/benchmark-runner/actions
.. |Coverage Status| image:: https://coveralls.io/repos/github/redhat-performance/benchmark-runner/badge.svg?branch=main
   :target: https://coveralls.io/github/redhat-performance/benchmark-runner?branch=main
.. |image2| image:: ../../media/grafana.png
.. |image3| image:: ../../media/docker2.png
.. |image4| image:: ../../media/demo.gif
.. |image5| image:: ../../media/benchmark-runner-ci-status.png
.. |image6| image:: ../../media/benchmark-runner-report.png


Benchmark-runner: How to develop ?
==================================

**Table of Contents**

.. raw:: html

   <!-- TOC -->

-  `Benchmark-runner: How to?`_

   -  `Add any new Python code`_
   -  `Update workload, modify parameters to workload, or change
      parameters for any CI job`_
   -  `Add new benchmark operator workload to benchmark runner`_
   -  `Add new custom workload to benchmark runner`_
   -  `Add workload to grafana dashboard`_

      -  `Data template`_

   -  `Monitor and debug workload`_
   -  `Determine the version of benchmark-runner in the current
      container image`_

.. raw:: html

   <!-- /TOC -->

Add any new Python code
-----------------------

If you need to add any new Python code in any directory, you *must*
create an ``__init__.py`` file in that directory if it does not already
exist. If you don’t, that code will not be propagated into the release
package.

To check this, run the following command:

::

   $ ls -l $(git ls-files |grep '\.py$' |grep -v '/__init__\.py$' | xargs dirname | sort -n |uniq | sed 's,$,/__init__.py,') 2>&1 >/dev/null

If there is any output, e. g.

::

   ls: cannot access 'tests/unittest/benchmark_runner/common/template_operations/__init__.py': No such file or directory

you need to create an empty file by that name and ``git add`` it.

Add new workload, modify parameters to workload, or change parameters for any CI job
------------------------------------------------------------------------------------

The unit tests include a check to ensure that the generated .yaml files
do not inadvertently change. This check, located in
``tests/unittest/benchmark_runner/common/templates/test_golden_files.py``,
compares these files against expected files found in
``tests/unittest/benchmark_runner/common/workloads_flavors/golden_files``
and fails if any golden files have been added, modified, or removed.

*If you add or modify any YAML files, you must run the following
commands:*

::

   PYTHONPATH=. python3 tests/unittest/benchmark_runner/common/template_operations/generate_golden_files.py
   git add tests/unittest/benchmark_runner/common/templates/golden_files
   git commit -m "Update golden files"

If you remove any YAML files, you must identify the changed files and
``git rm`` them before committing the result.

The check is run automatically as part of the unit tests; if you want to
run it manually, you can do so as follows. The test should take only a
few seconds to run.

\``\` $ PYTHONPATH=. python3 -m pytest -v
tests/unittest/benchmark_runner/common/template_operations/
============================== test session starts
=============================== platform linux – Python 3.9.5,
pytest-6.2.2, py-1.10.0, pluggy-0.13.1 – /usr/bin/python3 cachedir:
.pytest_cache rootdir: /home/rkrawitz/sandbox/benchmark-r

.. _`Benchmark-runner: How to?`: #benchmark-runner-how-to
.. _Add any new Python code: #add-any-new-python-code
.. _Add new workload, modify parameters to workload, or change parameters for any CI job: #add-new-workload-modify-parameters-to-workload-or-change-parameters-for-any-ci-job
.. _Add new benchmark operator workload to benchmark runner: #add-new-benchmark-operator-workload-to-benchmark-runner
.. _Add new custom workload to benchmark runner: #add-new-custom-workload-to-benchmark-runner
.. _Add workload to grafana dashboard: #add-workload-to-grafana-dashboard
.. _Data template: #data-template
.. _Monitor and debug workload: #monitor-and-debug-workload
.. _Determine the version of benchmark-runner in the current container image: #determine-the-version-of-benchmark-runner-in-the-current-container-image