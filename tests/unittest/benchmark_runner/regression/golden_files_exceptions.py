
class GoldenFileError(Exception):
    """Base class for all exceptions related to golden file checks"""
    pass


class GoldenFileCheckFailed(GoldenFileError):
    """Exception for comparison failures"""
    def __init__(self, miscompare: list, missing: list, unexpected:list, cannot_compare: list):
        sep = "\n    "
        errors = []
        if miscompare is not None and len(miscompare) > 0:
            errors.append(f'The following files failed comparison check:{sep}{sep.join(sorted(miscompare))}')

        if missing is not None and len(missing) > 0:
            errors.append(f'The following files are missing:{sep}{sep.join(sorted(missing))}')

        if unexpected is not None and len(unexpected) > 0:
            errors.append(f'The following unexpected files are present:{sep}{sep.join(sorted(unexpected))}')

        if cannot_compare is not None and len(cannot_compare) > 0:
            errors.append(f'The following files cannot be compared:{sep}{sep.join(sorted(cannot_compare))}')

        error_sep = '\n\n'
        self.message = error_sep.join(errors)
        super(GoldenFileCheckFailed, self).__init__(self.message)
