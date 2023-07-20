# Follow the stops:
# git clone https://github.com/redhat-performance/benchmark-runner
# update environment variables i.e. ('WORKLOAD','vdbench_vm') in benchmark_runner/main/environment_variables.py
# run from benchmark-runner root path
PYTHONPATH=. python3 benchmark_runner/main/main.py "$@"
