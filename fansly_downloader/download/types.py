"""Download Types"""


from enum import StrEnum, auto


class DownloadType(StrEnum):
    NOTSET = auto()
    COLLECTIONS = auto()
    MESSAGES = auto()
    SINGLE = auto()
    TIMELINE = auto()
