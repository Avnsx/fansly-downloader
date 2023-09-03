"""Class to Represent Media Items"""


from dataclasses import dataclass
from typing import Any

from fansly_downloader.utils.datetime import get_adjusted_datetime


@dataclass
class MediaItem(object):
    """Represents a media item published on Fansly
    eg. a picture or video.
    """
    default_normal_id: int = 0
    default_normal_created_at: int = 0
    default_normal_locations: str | None = None
    default_normal_mimetype: str | None = None
    default_normal_height: int = 0

    media_id: int = 0
    metadata: dict[str, Any] | None = None
    mimetype: str | None = None
    created_at: int = 0
    download_url: str | None = None
    file_extension: str | None = None

    highest_variants_resolution: int = 0
    highest_variants_resolution_height: int = 0
    highest_variants_resolution_url: str | None = None

    is_preview: bool = False


    def created_at_str(self) -> str:
        return get_adjusted_datetime(self.created_at)


    def get_download_url_file_extension(self) -> str | None:
        if self.download_url:
            return self.download_url.split('/')[-1].split('.')[-1].split('?')[0]
        else:
            return None


    def get_file_name(self) -> str:
        """General filename construction & if content is a preview;
        add that into it's filename.
        """
        id = 'id'

        if self.is_preview:
            id = 'preview_id'

        return f"{self.created_at_str()}_{id}_{self.media_id}.{self.file_extension}"
