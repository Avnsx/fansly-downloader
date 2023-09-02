"""Argument Parsing and Configuration Mapping"""


import argparse

from functools import partial
from pathlib import Path

from .config import parse_items_from_line, sanitize_creator_names
from .fanslyconfig import FanslyConfig
from .metadatahandling import MetadataHandling
from .modes import DownloadMode

from errors import ConfigError
from textio import print_debug, print_warning
from utils.common import is_valid_post_id, save_config_or_raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fansly Downloader scrapes media content from one or more Fansly creators. "
            "Settings will be taken from config.ini or internal defaults and "
            "can be overriden with the following parameters.\n"
            "Using the command-line will not overwrite config.ini.",
    )

    #region Essential Options

    parser.add_argument(
        '-u', '--user',
        required=False,
        default=None,
        metavar='USER',
        dest='users',
        help="A list of one or more Fansly creators you want to download "
            "content from.\n"
            "This overrides TargetedCreator > username in config.ini.",
        nargs='+',
    )
    parser.add_argument(
        '-dir', '--directory',
        required=False,
        default=None,
        dest='download_directory',
        help="The base directory to store all creators' content in. "
            "A subdirectory for each creator will be created automatically. "
            "If you do not specify --no-folder-suffix, "
            "each creator's folder will be suffixed with ""_fansly"". "
            "Please remember to quote paths including spaces.",
    )
    parser.add_argument(
        '-t', '--token',
        required=False,
        default=None,
        metavar='AUTHORIZATION_TOKEN',
        dest='token',
        help="The Fansly authorization token obtained from a browser session.",
    )
    parser.add_argument(
        '-ua', '--user-agent',
        required=False,
        default=None,
        dest='user_agent',
        help="The browser user agent string to use when communicating with "
            "Fansly servers. This should ideally be set to the user agent "
            "of the browser you use to view Fansly pages and where the "
            "authorization token was obtained from.",
    )

    #endregion

    #region Download modes

    download_modes = parser.add_mutually_exclusive_group(required=False)

    download_modes.add_argument(
        '--normal',
        required=False,
        default=False,
        action='store_true',
        dest='download_mode_normal',
        help='Use "Normal" download mode. This will download messages and timeline media.',
    )
    download_modes.add_argument(
        '--messages',
        required=False,
        default=False,
        action='store_true',
        dest='download_mode_messages',
        help='Use "Messages" download mode. This will download messages only.',
    )
    download_modes.add_argument(
        '--timeline',
        required=False,
        default=False,
        action='store_true',
        dest='download_mode_timeline',
        help='Use "Timeline" download mode. This will download timeline content only.',
    )
    download_modes.add_argument(
        '--collection',
        required=False,
        default=False,
        action='store_true',
        dest='download_mode_collection',
        help='Use "Collection" download mode. This will ony download a collection.',
    )
    download_modes.add_argument(
        '--single',
        required=False,
        default=None,
        metavar='POST_ID',
        dest='download_mode_single',
        help='Use "Single" download mode. This will download a single post '
            "by ID from an arbitrary creator. "
            "A post ID must be at least 10 characters and consist of digits only."
            "Example - https://fansly.com/post/1283998432982 -> ID is: 1283998432982",
    )

    #endregion

    #region Other Options

    parser.add_argument(
        '-ni', '--non-interactive',
        required=False,
        default=False,
        action='store_true',
        dest='non_interactive',
        help="Do not ask for input during warnings and errors that need "
            "your attention but can be automatically continued. "
            "Setting this will download all media of all users without any "
            "intervention.",
    )
    parser.add_argument(
        '-npox', '--no-prompt-on-exit',
        required=False,
        default=False,
        action='store_true',
        dest='no_prompt_on_exit',
        help="Do not ask to press <ENTER> at the very end of the program. "
            "Set this for a fully automated/headless experience.",
    )
    parser.add_argument(
        '-nfs', '--no-folder-suffix',
        required=False,
        default=False,
        action='store_true',
        dest='no_folder_suffix',
        help='Do not add "_fansly" to the download folder of a creator.',
    )
    parser.add_argument(
        '-np', '--no-previews',
        required=False,
        default=False,
        action='store_true',
        dest='no_media_previews',
        help="Do not download media previews (which may contain spam).",
    )
    parser.add_argument(
        '-hd', '--hide-downloads',
        required=False,
        default=False,
        action='store_true',
        dest='hide_downloads',
        help="Do not show download information.",
    )
    parser.add_argument(
        '-nof', '--no-open-folder',
        required=False,
        default=False,
        action='store_true',
        dest='no_open_folder',
        help="Do not open the download folder on creator completion.",
    )
    parser.add_argument(
        '-nsm', '--no-separate-messages',
        required=False,
        default=False,
        action='store_true',
        dest='no_separate_messages',
        help="Do not separate messages into their own folder.",
    )
    parser.add_argument(
        '-nst', '--no-separate-timeline',
        required=False,
        default=False,
        action='store_true',
        dest='no_separate_timeline',
        help="Do not separate timeline content into it's own folder.",
    )
    parser.add_argument(
        '-sp', '--separate-previews',
        required=False,
        default=False,
        action='store_true',
        dest='separate_previews',
        help="Separate preview media (which may contain spam) into their own folder.",
    )
    parser.add_argument(
        '-udt', '--use-duplicate-threshold',
        required=False,
        default=False,
        action='store_true',
        dest='use_duplicate_threshold',
        help="Use an internal de-deduplication threshold to not download "
            "already downloaded media again.",
    )
    parser.add_argument(
        '-mh', '--metadata-handling',
        required=False,
        default=None,
        type=str,
        dest='metadata_handling',
        help="How to handle media EXIF metadata. "
            "Supported strategies: Advanced (Default), Simple",
    )

    #endregion

    #region Developer/troubleshooting arguments

    parser.add_argument(
        '--debug',
        required=False,
        default=False,
        action='store_true',
        help="Print debugging output. Only for developers or troubleshooting.",
    )
    parser.add_argument(
        '--updated-to',
        required=False,
        default=None,
        help="This is for internal use of the self-updating functionality only.",
    )

    #endregion

    return parser.parse_args()


