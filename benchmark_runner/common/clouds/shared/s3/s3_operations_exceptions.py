
class S3OperationsError(Exception):
    """ Base class for all s3 operations error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class S3FileNotUploaded(S3OperationsError):
    """
    This class is error that s3 file is not uploaded
    """
    def __init__(self):
        self.message = "S3 File is not uploaded"
        super(S3FileNotUploaded, self).__init__(self.message)


class S3FileNotDownloaded(S3OperationsError):
    """
    This class is error that s3 file is not downloaded
    """
    def __init__(self):
        self.message = "S3 File is not downloaded"
        super(S3FileNotDownloaded, self).__init__(self.message)


class S3FileNotDeleted(S3OperationsError):
    """
    This class is error that s3 file is not deleted
    """
    def __init__(self):
        self.message = "S3 File is not deleted"
        super(S3FileNotDeleted, self).__init__(self.message)


class S3KeyNotCreated(S3OperationsError):
    """
    This class is error that s3 key is not created
    """
    def __init__(self):
        self.message = "S3 File is not deleted"
        super(S3KeyNotCreated, self).__init__(self.message)


class S3FileNotExist(S3OperationsError):
    """
    This class is error that s3 file is not exist
    """
    def __init__(self):
        self.message = "S3 File is not exist"
        super(S3FileNotExist, self).__init__(self.message)


class S3FailedCreatePresingedURL(S3OperationsError):
    """
    This class is error that failed to create presigned url
    """
    def __init__(self):
        self.message = "failed to create presigned url"
        super(S3FailedCreatePresingedURL, self).__init__(self.message)