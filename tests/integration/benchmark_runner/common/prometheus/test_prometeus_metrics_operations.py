import os
import time
from datetime import datetime

from benchmark_runner.common.prometheus.prometheus_metrics_operations import PrometheusMetricsOperation


def test_get_prometheus_timestamp():
    """
    This method test get prometheus timestamp
    :return: 
    """
    prometheus_metrics_operation = PrometheusMetricsOperation()
    assert prometheus_metrics_operation.get_prometheus_timestamp()
    assert type(prometheus_metrics_operation.get_prometheus_timestamp()) == datetime


def test_init_prometheus():
    """
    This method test_init_prometheus
    :return:
    """
    prometheus_metrics_operation = PrometheusMetricsOperation()
    assert prometheus_metrics_operation.init_prometheus()
    assert type(prometheus_metrics_operation.init_prometheus()) == datetime


def test_finalize_prometheus():
    """
    This method test_finalize_prometheus
    :return:
    """
    prometheus_metrics_operation = PrometheusMetricsOperation()
    assert prometheus_metrics_operation.finalize_prometheus()
    assert type(prometheus_metrics_operation.finalize_prometheus()) == datetime


def test_run_prometheus_query():
    """
    This method test_run_prometheus_queries
    :return:
    """
    prometheus_metrics_operation = PrometheusMetricsOperation()
    prometheus_metrics_operation.init_prometheus()
    time.sleep(70)
    prometheus_metrics_operation.finalize_prometheus()
    assert prometheus_metrics_operation.run_prometheus_query(query='sum(irate(node_cpu_seconds_total[1m])) by (mode,instance) > 0')


def test_run_prometheus_queries():
    """
    This method test_run_prometheus_queries
    :return:
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_full_path = os.path.join(current_dir, 'metrics.yaml')
    prometheus_metrics_operation = PrometheusMetricsOperation()
    prometheus_metrics_operation.init_prometheus()
    time.sleep(70)
    prometheus_metrics_operation.finalize_prometheus()
    assert prometheus_metrics_operation.run_prometheus_queries(query_yaml_file=yaml_full_path)