def check_attributes(
            args: argparse.Namespace,
            config: FanslyConfig,
            arg_attribute: str,
            config_attribute: str
        ) -> None:
    """A helper method to validate the presence of attributes (properties)
    in `argparse.Namespace` and `FanslyConfig` objects for mapping
    arguments. This is to locate code changes and typos.

    :param args: The arguments parsed.
    :type args: argparse.Namespace
    :param config: The Fansly Downloader configuration.
    :type config: FanslyConfig
    :param arg_attribute: The argument destination variable name.
    :type arg_attribute: str
    :param config_attribute: The configuration attribute/property name.
    :type config_attribute: str

    :raise RuntimeError: Raised when an attribute does not exist.

    """
    if hasattr(args, arg_attribute) and hasattr(config, config_attribute):
        return
    
    raise RuntimeError(
        'Internal argument configuration error - please contact the developer.'
        f'(args.{arg_attribute} == {hasattr(args, arg_attribute)}, '
        f'config.{config_attribute} == {hasattr(config, config_attribute)})'
    )


def map_args_to_config(args: argparse.Namespace, config: FanslyConfig) -> None:
    """Maps command-line arguments to the configuration object of
    the current session.
    
    :param argparse.Namespace args: The command-line arguments
        retrieved via argparse.
    :param FanslyConfig config: The program configuration to map the
        arguments to.
    """
    if config.config_path is None:
        raise RuntimeError('Internal error mapping arguments - configuration path not set. Load the config first.')

    config_overridden = False
    
    config.debug = args.debug
    
    if config.debug:
        print_debug(f'Args: {args}')
        print()

    if args.users is not None:
        # If someone "abused" argparse like this:
        #   -u creater1, creator7 , lovedcreator
        # ... then it's best to re-construct a line and fully parse.
        users_line = ' '.join(args.users)
        config.user_names = \
            sanitize_creator_names(parse_items_from_line(users_line))
        config_overridden = True

    if config.debug:
        print_debug(f'Value of `args.users` is: {args.users}')
        print_debug(f'`args.users` is None == {args.users is None}')
        print_debug(f'`config.username` is: {config.user_names}')
        print()

    if args.download_mode_normal:
        config.download_mode = DownloadMode.NORMAL
        config_overridden = True

    if args.download_mode_messages:
        config.download_mode = DownloadMode.MESSAGES
        config_overridden = True

    if args.download_mode_timeline:
        config.download_mode = DownloadMode.TIMELINE
        config_overridden = True

    if args.download_mode_collection:
        config.download_mode = DownloadMode.COLLECTION
        config_overridden = True

    if args.download_mode_single is not None:
        post_id = args.download_mode_single
        config.download_mode = DownloadMode.SINGLE
        
        if not is_valid_post_id(post_id):
            raise ConfigError(
                f"Argument error - '{post_id}' is not a valid post ID. "
                "At least 10 characters/only digits required."
            )

        config.post_id = post_id
        config_overridden = True

    if args.metadata_handling is not None:
        handling = args.metadata_handling.strip().lower()

        try:
            config.metadata_handling = MetadataHandling(handling)
            config_overridden = True
        
        except ValueError:
               raise ConfigError(
                f"Argument error - '{handling}' is not a valid metadata handling strategy."
            )         

    # The code following avoids code duplication of checking an
    # argument and setting the override flag for each argument.
    # On the other hand, this certainly not refactoring/renaming friendly.
    # But arguments following similar patterns can be changed or
    # added more easily.

    # Simplify since args and config arguments will always be the same
    check_attr = partial(check_attributes, args, config)

    # Not-None-settings to map
    not_none_settings = [
        'download_directory',
        'token',
        'user_agent',
        'updated_to',
    ]

    # Sets config when arguments are not None
    for attr_name in not_none_settings:
        check_attr(attr_name, attr_name)
        arg_attribute = getattr(args, attr_name)

        if arg_attribute is not None:

            if attr_name == 'download_directory':
                setattr(config, attr_name, Path(arg_attribute))

            else:
                setattr(config, attr_name, arg_attribute)

            config_overridden = True

    # Do-settings to map to config
    positive_bools = [
        'separate_previews',
        'use_duplicate_threshold',
    ]

    # Sets config to arguments when arguments are True
    for attr_name in positive_bools:
        check_attr(attr_name, attr_name)
        arg_attribute = getattr(args, attr_name)

        if arg_attribute == True:
            setattr(config, attr_name, arg_attribute)
            config_overridden = True

    # Do-not-settings to map to config
    negative_bool_map = [
        ('non_interactive', 'interactive'),
        ('no_prompt_on_exit', 'prompt_on_exit'),
        ('no_folder_suffix', 'use_folder_suffix'),
        ('no_media_previews', 'download_media_previews'),
        ('hide_downloads', 'show_downloads'),
        ('no_open_folder', 'open_folder_when_finished'),
        ('no_separate_messages', 'separate_messages'),
        ('no_separate_timeline', 'separate_timeline'),
        ('no_separate_messages', 'separate_messages'),
    ]

    # Set config to the inverse (negation) of arguments that are True
    for attributes in negative_bool_map:
        arg_name = attributes[0]
        config_name = attributes[1]
        check_attr(arg_name, config_name)

        arg_attribute = getattr(args, arg_name)

        if arg_attribute == True:
            setattr(config, config_name, not arg_attribute)

    if config_overridden:
        print_warning(
            "You have specified some command-line arguments that override config.ini settings.\n"
            f"{20*' '}A separate, temporary config file will be generated for this session\n"
            f"{20*' '}to prevent accidental changes to your original configuration.\n"
        )
        config.config_path = config.config_path.parent / 'config_args.ini'
        save_config_or_raise(config)
