
import tempfile
from unittest.mock import MagicMock, patch
from tests.unittest.benchmark_runner.common.google_drive.mock_google_drive import mock_google_drive


@mock_google_drive
def test_list_files_in_folder(google_drive_operations, mock_google_drive_service):
    """
    Tests listing files in a Google Drive folder.

    @param google_drive_operations: Instance of GoogleDriveOperations.
    """
    # Now call the method to test
    result = google_drive_operations.list_files_in_folder('root_folder_id')

    # Assert the expected results based on the mocked data
    assert len(result) == 2
    assert result[0]['id'] == '1CcVZmoN4qjEaMrJrYSpzcUIZA5_JmFnM'
    assert result[0]['name'] == 'summary_report_4.15.13_4.16.13.html'
    assert result[0]['mimeType'] == 'text/html'
    assert result[1]['id'] == '1dHTHrAHdJljXE_6itAG7FYPqtu07ZyIJ'
    assert result[1]['name'] == 'summary_report_4.15.13_4.16.0-rc.8.html'
    assert result[1]['mimeType'] == 'text/html'


@mock_google_drive
def test_find_existing_file(google_drive_operations, mock_google_drive_service):
    """
    Tests finding an existing file in a Google Drive shared drive.

    @param google_drive_operations: Instance of GoogleDriveOperations.
    @param mock_google_drive_service: Mocked Google Drive service.
    """
    # Now call the method to test
    result = google_drive_operations.find_existing_file('summary_report_4.15.13_4.16.0-rc.8.html', 'shared_drive_id')

    # Assert the expected result
    assert result is not None
    assert result['id'] == '1dHTHrAHdJljXE_6itAG7FYPqtu07ZyIJ'
    assert result['name'] == 'summary_report_4.15.13_4.16.0-rc.8.html'
    assert result['mimeType'] == 'text/html'


@mock_google_drive
def test_upload_file_with_mock(google_drive_operations, mock_google_drive_service):
    """
    Tests uploading a new file to a Google Drive shared drive using a mock for upload_file.

    @param google_drive_operations: Instance of GoogleDriveOperations.
    @param mock_google_drive_service: Mocked Google Drive service.
    """
    # Prepare a temporary file to upload
    with tempfile.NamedTemporaryFile(suffix='.html') as temp_file:
        temp_file_name = temp_file.name.split('/')[-1]  # Extract only the file name

        # Mock the upload_file method to update the mock_service
        def mock_upload_file(file_path, shared_drive_id):
            # Simulate updating the mock_service with the new file entry
            mock_service = google_drive_operations.service
            updated_entry = {'id': 'new_file_id', 'name': temp_file_name, 'mimeType': 'text/html'}
            mock_service.files.return_value.list.return_value.execute.return_value['files'].append(updated_entry)
            return mock_service.files.return_value.list.return_value.execute.return_value['files']

        # Patch the upload_file method with the mock implementation
        google_drive_operations.upload_file = MagicMock(side_effect=mock_upload_file)

        # Call the upload_file method
        returned_files_list = google_drive_operations.upload_file(temp_file.name, 'shared_drive_id')

        # Verify the returned files list
        assert returned_files_list is not None
        assert len(returned_files_list) == 3  # Assuming three files are now in the list after upload

        # Verify that the new file entry exists in the returned files list
        assert any(file['name'] == temp_file_name for file in returned_files_list)
