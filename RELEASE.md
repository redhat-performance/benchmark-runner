
## RELEASE NOTES

#### Benchmark-Runner V1.0.63

There is a new stable version for Benchmark-Runner, it includes:

1. Benchmark-Runner new feature support:
   
* Adding support for VM workloads
* Adding support for running Benchmark runner without active Elasticsearch server
* Adding node selector support for Benchmark-Operator pod [PIN_NODE_BENCHMARK_OPERATOR]
* [Github Actions](https://github.com/redhat-performance/benchmark-runner/runs/3169383450?check_suite_focus=true) - adding Azure cluster support for integration and E2E tests
* Install ECK on Azure OpenShift cluster for ElasticSearch support and secured Kibana url.
* [Coveralls](https://coveralls.io/github/redhat-performance/benchmark-runner?branch=main) - adding Pytest coverage.

2. Support major Benchmark-Operator changes:

* Install using make deploy
* Support benchmark-controller-manager pod
* Support UUID per workload
* Support new namespace benchmark-operator instead of my-ripsaw


** [Closed issues](https://github.com/redhat-performance/benchmark-runner/issues?q=is%3Aissue+is%3Aclosed)