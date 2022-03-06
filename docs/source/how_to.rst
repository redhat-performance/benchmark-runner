
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
