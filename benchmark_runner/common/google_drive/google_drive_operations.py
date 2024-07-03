
import os
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from benchmark_runner.common.logger.logger_time_stamp import logger  # Added logger import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveOperations:
    """
    This class is for Google Drive operations and requires the following:

    1. credentials.json - Obtain from the "Google Cloud Console" under "APIs & Services" > "Credentials" > "Create Credentials" and select "OAuth 2.0 Client ID".
    2. token.json - This is generated automatically. If a browser is not available, copy the token from a machine with a browser.
    """
    def __init__(self):
        """
        Initializes GoogleDriveOperations with authentication.
        """
        self.creds = self.authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

    def authenticate(self):
        """
        Authenticates and returns credentials using token.json or interactive login.
        :return: Credentials object
        """
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        return creds

    def list_files_in_folder(self, folder_id, level=0):
        """
        Recursively lists files and folders in a specified Google Drive folder.
        :param folder_id: The ID of the folder to list.
        :param level: Current recursion level (default is 0).
        :return: List of file and folder metadata dictionaries.
        """
        items = []
        page_token = None
        while True:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token
            ).execute()

            items.extend(results.get('files', []))
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break

        for item in items:
            indent = '  ' * level
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                logger.info(f"{indent}Folder: {item['name']} ({item['id']})")
                self.list_files_in_folder(item['id'], level + 1)
            else:
                logger.info(f"{indent}File: {item['name']} ({item['id']})")

        return items

    def list_folders_and_files_in_shared_drive(self, shared_drive_id):
        """
        Lists all folders and files within a specified Google Drive shared drive.
        :param shared_drive_id: The ID of the shared drive to list.
        """
        try:
            logger.info(f'Folders and Files in shared drive with ID {shared_drive_id}:')
            self.list_files_in_folder(shared_drive_id)
            logger.info("Folder and file listing successful!")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def find_existing_file(self, file_name, shared_drive_id):
        """
        Finds an existing file in a specified Google Drive shared drive.
        :param file_name: The name of the file to find.
        :param shared_drive_id: The ID of the shared drive to search.
        :return: File metadata dictionary if found, otherwise None.
        """
        try:
            all_files = self.list_files_in_folder(shared_drive_id)
            for file in all_files:
                if file['name'] == file_name:
                    return file
            return None
        except Exception as e:
            logger.error(f"An error occurred while searching for the file: {e}")
            return None

    def upload_file(self, file_path, shared_drive_id):
        """
        Uploads a file to a specified Google Drive shared drive and override if exist
        :param file_path: The local path of the file to upload.
        :param shared_drive_id: The ID of the shared drive to upload the file to.
        """
        try:
            file_name = os.path.basename(file_path)
            existing_file = self.find_existing_file(file_name, shared_drive_id)
            media = MediaFileUpload(file_path)

            if existing_file:
                file_id = existing_file['id']
                file = self.service.files().update(
                    fileId=file_id,
                    media_body=media,
                    supportsAllDrives=True,
                    fields='id'
                ).execute()
                logger.info(f"File '{file_name}' updated successfully in shared drive with ID: {shared_drive_id}")
            else:
                file_metadata = {
                    'name': file_name,
                    'parents': [shared_drive_id]
                }
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    supportsAllDrives=True,
                    fields='id'
                ).execute()
                logger.info(f"File '{file_name}' uploaded successfully to shared drive with ID: {shared_drive_id}")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
