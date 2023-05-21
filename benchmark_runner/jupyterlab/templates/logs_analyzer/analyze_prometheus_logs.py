import os

# Progress bar
import subprocess
import requests
import ipywidgets as widgets
from tqdm.auto import tqdm

# Open grafana url
from IPython.display import HTML, display

# parse grafana date
import time
from datetime import datetime

# logging
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AnalyzePrometheusLogs:
    """
    This class analyze prometheus logs
    """
    TIMEOUT = 30
    SLEEP = 3
    CHUNK_SIZE = 8192

    def __init__(self, s3_logs_url: str):
        self.__s3_logs_url = s3_logs_url
        self.__logs_dir = os.path.join(os.path.join(os.getcwd(), 'logs'))
        self.__filename = self.__s3_logs_url.split('/')[-1]
        self.__log_dir_path = os.path.join(self.__logs_dir, self.__filename)

    def cleanup(self):
        """
        This method cleans up existing logs and Prometheus images
        @return:
        """
        # Delete Prometheus container
        os.system('podman rmi -f docker.io/prom/prometheus;')
        # delete logs dir if exist
        if os.path.exists(self.__logs_dir):
            os.system(f"rm -rf {self.__logs_dir}")

    def download_s3_logs(self, username: str, password: str):
        """
        This method downloads s3 logs
        @param username:
        @param password:
        @return:
        """
        if not os.path.exists(self.__logs_dir):
            os.mkdir(self.__logs_dir)

        # create a session with the credentials
        session = requests.Session()
        session.auth = (username, password)

        # download with progress bar
        response = session.get(self.__s3_logs_url, stream=True)
        size = int(response.headers.get('Content-Length', 0))

        progress = widgets.IntProgress(description='Downloading', min=0, max=size)
        display(progress)

        with open(os.path.join(self.__logs_dir, self.__filename), 'wb') as f:
            with tqdm.wrapattr(f, "write", total=size) as fileobj:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        fileobj.write(chunk)
                        progress.value += len(chunk)

        logger.info('Download complete!')

    def untar_and_chmod_prometheus_logs(self):
        """
        This method untars and sets the chmod for Prometheus logs, and returns the path to the 'promdb' directory
        @return:
        """
        logger.info(f'untar download file {self.__log_dir_path}')
        os.system(f"tar -xvf {self.__log_dir_path} -C {self.__logs_dir}")

        promdb_file = [f for f in os.listdir(self.__log_dir_path.split('.')[0]) if f.startswith('promdb')]

        logger.info(f"untar prometheus file: {os.path.join(self.__logs_dir, self.__filename.split('.')[0], promdb_file[0])}")
        os.system(f"tar -xvf {os.path.join(self.__logs_dir, self.__filename.split('.')[0], promdb_file[0])} -C {os.path.join(self.__logs_dir, self.__filename.split('.')[0])}")

        promdb_file = [f for f in os.listdir(self.__log_dir_path.split('.')[0]) if f.startswith('promdb') and not f.endswith('tar')]
        promdb_dir_path = f"{os.path.join(self.__logs_dir, self.__filename.split('.')[0], promdb_file[0])}"

        logger.info(f'chmod {promdb_dir_path}')
        os.system(f"chmod -R g-s,a+rw {promdb_dir_path}")
        return promdb_dir_path

    def run_container(self, image_name, command):
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
        while current_wait_time <= self.TIMEOUT:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                time.sleep(self.SLEEP)
                break
            if output:
                logger.info(output.strip())
            time.sleep(self.SLEEP)
            current_wait_time += self.SLEEP

        return_code = process.poll()
        logger.info(f"Container exited with return code {return_code}")
        return return_code

    def open_grafana_dashboard(self, promdb_dir_path: str, grafana_dashboard_url: str):
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
        if self.__s3_logs_url:
            display(HTML(html_code))
