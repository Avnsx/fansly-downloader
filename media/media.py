"""Media and Fansly Related Utility Functions"""


import json

from . import MediaItem

from download.downloadstate import DownloadState
from textio import print_error


def simplify_mimetype(mimetype: str):
    """Simplify (normalize) the MIME types in Fansly replies
    to usable standards.
    """
    if mimetype == 'application/vnd.apple.mpegurl':
        mimetype = 'video/mp4'

    elif mimetype == 'audio/mp4': # another bug in fansly api, where audio is served as mp4 filetype ..
        mimetype = 'audio/mp3' # i am aware that the correct mimetype would be "audio/mpeg", but we just simplify it

    return mimetype


def parse_variant_metadata(variant_metadata_json: str):
    """Fixes Fansly API's current_variant_resolution height bug."""

    variant_metadata = json.loads(variant_metadata_json)

    max_variant = max(variant_metadata['variants'], key=lambda variant: variant['h'], default=None)

    # if a highest height is not found, we just hope 1080p is available
    if not max_variant:
        return 1080

    # else parse through variants and find highest height
    if max_variant['w'] < max_variant['h']:
        max_variant['w'], max_variant['h'] = max_variant['h'], max_variant['w']

    return max_variant['h']


# TODO: Enums in Python for content_type?
def parse_variants(item: MediaItem, content: dict, content_type: str, media_info: dict): # content_type: media / preview
    """Parse metadata and resolution variants of a Fansly media item.
    
    :param MediaItem item: The media to parse and correct.
    :param dict content: ???
    :param str content_type: "media" or "preview"
    :param dict media_info: ???

    :return: None.
    """
    
    if content.get('locations'):
        location_url: str = content['locations'][0]['location']

        current_variant_resolution = (content['width'] or 0) * (content['height'] or 0)

        if current_variant_resolution > item.highest_variants_resolution \
                and item.default_normal_mimetype == simplify_mimetype(content['mimetype']):

            item.highest_variants_resolution = current_variant_resolution
            item.highest_variants_resolution_height = content['height'] or 0
            item.highest_variants_resolution_url = location_url

            item.media_id = int(content['id'])
            item.mimetype = simplify_mimetype(content['mimetype'])

            # if key-pair-id is not in there we'll know it's the new .m3u8 format, so we construct a generalised url, which we can pass relevant auth strings with
            # note: this url won't actually work, its purpose is to just pass the strings through the download_url variable
            if not 'Key-Pair-Id' in item.highest_variants_resolution_url:
                try:
                    # use very specific metadata, bound to the specific media to get auth info
                    item.metadata = content['locations'][0]['metadata']

                    item.highest_variants_resolution_url = \
                        f"{item.highest_variants_resolution_url.split('.m3u8')[0]}_{parse_variant_metadata(content['metadata'])}.m3u8?ngsw-bypass=true&Policy={item.metadata['Policy']}&Key-Pair-Id={item.metadata['Key-Pair-Id']}&Signature={item.metadata['Signature']}"

                except KeyError:
                    # we pass here and catch below
                    pass

            """
            it seems like the date parsed here is actually the correct date,
            which is directly attached to the content. but posts that could be uploaded
            8 hours ago, can contain images from 3 months ago. so the date we are parsing here,
            might be the date, that the fansly CDN has first seen that specific content and the
            content creator, just attaches that old content to a public post after e.g. 3 months.

            or createdAt & updatedAt are also just bugged out idk..
            note: images would be overwriting each other by filename, if hashing didnt provide uniqueness
            else we would be forced to add randint(-1800, 1800) to epoch timestamps
            """
            try:
                item.created_at = int(content['updatedAt'])

            except Exception:
                item.created_at = int(media_info[content_type]['createdAt'])

    item.download_url = item.highest_variants_resolution_url


