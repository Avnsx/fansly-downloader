"""Metadata Handling"""


from enum import StrEnum, auto


class MetadataHandling(StrEnum):
    NOTSET = auto()
    ADVANCED = auto()
    SIMPLE = auto()
