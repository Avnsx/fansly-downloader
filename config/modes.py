"""Download Modes"""


from enum import StrEnum, auto


class DownloadMode(StrEnum):
    NOTSET = auto()
    COLLECTION = auto()
    MESSAGES = auto()
    NORMAL = auto()
    SINGLE = auto()
    TIMELINE = auto()
