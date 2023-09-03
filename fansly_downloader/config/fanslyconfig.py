"""Configuration Class for Shared State"""


import requests

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from .metadatahandling import MetadataHandling
from .modes import DownloadMode


@dataclass
class FanslyConfig(object):
    #region Fields

    #region File-Independent Fields

    # Mandatory property
    # This should be set to __version__ in the main script.
    program_version: str

    # Define base threshold (used for when modules don't provide vars)
    DUPLICATE_THRESHOLD: int = 50

    # Configuration file
    config_path: Path | None = None

    # Misc
    token_from_browser_name: str | None = None
    debug: bool = False
    # If specified on the command-line
    post_id: str | None = None
    # Set on start after self-update
    updated_to: str | None = None

    # Objects
    _parser = ConfigParser(interpolation=None)
    # Define requests session
    http_session = requests.Session()

    #endregion

    #region config.ini Fields

    # TargetedCreator > username
    user_names: set[str] | None = None

    # MyAccount
    token: str | None = None
    user_agent: str | None = None

    # Options
    # "Normal" | "Timeline" | "Messages" | "Single" | "Collection"
    download_mode: DownloadMode = DownloadMode.NORMAL
    download_directory: (None | Path) = None
    download_media_previews: bool = True
    # "Advanced" | "Simple"
    metadata_handling: MetadataHandling = MetadataHandling.ADVANCED
    open_folder_when_finished: bool = True
    separate_messages: bool = True
    separate_previews: bool = False
    separate_timeline: bool = True
    show_downloads: bool = True
    use_duplicate_threshold: bool = False
    use_folder_suffix: bool = True
    # Show input prompts or sleep - for automation/scheduling purposes
    interactive: bool = True
    # Should there be a "Press <ENTER>" prompt at the very end of the program?
    # This helps for semi-automated runs (interactive=False) when coming back
    # to the computer and wanting to see what happened in the console window.
    prompt_on_exit: bool = True

    #endregion

    #endregion

    #region Methods

    def user_names_str(self) -> str | None:
        """Returns a nicely formatted and alphabetically sorted list of
        creator names - for console or config file output.
        
        :return: A single line of all creator names, alphabetically sorted
            and separated by commas eg. "alice, bob, chris, dora".
            Returns None if user_names is None.
        :rtype: str | None
        """
        if self.user_names is None:
            return None

        return ', '.join(sorted(self.user_names))


    def download_mode_str(self) -> str:
        """Gets the string representation of `download_mode`."""
        return str(self.download_mode).capitalize()


    def metadata_handling_str(self) -> str:
        """Gets the string representation of `metadata_handling`."""
        return str(self.metadata_handling).capitalize()

    
    def _sync_settings(self) -> None:
        """Syncs the settings of the config object
        to the config parser/config file.

        This helper is required before saving.
        """
        self._parser.set('TargetedCreator', 'username', self.user_names_str())

        self._parser.set('MyAccount', 'authorization_token', self.token)
        self._parser.set('MyAccount', 'user_agent', self.user_agent)

        if self.download_directory is None:
            self._parser.set('Options', 'download_directory', 'Local_directory')
        else:
            self._parser.set('Options', 'download_directory', str(self.download_directory))

        self._parser.set('Options', 'download_mode', self.download_mode_str())
        self._parser.set('Options', 'metadata_handling', self.metadata_handling_str())
        
        # Booleans
        self._parser.set('Options', 'show_downloads', str(self.show_downloads))
        self._parser.set('Options', 'download_media_previews', str(self.download_media_previews))
        self._parser.set('Options', 'open_folder_when_finished', str(self.open_folder_when_finished))
        self._parser.set('Options', 'separate_messages', str(self.separate_messages))
        self._parser.set('Options', 'separate_previews', str(self.separate_previews))
        self._parser.set('Options', 'separate_timeline', str(self.separate_timeline))
        self._parser.set('Options', 'use_duplicate_threshold', str(self.use_duplicate_threshold))
        self._parser.set('Options', 'use_folder_suffix', str(self.use_folder_suffix))
        self._parser.set('Options', 'interactive', str(self.interactive))
        self._parser.set('Options', 'prompt_on_exit', str(self.prompt_on_exit))


    def _load_raw_config(self) -> list[str]:
        if self.config_path is None:
            return []

        else:
            return self._parser.read(self.config_path)


    def _save_config(self) -> bool:
        if self.config_path is None:
            return False

        else:
            self._sync_settings()

            with self.config_path.open('w', encoding='utf-8') as f:
                self._parser.write(f)
                return True


    def token_is_valid(self) -> bool:
        if self.token is None:
            return False

        return not any(
            [
                len(self.token) < 50,
                'ReplaceMe' in self.token,
            ]
        )

    
    def useragent_is_valid(self) -> bool:
        if self.user_agent is None:
            return False

        return not any(
            [
                len(self.user_agent) < 40,
                'ReplaceMe' in self.user_agent,
            ]
        )
    

    def get_unscrambled_token(self) -> str | None:
        """Gets the unscrambled Fansly authorization token.

        Unscrambles the token if necessary.
                
        :return: The unscrambled Fansly authorization token.
        :rtype: str | None
        """

        if self.token is not None:
            F, c ='fNs', self.token
            
            if c[-3:] == F:
                c = c.rstrip(F)

                A, B, C = [''] * len(c), 7, 0
                
                for D in range(B):
                    for E in range(D, len(A), B) : A[E] = c[C]; C += 1
                
                return ''.join(A)

            else:
                return self.token

        return self.token


    def http_headers(self) -> dict[str, str]:
        token = self.get_unscrambled_token()

        if token is None or self.user_agent is None:
            raise RuntimeError('Internal error generating HTTP headers - token and user agent not set.')

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://fansly.com/',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': token,
            'User-Agent': self.user_agent,
        }

        return headers

    #endregion
