#!/usr/bin/env python3

"""Fansly Downloader"""

__version__ = '0.5.2'
__date__ = '2023-09-03T14:40:00+02'
__maintainer__ = 'Avnsx (Mika C.)'
__copyright__ = f'Copyright (C) 2021-2023 by {__maintainer__}'
__authors__: list[str] = []
__credits__: list[str] = []

# TODO: Fix in future: audio needs to be properly transcoded from mp4 to mp3, instead of just saved as


import base64
import traceback

from random import randint
from time import sleep

from fansly_downloader.config import FanslyConfig, load_config, validate_adjust_config
from fansly_downloader.config.args import parse_args, map_args_to_config
from fansly_downloader.config.modes import DownloadMode
from fansly_downloader.download.core import *
from fansly_downloader.errors import *
from fansly_downloader.fileio.dedupe import dedupe_init
from fansly_downloader.pathio import delete_temporary_pyinstaller_files
from fansly_downloader.textio import (
    input_enter_close,
    input_enter_continue,
    print_error,
    print_info,
    print_warning,
    set_window_title,
)
from fansly_downloader.updater import self_update
from fansly_downloader.utils.common import exit, open_location
from fansly_downloader.utils.web import remind_stargazing


# tell PIL to be tolerant of files that are truncated
#ImageFile.LOAD_TRUNCATED_IMAGES = True

# turn off for our purpose unnecessary PIL safety features
#Image.MAX_IMAGE_PIXELS = None


def print_statistics(config: FanslyConfig, state: DownloadState) -> None:

    print(
        f"\n╔═\n  Finished {config.download_mode_str()} type download of {state.pic_count} pictures & {state.vid_count} videos " \
        f"from @{state.creator_name}!\n  Declined duplicates: {state.duplicate_count}" \
        f"\n  Saved content in directory: '{state.base_path}'"\
        f"\n\n  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶\n{74*' '}═╝")

    sleep(10)


