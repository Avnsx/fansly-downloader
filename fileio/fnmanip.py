"""File Name Manipulation Functions"""


import concurrent.futures
import hashlib
import mimetypes
import imagehash
import os
import re
import traceback

from pathlib import Path
from PIL import Image

from config import FanslyConfig
from download.downloadstate import DownloadState
from textio import print_debug, print_error


# turn off for our purpose unnecessary PIL safety features
Image.MAX_IMAGE_PIXELS = None


def extract_media_id(filename: str) -> int | None:
    """Extracts the media_id from an existing file's name."""
    match = re.search(r'_id_(\d+)', filename)

    if match:
        return int(match.group(1))

    return None


def extract_hash_from_filename(filename: str) -> str | None:
    """Extracts the hash from an existing file's name."""
    match = re.search(r'_hash_([a-fA-F0-9]+)', filename)

    if match:
        return match.group(1)

    return None


def add_hash_to_filename(filename: Path, file_hash: str) -> str:
    """Adds a hash to an existing file's name."""
    base_name, extension = str(filename.parent / filename.stem), filename.suffix
    hash_suffix = f"_hash_{file_hash}{extension}"

    # adjust filename for 255 bytes filename limit, on all common operating systems
    max_length = 250

    if len(base_name) + len(hash_suffix) > max_length:
        base_name = base_name[:max_length - len(hash_suffix)]
    
    return f"{base_name}{hash_suffix}"


def add_hash_to_image(state: DownloadState, filepath: Path):
    """Hashes existing images in download directories."""
    try:
        filename = filepath.name

        media_id = extract_media_id(filename)

        if media_id:
            state.recent_photo_media_ids.add(media_id)

        existing_hash = extract_hash_from_filename(filename)

        if existing_hash:
            state.recent_photo_hashes.add(existing_hash)

        else:
            with Image.open(filepath) as img:

                file_hash = str(imagehash.phash(img, hash_size = 16))

                state.recent_photo_hashes.add(file_hash)
                
                new_filename = add_hash_to_filename(Path(filename), file_hash)
                new_filepath = filepath.parent / new_filename

                filepath = filepath.rename(new_filepath)

    except FileExistsError:
        filepath.unlink()

    except Exception:
        print_error(f"\nError processing image '{filepath}': {traceback.format_exc()}", 15)


def add_hash_to_other_content(state: DownloadState, filepath: Path, content_format: str):
    """Hashes audio and video files in download directories."""
    
    try:
        filename = filepath.name

        media_id = extract_media_id(filename)

        if media_id:

            if content_format == 'video':
                state.recent_video_media_ids.add(media_id)

            elif content_format == 'audio':
                state.recent_audio_media_ids.add(media_id)

        existing_hash = extract_hash_from_filename(filename)

        if existing_hash:

            if content_format == 'video':
                state.recent_video_hashes.add(existing_hash)

            elif content_format == 'audio':
                state.recent_audio_hashes.add(existing_hash)

        else:
            h = hashlib.md5()

            with open(filepath, 'rb') as f:
                while (part := f.read(1_048_576)):
                    h.update(part)

            file_hash = h.hexdigest()

            if content_format == 'video':
                state.recent_video_hashes.add(file_hash)

            elif content_format == 'audio':
                state.recent_audio_hashes.add(file_hash)
            
            new_filename = add_hash_to_filename(Path(filename), file_hash)
            new_filepath = filepath.parent / new_filename

            filepath = filepath.rename(new_filepath)

    except FileExistsError:
        filepath.unlink()

    except Exception:
        print_error(f"\nError processing {content_format} '{filepath}': {traceback.format_exc()}", 16)


def add_hash_to_file(config: FanslyConfig, state: DownloadState, file_path: Path) -> None:
    """Hashes a file according to it's file type."""

    mimetype, _ = mimetypes.guess_type(file_path)

    if config.debug:
        print_debug(f"Hashing file of type '{mimetype}' at location '{file_path}' ...")

    if mimetype is not None:

        if mimetype.startswith('image'):
            add_hash_to_image(state, file_path)

        elif mimetype.startswith('video'):
            add_hash_to_other_content(state, file_path, content_format='video')

        elif mimetype.startswith('audio'):
            add_hash_to_other_content(state, file_path, content_format='audio')


def add_hash_to_folder_items(config: FanslyConfig, state: DownloadState) -> None:
    """Recursively adds hashes to all media files in the folder and
    it's sub-folders.
    """

    if state.download_path is None:
        raise RuntimeError('Internal error hashing media files - download path not set.')

    # Beware - thread pools may silently swallow exceptions!
    # https://docs.python.org/3/library/concurrent.futures.html
    with concurrent.futures.ThreadPoolExecutor() as executor:

        for root, _, files in os.walk(state.download_path):
            
            if config.debug:
                print_debug(f"OS walk: '{root}', {files}")
                print()

            if len(files) > 0:
                futures: list[concurrent.futures.Future] = []

                for file in files:
                    # map() doesn't cut it, or at least I couldn't get it to
                    # work with functions requiring multiple arguments.
                    future = executor.submit(add_hash_to_file, config, state, Path(root) / file)
                    futures.append(future)

                # Iterate over the future results so exceptions will be thrown
                for future in futures:
                    future.result()

                if config.debug:
                    print()
