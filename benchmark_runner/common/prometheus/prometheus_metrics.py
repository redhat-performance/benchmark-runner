
from functools import wraps

from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.common.prometheus.prometheus_metrics_operations import PrometheusMetricsOperation


def prometheus_metrics(yaml_full_path: str = None):
    """
    This decorator method run prometheus metrics
    :param yaml_full_path: custom metric full path of yaml file [optional]
    :return:
    """
    def prometheus_metrics_internal(method):
        """
        This decorator method is for running prometheus queries and get prometheus metrics
        """
        @wraps(method)  # solve method help doc
        def method_wrapper(*args, **kwargs):
            prometheus_metrics_operation = PrometheusMetricsOperation()
            prometheus_metrics_operation.init_prometheus()
            try:
                result = method(*args, **kwargs)
                prometheus_metrics_operation.finalize_prometheus()
                # run several queries from custom yaml queries file or default yaml queries  file
                prometheus_metrics_operation.run_prometheus_queries(query_yaml_file=yaml_full_path)
                prometheus_metrics_operation.upload_result_to_elastic()
            except Exception as err:
                logger.error(f'error :{err}')
                raise err  # MethodError(method.__name__, err)

            return result
        return method_wrapper
    return prometheus_metrics_internal
