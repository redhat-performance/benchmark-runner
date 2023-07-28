# To run a workload with custom parameters through JupyterLab terminal, follow these steps:

1. Open the terminal

```
cd /notebooks/templates/run_workloads
```

2. Clone the repository if not already cloned: 

```
git clone https://github.com/redhat-performance/benchmark-runner
or 
update the repository with "git pull" if already cloned.
```

3. Change the directory to benchmark-runner:

```
cd benchmark-runner
```

4. Run the following command in the terminal:

```
PYTHONPATH=. python3 benchmark_runner/main/main.py "$@"
```
or

```
./run_benchmark.sh arg1 arg2
```

**Optional**: instead of arguments, set environment variables in benchmark_runner/main/environment_variables.py, e.g., ('WORKLOAD', 'vdbench_vm').

**Optional**: For custom workload parameters, configure the templates in benchmark_runner/common/template_operations/templates.


