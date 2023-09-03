"""Program Downloading State Management"""


from dataclasses import dataclass, field
from pathlib import Path

from .types import DownloadType


@dataclass
class DownloadState(object):
    #region Fields

    # Mandatory Field
    creator_name: str

    download_type: DownloadType = DownloadType.NOTSET
    
    # Creator state
    creator_id: str | None = None
    following: bool = False
    subscribed: bool = False

    base_path: Path | None = None
    download_path: Path | None = None

    # Counters
    pic_count: int = 0
    vid_count: int = 0
    duplicate_count: int = 0

    total_timeline_pictures: int = 0
    total_timeline_videos: int = 0

    # History
    recent_audio_media_ids: set = field(default_factory=set)
    recent_photo_media_ids: set = field(default_factory=set)
    recent_video_media_ids: set = field(default_factory=set)
    recent_audio_hashes: set = field(default_factory=set)
    recent_photo_hashes: set = field(default_factory=set)
    recent_video_hashes: set = field(default_factory=set)

    #endregion

    #region Methods

    def download_type_str(self) -> str:
        """Gets `download_type` as a string representation."""
        return str(self.download_type).capitalize()

    #endregion
