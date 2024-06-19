
class S3OperationsError(Exception):
    """ Base class for all s3 operations error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class S3FileNotUploaded(S3OperationsError):
    """
    This class represents an error indicating that the S3 file was not uploaded
    """
    def __init__(self):
        self.message = "S3 file/object was not uploaded"
        super(S3FileNotUploaded, self).__init__(self.message)


class S3FileNotDownloaded(S3OperationsError):
    """
    This class represents an error indicating that the S3 file could not be downloaded
    """
    def __init__(self):
        self.message = "S3 file/object could not be downloaded"
        super(S3FileNotDownloaded, self).__init__(self.message)


class S3FileNotDeleted(S3OperationsError):
    """
    This class represents an error indicating that the S3 file/object was not deleted
    """
    def __init__(self):
        self.message = "S3 file/object is not deleted"
        super(S3FileNotDeleted, self).__init__(self.message)


class S3KeyNotCreated(S3OperationsError):
    """
    This class represents an error indicating that the S3 key/folder was not created.
    """
    def __init__(self):
        self.message = "S3 folder/key was not created"
        super(S3KeyNotCreated, self).__init__(self.message)


class S3FileNotExist(S3OperationsError):
    """
    This class represents an error indicating that the S3 file/object does not exist
    """
    def __init__(self):
        self.message = "S3 file/object does not exist"
        super(S3FileNotExist, self).__init__(self.message)


class S3FailedCreatePresingedURL(S3OperationsError):
    """
    This class is error that failed to create presigned url
    """
    def __init__(self):
        self.message = "failed to create presigned url"
        super(S3FailedCreatePresingedURL, self).__init__(self.message)
