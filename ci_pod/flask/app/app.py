import os
import shutil
import boto3
from pathlib import Path
from flask import Flask, send_file, abort

# Constant parameters
TEMP_DIR = '/tmp/ci_pod_data'
BUCKET = os.path.join(TEMP_DIR, 'BUCKET')
AWS_DEFAULT_REGION = os.path.join(TEMP_DIR, 'AWS_DEFAULT_REGION')
ENDPOINT_URL = os.path.join(TEMP_DIR, 'ENDPOINT_URL')
AWS_ACCESS_KEY_ID = os.path.join(TEMP_DIR, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.path.join(TEMP_DIR, 'AWS_SECRET_ACCESS_KEY')

app = Flask(__name__)


@app.route('/health')
def health():
    """
    This method runs health check
    @return:
    """
    return 'OK'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def flask_download_file(path):
    """
    This method gets path and download file from s3
    @param path:
    @return:
    """

    # show the path after /
    temp = (str(path)).split("/")
    file_name = temp[(len(temp) - 1)]
    list_folder = temp[:-1]
    folder = '/'.join(list_folder)
    store_path = os.path.join(TEMP_DIR, folder)
    os.makedirs(store_path, exist_ok=True)
    s3path = str(path)
    local_path = os.path.join(store_path, file_name)

    # read data from file due to flask limitation to read from environment variable
    bucket = Path(BUCKET).read_text()
    aws_default_region = Path(AWS_DEFAULT_REGION).read_text()
    endpoint_url = Path(ENDPOINT_URL).read_text()
    aws_access_key_id = Path(AWS_ACCESS_KEY_ID).read_text()
    aws_secret_access_key = Path(AWS_SECRET_ACCESS_KEY).read_text()
    try:
        s3_client = boto3.client(service_name='s3',
                                 region_name=aws_default_region,
                                 endpoint_url=endpoint_url,
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)
        s3_client.download_file(Bucket=bucket, Key=s3path, Filename=local_path)
    except Exception as e:
        print("Exception:")
        print(str(e))
        abort(404)

    result = send_file(local_path, as_attachment=True)
    # remove local folder
    shutil.rmtree(store_path)
    return result


if __name__ == "__main__":

    # Create the temp directory if it doesn't exist
    os.makedirs(TEMP_DIR, exist_ok=True)
    # Important: Store environment variables in file due to flask did not recognized environment variables
    Path(BUCKET).write_text(os.environ['BUCKET'])
    Path(AWS_DEFAULT_REGION).write_text(os.environ['AWS_DEFAULT_REGION'])
    Path(ENDPOINT_URL).write_text(os.environ['ENDPOINT_URL'])
    Path(AWS_ACCESS_KEY_ID).write_text(os.environ['AWS_ACCESS_KEY_ID'])
    Path(AWS_SECRET_ACCESS_KEY).write_text(os.environ['AWS_SECRET_ACCESS_KEY'])
    app.run('0.0.0.0', '3002')
