"""Common Utility Functions"""


import os
import platform
import subprocess

from pathlib import Path

from fansly_downloader.config.fanslyconfig import FanslyConfig
from fansly_downloader.errors import ConfigError


def exit(status: int=0) -> None:
    """Exits the program.

    This function overwrites the default exit() function with a
    pyinstaller compatible one.

    :param status: The exit code of the program.
    :type status: int
    """
    os._exit(status)


def save_config_or_raise(config: FanslyConfig) -> bool:
    """Tries to save the configuration to `config.ini` or
    raises a `ConfigError` otherwise.

    :param config: The program configuration.
    :type config: FanslyConfig

    :return: True if configuration was successfully written.
    :rtype: bool

    :raises ConfigError: When the configuration file could not be saved.
        This may be due to invalid path issues or permission/security
        software problems.
    """
    if not config._save_config():
        raise ConfigError(
            f"Internal error: Configuration data could not be saved to '{config.config_path}'. "
            "Invalid path or permission/security software problem."
        )
    else:
        return True


def is_valid_post_id(post_id: str) -> bool:
    """Validates a Fansly post ID.

    Valid post IDs must:
    
    - only contain digits
    - be longer or equal to 10 characters
    - not contain spaces
    
    :param post_id: The post ID string to validate.
    :type post_id: str

    :return: True or False.
    :rtype: bool
    """
    return all(
        [
            post_id.isdigit(),
            len(post_id) >= 10,
            not any(char.isspace() for char in post_id),
        ]
    )


def open_location(filepath: Path, open_folder_when_finished: bool, interactive: bool) -> bool:
    """Opens the download directory in the platform's respective
    file manager application once the download process has finished.

    :param filepath: The base path of all downloads.
    :type filepath: Path
    :param open_folder_when_finished: Open the folder or do nothing.
    :type open_folder_when_finished: bool
    :param interactive: Running interactively or not.
        Folder will not be opened when set to False.
    :type interactive: bool

    :return: True when the folder was opened or False otherwise.
    :rtype: bool
    """
    plat = platform.system()

    if not open_folder_when_finished or not interactive:
        return False
    
    if not os.path.isfile(filepath) and not os.path.isdir(filepath):
        return False
    
    # tested below and they work to open folder locations
    if plat == 'Windows':
        # verified works
        os.startfile(filepath)

    elif plat == 'Linux':
        # verified works
        subprocess.run(['xdg-open', filepath], shell=False)
        
    elif plat == 'Darwin':
        # verified works
        subprocess.run(['open', filepath], shell=False)

    return True
