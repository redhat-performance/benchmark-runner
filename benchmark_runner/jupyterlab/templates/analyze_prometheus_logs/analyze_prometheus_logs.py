
import os
import subprocess

# Open grafana url
from IPython.display import HTML, display

# parse grafana date
import time
from datetime import datetime

# logging
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from typeguard import typechecked

# log operations
from benchmark_runner.jupyterlab.templates.logs_operations.logs_operations import LogsOperations


class AnalyzePrometheusLogs:
    """
    This class analyze prometheus logs
    """
    TIMEOUT = 30
    SLEEP = 3

    def __init__(self, s3_logs_url: str):
        self.logs_operations = LogsOperations(s3_logs_url=s3_logs_url)

    def untar_and_chmod_prometheus_logs(self):
        """
        This method untars and sets the chmod for prometheus logs directory, and returns the path to the prometheus logs directory
        @return: prometheus_logs path
        """
        self.logs_operations.untar_and_chmod_logs()
        promdb_file = [f for f in os.listdir(self.logs_operations.log_dir_filename.split('.')[0]) if f.startswith('promdb')]
        logger.info(
            f"untar prometheus file: {os.path.join(self.logs_operations.logs_dir, self.logs_operations.filename.split('.')[0], promdb_file[0])}")
        os.system(
            f"tar -xvf {os.path.join(self.logs_operations.logs_dir, self.logs_operations.filename.split('.')[0], promdb_file[0])} -C {os.path.join(self.logs_operations.logs_dir, self.logs_operations.filename.split('.')[0])}")
        promdb_file = [f for f in os.listdir(self.logs_operations.log_dir_filename.split('.')[0]) if
                       f.startswith('promdb') and not f.endswith('tar')]
        promdb_dir_path = f"{os.path.join(self.logs_operations.logs_dir, self.logs_operations.filename.split('.')[0], promdb_file[0])}"

        logger.info(f'chmod {promdb_dir_path}')
        os.system(f"chmod -R g-s,a+rw {promdb_dir_path}")
        return promdb_dir_path

    @staticmethod
    @typechecked
    def run_container(image_name: str, command: str):
        """
        This method runs the container and waits until it finishes running
        @param image_name:
        @param command:
        @return:
        """
        cmd = f"podman run --name {image_name} {command}"
        logger.info(f"Running container image {image_name}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        current_wait_time = 0
        while current_wait_time <= AnalyzePrometheusLogs.TIMEOUT:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                time.sleep(AnalyzePrometheusLogs.SLEEP)
                break
            if output:
                logger.info(output.strip())
            time.sleep(AnalyzePrometheusLogs.SLEEP)
            current_wait_time += AnalyzePrometheusLogs.SLEEP

        return_code = process.poll()
        logger.info(f"Container exited with return code {return_code}")
        return return_code

    @staticmethod
    @typechecked
    def open_grafana_dashboard(promdb_dir_path: str, grafana_dashboard_url: str):
        """
        This method opens the Grafana dashboard that is mounted to promdb
        @param promdb_dir_path:
        @param grafana_dashboard_url:
        @return:
        """
        start_time = promdb_dir_path.split('/')[-1].split('+')[:2][0].replace('prom', '').replace('db_', '')
        end_time = promdb_dir_path.split('/')[-1].split('+')[:2][1].replace('prom', '').replace('0000_', '')
        grafana_start_time = datetime.strptime(start_time, "%Y_%m_%dT%H_%M_%S")
        grafana_start_time = int(time.mktime(grafana_start_time.timetuple()) * 1000)
        grafana_end_time = datetime.strptime(end_time, "%Y_%m_%dT%H_%M_%S")
        grafana_end_time = int(time.mktime(grafana_end_time.timetuple()) * 1000)
        grafana_url = f"{grafana_dashboard_url}?orgId=1&from={grafana_start_time}&to={grafana_end_time}"
        logger.info(f"Grafana direct link:: {grafana_url}")
        js_code = f"window.open('{grafana_url}')"
        html_code = f"<script>{js_code}</script>"
        display(HTML(html_code))
