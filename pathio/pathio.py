"""Work Directory Manipulation"""


import os
import sys
import time

from pathlib import Path
from tkinter import Tk, filedialog

from config import FanslyConfig
from download.downloadstate import DownloadState
from download.types import DownloadType
from textio import print_info, print_warning, print_error


# if the users custom provided filepath is invalid; a tkinter dialog will open during runtime, asking to adjust download path
def ask_correct_dir() -> Path:
    root = Tk()
    root.withdraw()

    while True:
        directory_name = filedialog.askdirectory()

        if Path(directory_name).is_dir():
            print_info(f"Folder path chosen: {directory_name}")
            return Path(directory_name)

        print_error(f"You did not choose a valid folder. Please try again!", 5)


def set_create_directory_for_download(config: FanslyConfig, state: DownloadState) -> Path:
    """Sets and creates the appropriate download directory according to
    download type for storing media from a distinct creator.

    :param FanslyConfig config: The current download session's
        configuration object. download_directory will be taken as base path.

    :param DownloadState state: The current download session's state.
        This function will modify base_path (based on creator) and
        save_path (full path based on download type) accordingly.

    :return Path: The (created) path current media downloads.
    """
    if config.download_directory is None:
        message = 'Internal error during directory creation - download directory not set.'
        raise RuntimeError(message)

    else:

        suffix = ''

        if config.use_folder_suffix:
            suffix = '_fansly'

        user_base_path = config.download_directory / f'{state.creator_name}{suffix}'
        
        user_base_path.mkdir(exist_ok=True)

        # Default directory if download types don't match in check below
        download_directory = user_base_path

        if state.download_type == DownloadType.COLLECTIONS:
            download_directory = config.download_directory / 'Collections'

        elif state.download_type == DownloadType.MESSAGES and config.separate_messages:
            download_directory = user_base_path / 'Messages'

        elif state.download_type == DownloadType.TIMELINE and config.separate_timeline:
            download_directory = user_base_path / 'Timeline'

        elif state.download_type == DownloadType.SINGLE:
            # TODO: Maybe for "Single" we should use the post_id as subdirectory?
            pass

        # If current download folder wasn't created with content separation, disable it for this download session too
        is_file_hierarchy_correct = True

        if user_base_path.is_dir():

            for directory in user_base_path.iterdir():

                if (user_base_path / directory).is_dir():

                    if 'Pictures' in str(directory) and any([config.separate_messages, config.separate_timeline]):
                        is_file_hierarchy_correct = False

                    if 'Videos' in str(directory) and any([config.separate_messages, config.separate_timeline]):
                        is_file_hierarchy_correct = False

            if not is_file_hierarchy_correct:
                print_warning(
                    f"Due to the presence of 'Pictures' and 'Videos' sub-directories in the current download folder"
                    f"\n{20*' '}content separation will remain disabled throughout this download session."
                )

                config.separate_messages, config.separate_timeline = False, False
            
                # utilize recursion to fix BASE_DIR_NAME generation
                return set_create_directory_for_download(config, state)

        # Save state
        state.base_path = user_base_path
        state.download_path = download_directory

        # Create the directory
        download_directory.mkdir(exist_ok=True)

        return download_directory


def delete_temporary_pyinstaller_files():
    """Delete old files from the PyInstaller temporary folder.
    
    Files older than an hour will be deleted.
    """
    try:
        base_path = sys._MEIPASS

    except Exception:
        return

    temp_dir = os.path.abspath(os.path.join(base_path, '..'))
    current_time = time.time()

    for folder in os.listdir(temp_dir):
        try:
            item = os.path.join(temp_dir, folder)

            if folder.startswith('_MEI') \
                and os.path.isdir(item) \
                    and (current_time - os.path.getctime(item)) > 3600:

                for root, dirs, files in os.walk(item, topdown=False):

                    for file in files:
                        os.remove(os.path.join(root, file))

                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))

                os.rmdir(item)

        except Exception:
            pass
