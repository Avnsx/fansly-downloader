"""Configuration File Manipulation"""


import configparser
import os

from configparser import ConfigParser
from os import getcwd
from os.path import join
from pathlib import Path

from .fanslyconfig import FanslyConfig
from .metadatahandling import MetadataHandling
from .modes import DownloadMode

from fansly_downloader.errors import ConfigError
from fansly_downloader.textio import print_info, print_config, print_warning
from fansly_downloader.utils.common import save_config_or_raise
from fansly_downloader.utils.web import open_url


def parse_items_from_line(line: str) -> list[str]:
    """Parses a list of items (eg. creator names) from a single line
    as eg. read from a configuration file.

    :param str line: A single line containing eg. user names
        separated by either spaces or commas (,).

    :return: A list of items (eg. names) parsed from the line.
    :rtype: list[str]
    """
    names: list[str] = []

    if ',' in line:
        names = line.split(',')

    else:
        names = line.split()

    return names


def sanitize_creator_names(names: list[str]) -> set[str]:
    """Sanitizes a list of creator names after they have been
    parsed from a configuration file.

    This will:

    * remove empty names
    * remove leading/trailing whitespace from a name
    * remove a leading @ from a name
    * remove duplicates
    * lower-case each name (for de-duplication to work)
    
    :param list[str] names: A list of names to process.

    :return: A set of unique, sanitized creator names.
    :rtype: set[str]
    """
    return set(
        name.strip().removeprefix('@').lower()
        for name in names
        if name.strip()
    )


def username_has_valid_length(name: str) -> bool:
    if name is None:
        return False

    return len(name) >= 4 and len(name) <= 30


def username_has_valid_chars(name: str) -> bool:
    if name is None:
        return False

    invalid_chars = set(name) \
        - set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    
    return not invalid_chars


def copy_old_config_values():
    """Copies configuration values from an old configuration file to
    a new one.

    Only sections/values existing in the new configuration will be adjusted.

    The hardcoded file names are from `old_config.ini` to `config.ini`.
    """
    current_directory = getcwd()
    old_config_path = join(current_directory, 'old_config.ini')
    new_config_path = join(current_directory, 'config.ini')

    if os.path.isfile(old_config_path) and os.path.isfile(new_config_path):
        old_config = ConfigParser(interpolation=None)
        old_config.read(old_config_path)

        new_config = ConfigParser(interpolation=None)
        new_config.read(new_config_path)

        # iterate over each section in the old config
        for section in old_config.sections():
            # check if the section exists in the new config
            if new_config.has_section(section):
                # iterate over each option in the section
                for option in old_config.options(section):
                    # check if the option exists in the new config
                    if new_config.has_option(section, option):
                        # get the value from the old config and set it in the new config
                        value = old_config.get(section, option)

                        # skip overwriting the version value
                        if section == 'Other' and option == 'version':
                            continue

                        new_config.set(section, option, value)

        # save the updated new config
        with open(new_config_path, 'w') as config_file:
            new_config.write(config_file)