def parse_media_info(
            state: DownloadState,
            media_info: dict,
            post_id: str | None=None,
        ) -> MediaItem:
    """Parse media JSON reply from Fansly API."""

    # initialize variables
    #highest_variants_resolution_url, download_url, file_extension, metadata, default_normal_locations, default_normal_mimetype, mimetype =  None, None, None, None, None, None, None
    #created_at, media_id, highest_variants_resolution, highest_variants_resolution_height, default_normal_height = 0, 0, 0, 0, 0
    item = MediaItem()

    # check if media is a preview
    item.is_preview = media_info['previewId'] is not None
    
    # fix rare bug, of free / paid content being counted as preview
    if item.is_preview:
        if media_info['access']:
            item.is_preview = False

    # variables in api "media" = "default_" & "preview" = "preview" in our code
    # parse normal basic (paid/free) media from the default location, before parsing its variants
    # (later on we compare heights, to determine which one we want)
    if not item.is_preview:
        default_details = media_info['media']

        item.default_normal_locations = media_info['media']['locations']
        item.default_normal_id = int(default_details['id'])
        item.default_normal_created_at = int(default_details['createdAt'])
        item.default_normal_mimetype = simplify_mimetype(default_details['mimetype'])
        item.default_normal_height = default_details['height'] or 0

    # if its a preview, we take the default preview media instead
    else:
        default_details = media_info['preview']

        item.default_normal_locations = media_info['preview']['locations']
        item.default_normal_id = int(media_info['preview']['id'])
        item.default_normal_created_at = int(default_details['createdAt'])
        item.default_normal_mimetype = simplify_mimetype(default_details['mimetype'])
        item.default_normal_height = default_details['height'] or 0

    if default_details['locations']:
        item.default_normal_locations = default_details['locations'][0]['location']

    # Variants functions extracted here

    # somehow unlocked / paid media: get download url from media location
    if 'location' in media_info['media']:
        variants = media_info['media']['variants']

        for content in variants:
            # TODO: Check for pass by value/reference error, should this return?
            parse_variants(item, content=content, content_type='media', media_info=media_info)

    # previews: if media location is not found, we work with the preview media info instead
    if not item.download_url and 'preview' in media_info:
        variants = media_info['preview']['variants']

        for content in variants:
            # TODO: Check for pass by value/reference error, should this return?
            parse_variants(item, content=content, content_type='preview', media_info=media_info)

    """
    so the way this works is; we have these 4 base variables defined all over this function.
    parse_variants() will initially overwrite them with values from each contents variants above.
    then right below, we will compare the values and decide which media has the higher resolution. (default populated content vs content from variants)
    or if variants didn't provide a higher resolution at all, we just fall back to the default content
    """
    if \
            all(
                [
                    item.default_normal_height,
                    item.default_normal_locations,
                    item.highest_variants_resolution_height,
                    item.highest_variants_resolution_url,
                ]
            ) and all(
                [
                    item.default_normal_height > item.highest_variants_resolution_height,
                    item.default_normal_mimetype == item.mimetype,
                ]
            ) or not item.download_url:
        # overwrite default variable values, which we will finally return; with the ones from the default media
        item.media_id = item.default_normal_id
        item.created_at = item.default_normal_created_at
        item.mimetype = item.default_normal_mimetype
        item.download_url = item.default_normal_locations

    # due to fansly may 2023 update
    if item.download_url:
        # parse file extension separately 
        item.file_extension = item.get_download_url_file_extension()

        if item.file_extension == 'mp4' and item.mimetype == 'audio/mp3':
            item.file_extension = 'mp3'

        # if metadata didn't exist we need the user to notify us through github, because that would be detrimental
        if not 'Key-Pair-Id' in item.download_url and not item.metadata:
            print_error(f"Failed downloading a video! Please open a GitHub issue ticket called 'Metadata missing' and copy paste this:\n\
                \n\tMetadata Missing\n\tpost_id: {post_id} & media_id: {item.media_id} & creator username: {state.creator_name}\n", 14)
            input('Press Enter to attempt continue downloading ...')
    
    return item
