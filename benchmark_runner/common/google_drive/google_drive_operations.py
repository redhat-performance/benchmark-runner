
import os
import time

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from benchmark_runner.common.logger.logger_time_stamp import logger  # Added logger import
from benchmark_runner.common.google_drive.google_drive_exceptions import FolderNotCreated
# Define the scope
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveOperations:
    """
    This class is for Google Drive operations and requires the following:

    1. credentials.json - Obtain from the "Google Cloud Console" under "APIs & Services" > "Credentials" > "Create Credentials" and select "OAuth 2.0 Client ID".
    2. token.json - This is generated automatically. If a browser is not available, copy the token from a machine with a browser.
    """
    def __init__(self, google_drive_path: str, google_drive_token_file: str, google_drive_credentials_file: str, google_drive_shared_drive_id: str):
        """
        Initializes GoogleDriveOperations with authentication.
        """
        self._google_drive_token = google_drive_token_file  # Read token from file
        self._google_drive_credentials = google_drive_credentials_file  # Read credentials from file
        self._google_drive_shared_drive_id = google_drive_shared_drive_id
        self._google_drive_path = google_drive_path
        self.creds = self.authenticate()
        self.service = build('drive', 'v3', credentials=self.creds)

    def authenticate(self):
        creds = None
        # Load credentials from token.json if it exists
        if os.path.exists(self._google_drive_token):
            creds = Credentials.from_authorized_user_file(self._google_drive_token, SCOPES)
        # If credentials are not valid or do not exist, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self._google_drive_credentials, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self._google_drive_credentials, 'w') as token_file:
                token_file.write(creds.to_json())
        return creds

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

    def get_folder_id(self, folder_names, shared_drive_id):
        """
        Finds the ID of a nested folder structure in the specified shared drive.
        :param folder_names: A list of folder names to traverse.
        :param shared_drive_id: The ID of the shared drive.
        :return: The ID of the innermost folder if the full path exists, else None.
        """
        parent_id = shared_drive_id

        for folder_name in folder_names:
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
            response = self.service.files().list(
                q=query,
                supportsAllDrives=True,
                fields='files(id)',
                spaces='drive'
            ).execute()

            folders = response.get('files', [])
            if folders:
                # Folder exists, move to the next level
                parent_id = folders[0]['id']
            else:
                # If any folder in the path doesn't exist, return None
                return None

        return parent_id

    def create_folder_at_path(self, folder_path, parent_folder_id):
        """
        Creates folders along a specified path in Google Drive and returns the ID of the last folder.
        :param folder_path: The path of folders to create, e.g., '2024/09/15/10'.
        :param parent_folder_id: The ID of the parent folder where the path starts.
        :return: The ID of the last folder in the path if successful, otherwise None.
        """
        for folder_name in folder_path.split('/'):
            parent_folder_id = self._find_or_create_folder(folder_name, parent_folder_id)
            if not parent_folder_id:
                return None
        return parent_folder_id

    def _find_or_create_folder(self, folder_name, parent_folder_id):
        """
        Finds a folder by name within a specified parent folder or creates it if not found.
        :param folder_name: The name of the folder to find or create.
        :param parent_folder_id: The ID of the parent folder to search within.
        :return: The ID of the found or newly created folder.
        """
        folder_id = self._find_folder_id(parent_folder_id, folder_name)
        if folder_id:
            return folder_id

        # Folder does not exist, create it
        return self.create_folder(folder_name, parent_folder_id)

    def create_folder(self, folder_name, parent_folder_id):
        """
        Creates a new folder in the specified parent folder.
        :param folder_name: The name of the new folder to create.
        :param parent_folder_id: The ID of the parent folder where the new folder will be created.
        :return: The ID of the newly created folder if successful, otherwise None.
        """
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return folder.get('id')
        except Exception as e:
            logger.error(f"Error creating folder '{folder_name}': {e}")
            return None

    def _find_folder_id(self, parent_folder_id, folder_name, max_retries=3, delay=5):
        """
        Finds a folder ID by name within a specified parent folder, with retry handling.

        :param parent_folder_id: The ID of the parent folder to search within.
        :param folder_name: The name of the folder to find.
        :param max_retries: The maximum number of retry attempts.
        :param delay: The delay (in seconds) between retries.
        :return: The ID of the folder if found, otherwise None.
        """
        for attempt in range(max_retries):
            try:
                response = self.service.files().list(
                    q=f"'{parent_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    pageSize=100,
                    fields="files(id, name)"
                ).execute()
                folders = response.get('files', [])
                if folders:
                    return folders[0]['id']
            except HttpError as e:
                if e.resp.status in [403, 404]:  # Permanent errors (e.g., permission denied)
                    logger.error(f"Permission error or folder not found: {e}")
                    break  # No point in retrying
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed with error {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed after {max_retries} attempts: {e}")
                    raise

        return None  # Explicit return if folder is not found

    def get_folder_id_by_path(self, folder_path, parent_folder_id):
        """
        Checks if a folder path exists in Google Drive and returns the ID of the last folder in the path.
        :param folder_path: The path of folders to check, e.g., '2024/09/15'.
        :param parent_folder_id: The ID of the parent folder where the search starts.
        :return: The ID of the last folder in the path if it exists, otherwise None.
        """
        folder_names = folder_path.split('/')
        current_parent_id = parent_folder_id

        for folder_name in folder_names:
            folder_id = self._find_folder_id(current_parent_id, folder_name)
            if folder_id:
                current_parent_id = folder_id
            else:
                # Folder in path does not exist
                return None

        return current_parent_id

    def is_folder_name_exists(self, folder_id, target_folder_name):
        """
        Recursively checks if a folder with the specified name exists in a given Google Drive folder.
        :param folder_id: The ID of the folder to start the search.
        :param target_folder_name: The name of the folder to find.
        :return: True if the folder exists, otherwise False.
        """
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

            items = results.get('files', [])
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    if item['name'] == target_folder_name:
                        return item['id']
                    # Recursively check in the subfolders
                    if self.is_folder_name_exists(item['id'], target_folder_name):
                        return item['id']

            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break

        return False

    def get_drive_folder_url(self, folder_path, parent_folder_id):
        """
        Retrieves the Google Drive folder URL based on the folder path without uploading a file.
        :param folder_path: The folder path to retrieve or create.
        :param parent_folder_id: The parent folder ID where the folder path begins.
        :return: The Google Drive URL for the folder.
        """
        # Check if the folder exists in the specified path
        folder_id = self.get_folder_id_by_path(folder_path, parent_folder_id)

        if folder_id:
            # Folder exists, return the folder URL
            folder_url = f"{self._google_drive_path}/{folder_id}"
            return folder_url

    def create_drive_folder_url(self, folder_path, parent_folder_id, retries=3, delay=5):
        """
         Create folder if it doesn't exist. Retries in case of failure.
        :param folder_path: The full folder path to retrieve or create.
        :param parent_folder_id: The starting parent folder ID.
        :param retries: Number of retry attempts on failure.
        :param delay: Initial delay between retries in seconds.
        :return: The Google Drive URL for the folder, or None on failure.
        """
        attempt = 1
        while attempt <= retries:
            folder_id = self.get_folder_id_by_path(folder_path, parent_folder_id)
            if folder_id:
                logger.debug(f"Folder already exists: {folder_path}")
                break

            logger.warning(f"Folder not found. Attempting to create it (Attempt {attempt}/{retries}).")
            try:
                folder_id = self.create_folder_at_path(folder_path, parent_folder_id)
                if folder_id:
                    logger.info(f"Successfully created folder: {folder_path}")
                    break
            except Exception as e:
                logger.error(f"Failed to create folder on attempt {attempt} due to: {e}")
                raise FolderNotCreated(folder_path)

            if attempt < retries:
                wait_time = delay * (2 ** (attempt - 1))
                logger.warning(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

            attempt += 1

        if not folder_id:
            error_msg = f"Unable to create or find the folder path after {retries} attempts: {folder_path}"
            logger.error(error_msg)
            raise FolderNotCreated(folder_path)

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
        Uploads a file to a specified Google Drive shared drive and returns the Google Drive folder URL.
        :param file_path: The local path of the file to upload.
        :param shared_drive_id: The ID of the shared drive to upload the file to.
        :return: The Google Drive URL for the folder containing the uploaded file.
        """
        try:
            file_name = os.path.basename(file_path)
            existing_file = self.find_existing_file(file_name, shared_drive_id)
            media = MediaFileUpload(file_path)

            if existing_file:
                file_id = existing_file['id']
                self.service.files().update(
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
                file_id = file.get('id')
                logger.info(f"File '{file_name}' uploaded successfully to shared drive with ID: {shared_drive_id}")

            # Return the Google Drive URL for the folder containing the uploaded file
            folder_url = f"{self._google_drive_path}/{shared_drive_id}"
            return folder_url

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    def upload_file_to_folder(self, file_path: str, folder_path: str, parent_folder_id: str):
        """
        This method uploads file into google drive folder_path and return the folder url
        @param file_path: the file path to upload to google drive
        @param folder_path: google drive folder path
        @param parent_folder_id: the base drive folder
        @return:the folder url
        """
        folder_id = self.get_folder_id_by_path(
            folder_path=folder_path,
            parent_folder_id=parent_folder_id)
        # new path
        if not folder_id:
            folder_id = self.create_folder_at_path(
                folder_path=folder_path,
                parent_folder_id=parent_folder_id)
        return self.upload_file(file_path=file_path, shared_drive_id=folder_id)