def main(config: FanslyConfig) -> int:
    """The main logic of the downloader program.
    
    :param config: The program configuration.
    :type config: FanslyConfig

    :return: The exit code of the program.
    :rtype: int
    """
    exit_code = EXIT_SUCCESS

    # Update window title with specific downloader version
    set_window_title(f"Fansly Downloader v{config.program_version}")

    # base64 code to display logo in console
    print(base64.b64decode('CiAg4paI4paI4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKWiOKWiOKWiOKVlyDilojilojilojilZcgICDilojilojilZfilojilojilojilojilojilojilojilZfilojilojilZcgIOKWiOKWiOKVlyAgIOKWiOKWiOKVlyAgICDilojilojilojilojilojilojilZcg4paI4paI4pWXICAgICAgICAgIOKWiOKWiOKWiOKWiOKWiOKVlyDilojilojilojilojilojilojilZcg4paI4paI4paI4paI4paI4paI4pWXIAogIOKWiOKWiOKVlOKVkOKVkOKVkOKVkOKVneKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKWiOKWiOKVlyAg4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4pWQ4pWQ4pWd4paI4paI4pWRICDilZrilojilojilZcg4paI4paI4pWU4pWdICAgIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVkSAgICAgICAgIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVlOKVkOKVkOKWiOKWiOKVlwogIOKWiOKWiOKWiOKWiOKWiOKVlyAg4paI4paI4paI4paI4paI4paI4paI4pWR4paI4paI4pWU4paI4paI4pWXIOKWiOKWiOKVkeKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVl+KWiOKWiOKVkSAgIOKVmuKWiOKWiOKWiOKWiOKVlOKVnSAgICAg4paI4paI4pWRICDilojilojilZHilojilojilZEgICAgICAgICDilojilojilojilojilojilojilojilZHilojilojilojilojilojilojilZTilZ3ilojilojilojilojilojilojilZTilZ0KICDilojilojilZTilZDilZDilZ0gIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVkeKWiOKWiOKVkeKVmuKWiOKWiOKVl+KWiOKWiOKVkeKVmuKVkOKVkOKVkOKVkOKWiOKWiOKVkeKWiOKWiOKVkSAgICDilZrilojilojilZTilZ0gICAgICDilojilojilZEgIOKWiOKWiOKVkeKWiOKWiOKVkSAgICAgICAgIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVkeKWiOKWiOKVlOKVkOKVkOKVkOKVnSDilojilojilZTilZDilZDilZDilZ0gCiAg4paI4paI4pWRICAgICDilojilojilZEgIOKWiOKWiOKVkeKWiOKWiOKVkSDilZrilojilojilojilojilZHilojilojilojilojilojilojilojilZHilojilojilojilojilojilojilojilZfilojilojilZEgICAgICAg4paI4paI4paI4paI4paI4paI4pWU4pWd4paI4paI4paI4paI4paI4paI4paI4pWXICAgIOKWiOKWiOKVkSAg4paI4paI4pWR4paI4paI4pWRICAgICDilojilojilZEgICAgIAogIOKVmuKVkOKVnSAgICAg4pWa4pWQ4pWdICDilZrilZDilZ3ilZrilZDilZ0gIOKVmuKVkOKVkOKVkOKVneKVmuKVkOKVkOKVkOKVkOKVkOKVkOKVneKVmuKVkOKVkOKVkOKVkOKVkOKVkOKVneKVmuKVkOKVnSAgICAgICDilZrilZDilZDilZDilZDilZDilZ0g4pWa4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWdICAgIOKVmuKVkOKVnSAg4pWa4pWQ4pWd4pWa4pWQ4pWdICAgICDilZrilZDilZ0gICAgIAogICAgICAgICAgICAgICAgICAgICAgICBkZXZlbG9wZWQgb24gZ2l0aHViLmNvbS9Bdm5zeC9mYW5zbHktZG93bmxvYWRlcgo=').decode('utf-8'))

    delete_temporary_pyinstaller_files()
    load_config(config)

    args = parse_args()
    # Note that due to config._sync_settings(), command-line arguments
    # may overwrite config.ini settings later on during validation
    # when the config may be saved again.
    # Thus a separate config_args.ini will be used for the session.
    map_args_to_config(args, config)

    self_update(config)

    # occasionally notfiy user to star repository
    if randint(1,100) <= 19:
        try:
            remind_stargazing(config)
        except Exception: # irrelevant enough, to pass regardless what errors may happen
            pass

    validate_adjust_config(config)

    if config.user_names is None \
            or config.download_mode == DownloadMode.NOTSET:
        raise RuntimeError('Internal error - user name and download mode should not be empty after validation.')

    for creator_name in sorted(config.user_names):
        try:
            state = DownloadState(creator_name)

            # Special treatment for deviating folder names later
            if not config.download_mode == DownloadMode.SINGLE:
                dedupe_init(config, state)

            print_download_info(config)

            get_creator_account_info(config, state)

            # Download mode:
            # Normal: Downloads Timeline + Messages one after another.
            # Timeline: Scrapes only the creator's timeline content.
            # Messages: Scrapes only the creator's messages content.
            # Single: Fetch a single post by the post's ID. Click on a post to see its ID in the url bar e.g. ../post/1283493240234
            # Collection: Download all content listed within the "Purchased Media Collection"

            print_info(f'Download mode is: {config.download_mode_str()}')
            print()

            if config.download_mode == DownloadMode.SINGLE:
                download_single_post(config, state)

            elif config.download_mode == DownloadMode.COLLECTION:
                download_collections(config, state)

            else:
                if any([config.download_mode == DownloadMode.MESSAGES, config.download_mode == DownloadMode.NORMAL]):
                    download_messages(config, state)

                if any([config.download_mode == DownloadMode.TIMELINE, config.download_mode == DownloadMode.NORMAL]):
                    download_timeline(config, state)

            print_statistics(config, state)

            # open download folder
            if state.base_path is not None:
                open_location(state.base_path, config.open_folder_when_finished, config.interactive)

        # Still continue if one creator failed
        except ApiAccountInfoError as e:
            print_error(str(e))
            input_enter_continue(config.interactive)
            exit_code = SOME_USERS_FAILED

    return exit_code


if __name__ == '__main__':
    config = FanslyConfig(program_version=__version__)
    exit_code = EXIT_SUCCESS

    try:
        exit_code = main(config)

    except KeyboardInterrupt:
        # TODO: Should there be any clean-up or in-program handling during Ctrl+C?
        print()
        print_warning('Program aborted.')
        exit_code = EXIT_ABORT

    except ApiError as e:
        print()
        print_error(str(e))
        exit_code = API_ERROR

    except ConfigError as e:
        print()
        print_error(str(e))
        exit_code = CONFIG_ERROR

    except DownloadError as e:
        print()
        print_error(str(e))
        exit_code = DOWNLOAD_ERROR

    except Exception as e:
        print()
        print_error(f'An unexpected error occurred: {e}\n{traceback.format_exc()}')
        exit_code = UNEXPECTED_ERROR

    input_enter_close(config.prompt_on_exit)
    exit(exit_code)
