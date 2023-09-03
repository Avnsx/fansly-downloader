"""Configuration Validation"""


from pathlib import Path
from time import sleep
from requests.exceptions import RequestException

from .config import username_has_valid_chars, username_has_valid_length
from .fanslyconfig import FanslyConfig

from fansly_downloader.errors import ConfigError
from fansly_downloader.pathio.pathio import ask_correct_dir
from fansly_downloader.textio import print_config, print_error, print_info, print_warning
from fansly_downloader.utils.common import save_config_or_raise
from fansly_downloader.utils.web import guess_user_agent, open_get_started_url


def validate_creator_names(config: FanslyConfig) -> bool:
    """Validates the input value for `config_username` in `config.ini`.
    
    :param FanslyConfig config: The configuration object to validate.

    :return: True if all user names passed the test/could be remedied,
        False otherwise.
    :rtype: bool
    """

    if config.user_names is None:
        return False

    # This is not only nice but also since this is a new list object,
    # we won't be iterating over the list (set) being changed.
    names = sorted(config.user_names)
    list_changed = False

    for user in names:
        validated_name = validate_adjust_creator_name(user, config.interactive)

        # Remove invalid names from set
        if validated_name is None:
            print_warning(f"Invalid creator name '{user}' will be removed from processing.")
            config.user_names.remove(user)
            list_changed = True
        
        # Has the user name been adjusted? (Interactive input)
        elif user != validated_name:
            config.user_names.remove(user)
            config.user_names.add(validated_name)
            list_changed = True
    
    print()

    # Save any potential changes
    if list_changed:
        save_config_or_raise(config)

    # No users left after validation -> error
    if len(config.user_names) == 0:
        return False

    else:
        return True


def validate_adjust_creator_name(name: str, interactive: bool=False) -> str | None:
    """Validates the name of a Fansly creator.
    
    :param name: The creator name to validate and potentially correct.
    :type name: str
    :param interactive: Prompts the user for a replacement name if an
        invalid creator name is encountered.
    :type interactive: bool

    :return: The potentially (interactively) adjusted creator name.
    :rtype: str
    """
    # validate input value for config_username in config.ini
    while True:
        usern_base_text = f"Invalid targeted creator name '@{name}':"
        usern_error = False

        replaceme_str = 'ReplaceMe'

        if replaceme_str.lower() in name.lower():
            print_warning(f"Config.ini value '{name}' for TargetedCreator > Username is a placeholder value.")
            usern_error = True

        if not usern_error and ' ' in name:
            print_warning(f'{usern_base_text} name must not contain spaces.')
            usern_error = True

        if not usern_error and not username_has_valid_length(name):
            print_warning(f"{usern_base_text} must be between 4 and 30 characters long!\n")
            usern_error = True

        if not usern_error and not username_has_valid_chars(name):
            print_warning(f"{usern_base_text} should only contain\n{20*' '}alphanumeric characters, hyphens, or underscores!\n")
            usern_error = True

        if not usern_error:
            print_info(f"Name validation for @{name} successful!")
            return name

        if interactive:
            print_config(
                f"Enter the username handle (eg. @MyCreatorsName or MyCreatorsName)"
                f"\n{19*' '}of the Fansly creator you want to download content from."
            )

            name = input(f"\n{19*' '}► Enter a valid username: ")
            name = name.strip().removeprefix('@')
        
        else:
            return None


def validate_adjust_token(config: FanslyConfig) -> None:
    """Validates the Fansly authorization token in the config
    and analyzes installed browsers to automatically find tokens.

    :param FanslyConfig config: The configuration to validate and correct.
    """
    # only if config_token is not set up already; verify if plyvel is installed
    plyvel_installed, browser_name = False, None

    if not config.token_is_valid():
            try:
                import plyvel
                plyvel_installed = True

            except ImportError:
                print_warning(
                    f"Fansly Downloader's automatic configuration for the authorization_token in the config.ini file will be skipped."
                    f"\n{20*' '}Your system is missing required plyvel (python module) builds by Siyao Chen (@liviaerxin)."
                    f"\n{20*' '}Installable with 'pip3 install plyvel-ci' or from github.com/liviaerxin/plyvel/releases/latest"
                )

    # semi-automatically set up value for config_token (authorization_token) based on the users input
    if plyvel_installed and not config.token_is_valid():
        
        # fansly-downloader plyvel dependant package imports
        from fansly_downloader.config.browser import (
            find_leveldb_folders,
            get_auth_token_from_leveldb_folder,
            get_browser_config_paths,
            get_token_from_firefox_profile,
            parse_browser_from_string,
        )

        from fansly_downloader.utils.web import get_fansly_account_for_token

        print_warning(
            f"Authorization token '{config.token}' is unmodified, missing or malformed"
            f"\n{20*' '}in the configuration file."
        )
        print_config(
            f"Trying to automatically configure Fansly authorization token"
            f"\n{19*' '}from any browser storage available on the local system ..."
        )

        browser_paths = get_browser_config_paths()
        fansly_account = None
        
        for browser_path in browser_paths:
            browser_fansly_token = None
        
            # if not firefox, process leveldb folders
            if 'firefox' not in browser_path.lower():
                leveldb_folders = find_leveldb_folders(browser_path)

                for folder in leveldb_folders:
                    browser_fansly_token = get_auth_token_from_leveldb_folder(folder, interactive=config.interactive)

                    if browser_fansly_token:
                        fansly_account = get_fansly_account_for_token(browser_fansly_token)
                        break  # exit the inner loop if a valid processed_token is found
        
            # if firefox, process sqlite db instead
            else:
                browser_fansly_token = get_token_from_firefox_profile(browser_path)

                if browser_fansly_token:
                    fansly_account = get_fansly_account_for_token(browser_fansly_token)
        
            if all([fansly_account, browser_fansly_token]):
                # we might also utilise this for guessing the useragent
                browser_name = parse_browser_from_string(browser_path)

                if config.interactive:
                    # let user pick a account, to connect to fansly downloader
                    print_config(f"Do you want to link the account '{fansly_account}' to Fansly Downloader? (found in: {browser_name})")

                    while True:
                        user_input_acc_verify = input(f"{19*' '}► Type either 'Yes' or 'No': ").strip().lower()

                        if user_input_acc_verify.startswith('y') or user_input_acc_verify.startswith('n'):
                            break # break user input verification

                        else:
                            print_error(f"Please enter either 'Yes' or 'No', to decide if you want to link to '{fansly_account}'.")

                else:
                    # Forcefully link account in interactive mode.
                    print_warning(f"Interactive mode is automtatically linking the account '{fansly_account}' to Fansly Downloader. (found in: {browser_name})")
                    user_input_acc_verify = 'y'

                # based on user input; write account username & auth token to config.ini
                if user_input_acc_verify.startswith('y') and browser_fansly_token is not None:
                    config.token = browser_fansly_token
                    config.token_from_browser_name = browser_name

                    save_config_or_raise(config)

                    print_info(f"Success! Authorization token applied to config.ini file.\n")

                    break # break whole loop

        # if no account auth was found in any of the users browsers
        if fansly_account is None:
            if config.interactive:
                open_get_started_url()

            raise ConfigError(
                f"Your Fansly account was not found in any of your browser's local storage."
                f"\n{18*' '}Did you recently browse Fansly with an authenticated session?"
                f"\n{18*' '}Please read & apply the 'Get-Started' tutorial."
            )
        
    # if users decisions have led to auth token still being invalid
    if not config.token_is_valid():
        if config.interactive:
            open_get_started_url()

        raise ConfigError(
            f"Reached the end and the authorization token in config.ini file is still invalid!"
            f"\n{18*' '}Please read & apply the 'Get-Started' tutorial."
        )


