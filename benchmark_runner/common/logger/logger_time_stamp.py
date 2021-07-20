from functools import wraps
import datetime
import time

from benchmark_runner.common.logger.init_logger import logger, get_log_path
from benchmark_runner.common.logger.logger_exceptions import MethodError
datetime_format = '%Y-%m-%d %H:%M:%S'


def logger_time_stamp(method):
    """
    This method log every method with its parameters
    """
    @wraps(method)  # solve method help doc
    def method_wrapper(*args, **kwargs):
        time_start = time.time()
        date_time_start = datetime.datetime.now().strftime(datetime_format)
        try:
            logger.info(f'Method name: {method.__name__} {kwargs} , Start time: {date_time_start} ')
            result = method(*args, **kwargs)
            time_end = time.time()
            date_time_end = datetime.datetime.now().strftime(datetime_format)
            total_time = time_end - time_start
            total_time_str = f'Total time: {round(total_time, 2)} sec'
            logger.info(f'Method name: {method.__name__} , End time: {date_time_end} , {total_time_str}')
        except Exception as err:
            time_end = time.time()
            total_time = time_end - time_start
            date_time_end = datetime.datetime.now().strftime(datetime_format)
            logger.error(f'Method name: {method.__name__} , End time with errors: {date_time_end} , Total time: {round(total_time, 2)} sec')
            raise err  # MethodError(method.__name__, err)

        return result
    return method_wrapper
