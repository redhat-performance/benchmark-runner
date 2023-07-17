
import os

# Progress bar
import requests
import ipywidgets as widgets
from tqdm.auto import tqdm

# Display progress bar
from IPython.display import display

# logging
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from typeguard import typechecked


class LogsOperations:
    """
    This class responsible for logs operations
    """
    CHUNK_SIZE = 8192

    def __init__(self, s3_logs_url: str):
        # s3 Logs url is mandatory
        if not s3_logs_url:
            raise ValueError("s3_logs_url is empty")
        self.s3_logs_url = s3_logs_url
        self.filename = self.s3_logs_url.split('/')[-1]
        self.logs_dir = os.path.join(os.getcwd(), 'logs')
        self.log_dir_filename = os.path.join(self.logs_dir, self.filename)

    def cleanup(self):
        """
        This method cleans up existing logs and Prometheus images
        @return:
        """
        # Delete Prometheus container
        os.system('podman rmi -f docker.io/prom/prometheus;')
        # delete logs dir if exist
        if os.path.exists(self.logs_dir):
            os.system(f"rm -rf {self.logs_dir}")

    @typechecked
    def download_s3_logs(self, username: str, password: str):
        """
        This method downloads s3 logs
        @param username:
        @param password:
        @return:
        """
        if not os.path.exists(self.logs_dir):
            os.mkdir(self.logs_dir)

        # create a session with the credentials
        session = requests.Session()
        session.auth = (username, password)

        # download with progress bar
        response = session.get(self.s3_logs_url, stream=True)
        size = int(response.headers.get('Content-Length', 0))

        progress = widgets.IntProgress(description='Downloading', min=0, max=size)
        display(progress)

        with open(os.path.join(self.logs_dir, self.filename), 'wb') as f:
            with tqdm.wrapattr(f, "write", total=size) as fileobj:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        fileobj.write(chunk)
                        progress.value += len(chunk)

        logger.info('Download complete!')

    def untar_and_chmod_logs(self):
        """
        This method untars and sets the chmod for logs directory, and returns the path to the logs directory
        @return:
        """
        logger.info(f'untar download file {self.log_dir_filename}')
        os.system(f"tar -xvf {self.log_dir_filename} -C {self.logs_dir}")

    def get_workload_dir(self):
        """
        This method returns workload directory
        @return:
        """
        workload__directory = [folder for folder in os.listdir(self.logs_dir) if folder.startswith(self.filename.replace('.tar.gz','')) and not '.tar.gz' in folder]
        return os.path.join(self.logs_dir, workload__directory[0])