def load_config(config: FanslyConfig) -> None:
    """Loads the program configuration from file.
    
    :param FanslyConfig config: The configuration object to fill.
    """

    print_info('Reading config.ini file ...')
    print()
    
    config.config_path = Path.cwd() / 'config.ini'

    if not config.config_path.exists():
        print_warning("Configuration file config.ini not found.")
        print_config("A default configuration file will be generated for you ...")

        with open(config.config_path, mode='w', encoding='utf-8'):
            pass

    config._load_raw_config()

    try:
        # WARNING: Do not use the save config helper until the very end!
        # Since the settings from the config object are synced to the parser
        # on save, all still uninitialized values from the partially loaded
        # config would overwrite the existing configuration!
        replace_me_str = 'ReplaceMe'

        #region TargetedCreator

        creator_section = 'TargetedCreator'

        if not config._parser.has_section(creator_section):
            config._parser.add_section(creator_section)

        # Check for command-line override - already set?
        if config.user_names is None:
            user_names = config._parser.get(creator_section, 'Username', fallback=replace_me_str) # string

            config.user_names = \
                sanitize_creator_names(parse_items_from_line(user_names))

        #endregion

        #region MyAccount

        account_section = 'MyAccount'

        if not config._parser.has_section(account_section):
            config._parser.add_section(account_section)

        config.token = config._parser.get(account_section, 'Authorization_Token', fallback=replace_me_str) # string
        config.user_agent = config._parser.get(account_section, 'User_Agent', fallback=replace_me_str) # string

        #endregion

        #region Other

        other_section = 'Other'

        # I obsoleted this ...
        #config.current_version = config.parser.get('Other', 'version') # str
        if config._parser.has_option(other_section, 'version'):
            config._parser.remove_option(other_section, 'version')

        # Remove empty section
        if config._parser.has_section(other_section) \
                and len(config._parser[other_section]) == 0:
            config._parser.remove_section(other_section)

        #endregion

        #region Options

        options_section = 'Options'

        if not config._parser.has_section(options_section):
            config._parser.add_section(options_section)

        # Local_directory, C:\MyCustomFolderFilePath -> str
        config.download_directory = Path(
            config._parser.get(options_section, 'download_directory', fallback='Local_directory')
        )
        
        # Normal (Timeline & Messages), Timeline, Messages, Single (Single by post id) or Collections -> str
        download_mode = config._parser.get(options_section, 'download_mode', fallback='Normal')
        config.download_mode = DownloadMode(download_mode.lower())

        # Advanced, Simple -> str
        metadata_handling = config._parser.get(options_section, 'metadata_handling', fallback='Advanced')
        config.metadata_handling = MetadataHandling(metadata_handling.lower())

        config.download_media_previews = config._parser.getboolean(options_section, 'download_media_previews', fallback=True)
        config.open_folder_when_finished = config._parser.getboolean(options_section, 'open_folder_when_finished', fallback=True)
        config.separate_messages = config._parser.getboolean(options_section, 'separate_messages', fallback=True)
        config.separate_previews = config._parser.getboolean(options_section, 'separate_previews', fallback=False)
        config.separate_timeline = config._parser.getboolean(options_section, 'separate_timeline', fallback=True)
        config.show_downloads = config._parser.getboolean(options_section, 'show_downloads', fallback=True)
        config.interactive = config._parser.getboolean(options_section, 'interactive', fallback=True)
        config.prompt_on_exit = config._parser.getboolean(options_section, 'prompt_on_exit', fallback=True)

        # I renamed this to "use_duplicate_threshold" but retain older config.ini compatibility
        # True, False -> boolean
        if config._parser.has_option(options_section, 'utilise_duplicate_threshold'):
            config.use_duplicate_threshold = config._parser.getboolean(options_section, 'utilise_duplicate_threshold', fallback=False)
            config._parser.remove_option(options_section, 'utilise_duplicate_threshold')

        else:
            config.use_duplicate_threshold = config._parser.getboolean(options_section, 'use_duplicate_threshold', fallback=False)

        # True, False -> boolean
        if config._parser.has_option(options_section, 'use_suffix'):
            config.use_folder_suffix = config._parser.getboolean(options_section, 'use_suffix', fallback=True)
            config._parser.remove_option(options_section, 'use_suffix')

        else:
            config.use_folder_suffix = config._parser.getboolean(options_section, 'use_folder_suffix', fallback=True)

        #endregion

        # Safe to save! :-)
        save_config_or_raise(config)

    except configparser.NoOptionError as e:
        error_string = str(e)
        raise ConfigError(f"Your config.ini file is invalid, please download a fresh version of it from GitHub.\n{error_string}")

    except ValueError as e:
        error_string = str(e)

        if 'a boolean' in error_string:
            if config.interactive:
                open_url('https://github.com/Avnsx/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#4-configini')

            raise ConfigError(
                f"'{error_string.rsplit('boolean: ')[1]}' is malformed in the configuration file! This value can only be True or False"
                f"\n{17*' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini [1]"
            )

        else:
            if config.interactive:
                open_url('https://github.com/Avnsx/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#4-configini')

            raise ConfigError(
                f"You have entered a wrong value in the config.ini file -> '{error_string}'"
                f"\n{17*' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini [2]"
            )

    except (KeyError, NameError) as key:
        if config.interactive:
            open_url('https://github.com/Avnsx/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#4-configini')

        raise ConfigError(
            f"'{key}' is missing or malformed in the configuration file!"
            f"\n{17*' '}Read the Wiki > Explanation of provided programs & their functionality > config.ini [3]"
        )