def validate_adjust_user_agent(config: FanslyConfig) -> None:
    # validate input value for "user_agent" in config.ini
    """Validates the input value for `user_agent` in `config.ini`.

    :param FanslyConfig config: The configuration to validate and correct.
    """    

    # if no matches / error just set random UA
    ua_if_failed = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

    based_on_browser = config.token_from_browser_name or 'Chrome'

    if not config.useragent_is_valid():
        print_warning(f"Browser user-agent '{config.user_agent}' in config.ini is most likely incorrect.")

        if config.token_from_browser_name is not None:
            print_config(
                f"Adjusting it with an educated guess based on the combination of your \n"
                f"{19*' '}operating system & specific browser."
            )

        else:
            print_config(
                f"Adjusting it with an educated guess, hardcoded for Chrome browser."
                f"\n{19*' '}If you're not using Chrome you might want to replace it in the config.ini file later on."
                f"\n{19*' '}More information regarding this topic is on the Fansly Downloader Wiki."
            )

        try:
            # thanks Jonathan Robson (@jnrbsn) - for continuously providing these up-to-date user-agents
            user_agent_response = config.http_session.get(
                'https://jnrbsn.github.io/user-agents/user-agents.json',
                headers = {
                    'User-Agent': f"Avnsx/Fansly Downloader {config.program_version}",
                    'accept-language': 'en-US,en;q=0.9'
                }
            )

            if user_agent_response.status_code == 200:
                config_user_agent = guess_user_agent(
                    user_agent_response.json(),
                    based_on_browser,
                    default_ua=ua_if_failed
                )
            else:
                config_user_agent = ua_if_failed

        except RequestException:
            config_user_agent = ua_if_failed

        # save useragent modification to config file
        config.user_agent = config_user_agent

        save_config_or_raise(config)

        print_info(f"Success! Applied a browser user-agent to config.ini file.\n")


def validate_adjust_download_directory(config: FanslyConfig) -> None:
    """Validates the `download_directory` value from `config.ini`
    and corrects it if possible.
    
    :param FanslyConfig config: The configuration to validate and correct.
    """
    # if user didn't specify custom downloads path
    if 'local_dir' in str(config.download_directory).lower():

        config.download_directory = Path.cwd()

        print_info(f"Acknowledging local download directory: '{config.download_directory}'")

    # if user specified a correct custom downloads path
    elif config.download_directory is not None \
        and config.download_directory.is_dir():

        print_info(f"Acknowledging custom basis download directory: '{config.download_directory}'")

    else: # if their set directory, can't be found by the OS
        print_warning(
            f"The custom base download directory file path '{config.download_directory}' seems to be invalid!"
            f"\n{20*' '}Please change it to a correct file path, for example: 'C:\\MyFanslyDownloads'"
            f"\n{20*' '}An Explorer window to help you set the correct path will open soon!"
            f"\n{20*' '}You may right-click inside the Explorer to create a new folder."
            f"\n{20*' '}Select a folder and it will be used as the default download directory."
        )

        sleep(10) # give user time to realise instructions were given

        config.download_directory = ask_correct_dir() # ask user to select correct path using tkinters explorer dialog

        # save the config permanently into config.ini
        save_config_or_raise(config)


def validate_adjust_config(config: FanslyConfig) -> None:
    """Validates all input values from `config.ini`
    and corrects them if possible.
    
    :param FanslyConfig config: The configuration to validate and correct.
    """
    if not validate_creator_names(config):
        raise ConfigError('Configuration error - no valid creator name specified.')

    validate_adjust_token(config)

    validate_adjust_user_agent(config)

    validate_adjust_download_directory(config)
