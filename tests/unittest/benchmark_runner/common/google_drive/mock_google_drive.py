import pytest
import tempfile
from unittest.mock import MagicMock, patch
from benchmark_runner.common.google_drive.google_drive_operations import GoogleDriveOperations


def mock_google_drive(func):
    def decorated(*args, **kwargs):
        # Set up the mock Google Drive service
        mock_service = MagicMock()
        mock_files = mock_service.files.return_value
        mock_files.list.return_value.execute.return_value = {
            'files': [
                {'id': '1CcVZmoN4qjEaMrJrYSpzcUIZA5_JmFnM', 'name': 'summary_report_4.15.13_4.16.13.html',
                 'mimeType': 'text/html'},
                {'id': '1dHTHrAHdJljXE_6itAG7FYPqtu07ZyIJ', 'name': 'summary_report_4.15.13_4.16.0-rc.8.html',
                 'mimeType': 'text/html'}
            ]
        }

        # Patch the GoogleDriveOperations to use the mock service
        with patch('benchmark_runner.common.google_drive.google_drive_operations.GoogleDriveOperations.authenticate', return_value=None):
            with patch('benchmark_runner.common.google_drive.google_drive_operations.build', return_value=mock_service):
                google_drive_operations = GoogleDriveOperations(google_drive_path='google_drive_path', credentials_path='credentials.json', token_path='token.json', shared_drive_id='shared_drive_id')
                google_drive_operations.service = mock_service

                return func(google_drive_operations, mock_service, *args, **kwargs)

    return decorated
