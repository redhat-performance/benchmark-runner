class GoogleDrive(Exception):
    """ Base class for all ElasticSearch error classes.
        All exceptions raised by the google drive library should inherit from this class. """
    pass


class FolderNotCreated(GoogleDrive):
    """Raised when a folder cannot be created in Google Drive after retries."""
    def __init__(self, folder_path, message=None):
        if message is None:
            message = f"Failed to create folder: {folder_path}"
        super().__init__(message)
        self.folder_path = folder_path
