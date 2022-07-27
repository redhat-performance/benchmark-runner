
## Inspect Prometheus Metrics

For Inspect Prometheus Metrics use @prometheus_metrics decorator.

For using default metrics benchmark_runner.common.prometheus.metrics-default.yaml:
[This will collect the metric for run() method]
```
from benchmark_runner.common.prometheus.prometheus_metrics import prometheus_metrics

@prometheus_metrics
def run():
    print('sleep 30 sec')
    time.sleep(30)
run()
```

For using custom metrics file, pass it as argument to decorator:
[This will collect custom metrics for run() method]
```
current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_full_path = os.path.join(current_dir, 'metrics.yaml')


@prometheus_metrics(yaml_full_path=yaml_full_path)
def run():
    print('sleep 30 sec')
    time.sleep(30)
run()
```

## Inspect Prometheus Snapshots

The CI jobs store snapshots of the Prometheus database for each run as part of the artifacts.  Within the artifact directory is a Prometheus snapshot directory named:

```
promdb-YYYY_MM_DDTHH_mm_ss+0000_YYYY_MM_DDTHH_mm_ss+0000.tar
```

The timestamps are for the start and end of the metrics capture; they
are stored in UTC time (`+0000`).  It is possible to run containerized
Prometheus on it to inspect the metrics.  *Note that Prometheus
requires write access to its database, so it will actually write to
the snapshot.* So for example if you have downloaded artifacts for a
run named `hammerdb-vm-mariadb-2022-01-04-08-21-23` and the Prometheus
snapshot within is named
`promdb_2022_01_04T08_21_52+0000_2022_01_04T08_45_47+0000`, you could run as follows:

```
$ local_prometheus_snapshot=/hammerdb-vm-mariadb-2022-01-04-08-21-23/promdb_2022_01_04T08_21_52+0000_2022_01_04T08_45_47+0000
$ chmod -R g-s,a+rw "$local_prometheus_snapshot"
$ sudo podman run --rm -p 9090:9090 -uroot -v "$local_prometheus_snapshot:/prometheus" --privileged prom/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --storage.tsdb.retention.time=100000d --storage.tsdb.retention.size=1000PB
```

and point your browser at port 9090 on your local system, you can run queries against it, e. g.

```
sum(irate(node_cpu_seconds_total[2m])) by (mode,instance) > 0
```

It is important to use the `--storage.tsdb.retention.time` option to
Prometheus, as otherwise Prometheus may discard the data in the
snapshot.  And note that you must set the time bounds on the
Prometheus query to fit the start and end times as recorded in the
name of the promdb snapshot.
