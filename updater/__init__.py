"""Self-Updating Functionality"""


import sys

from utils.web import get_release_info_from_github

from .utils import check_for_update, delete_deprecated_files, post_update_steps

from config import FanslyConfig, copy_old_config_values
from textio import print_warning
from utils.common import save_config_or_raise


def self_update(config: FanslyConfig):
    """Performs self-updating if necessary."""

    release_info = get_release_info_from_github(config.program_version)

    # Regular start, not after update
    if config.updated_to is None:
        # check if a new version is available
        check_for_update(config)

    # if started with --updated-to start argument
    else:

        # config.ini backwards compatibility fix (≤ v0.4) -> fix spelling mistake "seperate" to "separate"
        if 'seperate_messages' in config._parser['Options']:
            config.separate_messages = \
                config._parser.getboolean('Options', 'seperate_messages')
            config._parser.remove_option('Options', 'seperate_messages')

        if 'seperate_previews' in config._parser['Options']:
            config.separate_previews = \
                config._parser.getboolean('Options', 'seperate_previews')
            config._parser.remove_option('Options', 'seperate_previews')

        # config.ini backwards compatibility fix (≤ v0.4) -> config option "naming_convention" & "update_recent_download" removed entirely
        options_to_remove = ['naming_convention', 'update_recent_download']

        for option in options_to_remove:
            
            if option in config._parser['Options']:
                config._parser.remove_option('Options', option)

                print_warning(
                    f"Just removed '{option}' from the config.ini file as the whole option"
                    f"\n{20*' '}is no longer supported after version 0.3.5."
                )
        
        # Just re-save the config anyway, regardless of changes
        save_config_or_raise(config)

        # check if old config.ini exists, compare each pre-existing value of it and apply it to new config.ini
        copy_old_config_values()
        
        # temporary: delete deprecated files
        delete_deprecated_files()

        # get release notes and if existent display it in terminal
        post_update_steps(config.program_version, release_info)

        # read the config.ini file for a last time
        config._load_raw_config()
