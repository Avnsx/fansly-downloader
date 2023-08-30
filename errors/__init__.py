"""Errors/Exceptions"""


#region Constants

EXIT_SUCCESS: int = 0
EXIT_ERROR: int = -1
EXIT_ABORT: int = -2
UNEXPECTED_ERROR: int = -3
API_ERROR: int = -4
CONFIG_ERROR: int = -5
DOWNLOAD_ERROR: int = -6
SOME_USERS_FAILED: int = -7
UPDATE_FAILED: int = -10
UPDATE_MANUALLY: int = -11
UPDATE_SUCCESS: int = 1

#endregion

#region Exceptions

class DuplicateCountError(RuntimeError):
    """The purpose of this error is to prevent unnecessary computation or requests to fansly.
    Will stop downloading, after reaching either the base DUPLICATE_THRESHOLD or 20% of total content.

    To maintain logical consistency, users have the option to disable this feature;
    e.g. a user downloads only 20% of a creator's media and then cancels the download, afterwards tries
    to update that folder -> the first 20% will report completed -> cancels the download -> other 80% missing
    """

    def __init__(self, duplicate_count):
        self.duplicate_count = duplicate_count
        self.message = f"Irrationally high rise in duplicates: {duplicate_count}"
        super().__init__(self.message)


class ConfigError(RuntimeError):
    """This error is raised when configuration data is invalid.
    
    Invalid data may have been provided by config.ini or command-line.
    """

    def __init__(self, *args):
        super().__init__(*args)


class ApiError(RuntimeError):
    """This error is raised when the Fansly API yields no or invalid results.

    This may be caused by authentication issues (invalid token),
    invalid user names or - in rare cases - changes to the Fansly API itself.
    """

    def __init__(self, *args):
        super().__init__(*args)


class ApiAuthenticationError(ApiError):
    """This specific error is raised when the Fansly API
    yields an authentication error.

    This may primarily be caused by an invalid token.
    """

    def __init__(self, *args):
        super().__init__(*args)


class ApiAccountInfoError(ApiError):
    """This specific error is raised when the Fansly API
    for account information yields invalid results.

    This may primarily be caused by an invalid user name.
    """

    def __init__(self, *args):
        super().__init__(*args)


class DownloadError(RuntimeError):
    """This error is raised when a media item could not be downloaded.

    This may be caused by network errors, proxy errors, server outages
    and so on.
    """

    def __init__(self, *args):
        super().__init__(*args)


class MediaError(RuntimeError):
    """This error is raised when data of a media item is invalid.

    This may be by programming errors or trace back to problems in
    Fansly API calls.
    """

    def __init__(self, *args):
        super().__init__(*args)

#endregion


__all__ = [
    'EXIT_ABORT',
    'EXIT_ERROR',
    'EXIT_SUCCESS',
    'API_ERROR',
    'CONFIG_ERROR',
    'DOWNLOAD_ERROR',
    'SOME_USERS_FAILED',
    'UNEXPECTED_ERROR',
    'UPDATE_FAILED',
    'UPDATE_MANUALLY',
    'UPDATE_SUCCESS',
    'ApiError',
    'ApiAccountInfoError',
    'ApiAuthenticationError',
    'ConfigError',
    'DownloadError',
    'DuplicateCountError',
    'MediaError',
]
