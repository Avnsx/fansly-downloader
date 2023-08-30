"""Configuration Utilities"""


import json
import os
import os.path
import platform
import plyvel
import psutil
import sqlite3
import traceback

from time import sleep

from textio import print_config


# Function to recursively search for "storage" folders and process SQLite files
def get_token_from_firefox_profile(directory: str) -> str | None:
    """Gets a Fansly authorization token from a Firefox
    configuration directory.
    
    :param str directory: The user's Firefox profile directory to analyze.

    :return: A Fansly authorization token if one could be found or None.
    :rtype: str | None
    """
    for root, _, files in os.walk(directory):
        # Search the profile's "storage" folder
        # TODO: It would probably be better to limit the search to the "default" subdirectory of "storage"
        if "storage" in root:
            for file in files:
                if file.endswith(".sqlite"):
                    sqlite_file = os.path.join(root, file)
                    session_active_session = get_token_from_firefox_db(sqlite_file)
                    if session_active_session is not None:
                        return session_active_session

    # No match was found
    return None


def get_token_from_firefox_db(sqlite_file_name: str, interactive: bool=True) -> str | None:
    """Fetches the Fansly token from the Firefox SQLite configuration
    database.

    :param str sqlite_file_name: The full path to the Firefox configuration
        database.
    
    :return: The Fansly token if found or None otherwise.
    :rtype: str | None
    """
    session_active_session = None

    try:
        with sqlite3.connect(sqlite_file_name) as conn:
            cursor = conn.cursor()

            # Get all table names in the SQLite database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()

                # Read key-value pairs
                for row in rows:
                    if row[0] == 'session_active_session':
                        session_active_session = json.loads(row[5].decode('utf-8'))['token']
                        break

        return session_active_session
    
    except sqlite3.OperationalError as e:
        # Got
        # "sqlite3.OperationalError: Could not decode to UTF-8 column 'value' with text"
        # all over the place.
        # I guess this is from other databases with different encodings,
        # maybe UTF-16. So just ignore.
        pass

    except sqlite3.Error as e:
        sqlite_error = str(e)

        if 'locked' in sqlite_error and 'irefox' in sqlite_file_name:

            if not interactive:
                # Do not forcefully close user's browser in non-interactive/scheduled mode.
                return None

            print_config(
                f"Firefox browser is open but needs to be closed for automatic configurator"
                f"\n{19*' '}to search your fansly account in the browsers storage."
                f"\n{19*' '}Please save any important work within the browser & close the browser yourself"
                f"\n{19*' '}or it will be closed automatically after continuing."
            )

            input(f"\n{19*' '}► Press <ENTER> to continue! ")

            close_browser_by_name('firefox')

            return get_token_from_firefox_db(sqlite_file_name, interactive) # recursively restart function

        else:
            print(f"Unexpected Error processing SQLite file:\n{traceback.format_exc()}")

    except Exception:
        print(f'Unexpected Error parsing Firefox SQLite databases:\n{traceback.format_exc()}')

    return None


def get_browser_config_paths() -> list[str]:
    """Returns a list of file system paths where web browsers
    would store configuration data in the current user profile and
    depending on the operating system.

    This function returns paths of all supported browsers regardless
    whether such a browser is installed or not.

    :return: A list of file system paths with potential web browser
        configuration data.
    :rtype: list[str]
    """
    browser_paths = []

    if platform.system() == 'Windows':
        appdata = os.getenv('appdata')
        local_appdata = os.getenv('localappdata')

        if appdata is None or local_appdata is None:
            raise RuntimeError("Windows OS AppData environment variables are empty but shouldn't.")

        browser_paths = [
            os.path.join(local_appdata, 'Google', 'Chrome', 'User Data'),
            os.path.join(local_appdata, 'Microsoft', 'Edge', 'User Data'),
            os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
            os.path.join(appdata, 'Opera Software', 'Opera Stable'),
            os.path.join(appdata, 'Opera Software', 'Opera GX Stable'),
            os.path.join(local_appdata, 'BraveSoftware', 'Brave-Browser', 'User Data'),
        ]

    elif platform.system() == 'Darwin': # macOS
        home = os.path.expanduser("~")
        # regarding safari comp:
        # https://stackoverflow.com/questions/58479686/permissionerror-errno-1-operation-not-permitted-after-macos-catalina-update

        browser_paths = [
            os.path.join(home, 'Library', 'Application Support', 'Google', 'Chrome'),
            os.path.join(home, 'Library', 'Application Support', 'Microsoft Edge'),
            os.path.join(home, 'Library', 'Application Support', 'Firefox', 'Profiles'),
            os.path.join(home, 'Library', 'Application Support', 'com.operasoftware.Opera'),
            os.path.join(home, 'Library', 'Application Support', 'com.operasoftware.OperaGX'),
            os.path.join(home, 'Library', 'Application Support', 'BraveSoftware'),
        ]

    elif platform.system() == 'Linux':
        home = os.path.expanduser("~")

        browser_paths = [
            os.path.join(home, '.config', 'google-chrome', 'Default'),
            os.path.join(home, '.mozilla', 'firefox'), # firefox non-snap (couldn't verify with ubuntu)
            os.path.join(home, 'snap', 'firefox', 'common', '.mozilla', 'firefox'), # firefox snap
            os.path.join(home, '.config', 'opera'), # btw opera gx, does not exist for linux
            os.path.join(home, '.config', 'BraveSoftware', 'Brave-Browser', 'Default'),
        ]

    return browser_paths


def find_leveldb_folders(root_path: str) -> set[str]:
    """Gets folders where leveldb (.ldb) files are located.
    
    :param str root_path: The directory path to start the search from.

    :return: A set of folder paths where leveldb files are located,
        potentially empty.
    :rtype: set[str]
    """
    leveldb_folders = set()

    for root, dirs, files in os.walk(root_path):
        for dir_name in dirs:
            if 'leveldb' in dir_name.lower():
                leveldb_folders.add(os.path.join(root, dir_name))
                break

        for file in files:
            if file.endswith('.ldb'):
                leveldb_folders.add(root)
                break

    return leveldb_folders


def close_browser_by_name(browser_name: str) -> None:
    """Closes an active web browser application by name
    eg. "Microsoft Edge" or "Opera Gx".

    :param str browser_name: The browser name.
    """
    # microsoft edge names its process msedge
    if browser_name == 'Microsoft Edge':
        browser_name = 'msedge'

    # opera gx just names its process opera
    elif browser_name == 'Opera Gx':
        browser_name = 'opera'

    browser_processes = [
        proc for proc in psutil.process_iter(attrs=['name'])
        if browser_name.lower() in proc.info['name'].lower()
    ]

    closed = False  # Flag to track if any process was closed

    if platform.system() == 'Windows':
        for proc in browser_processes:
            proc.terminate()
            closed = True

    elif platform.system() == 'Darwin' or platform.system() == 'Linux':
        for proc in browser_processes:
            proc.kill()
            closed = True

    if closed:
        print_config(f"Succesfully closed {browser_name} browser.")
        sleep(3) # give browser time to close its children processes


def parse_browser_from_string(browser_name: str) -> str:
    """Returns a normalized browser name according to the input
    or "Unknown".
    
    :param str browser_name: The web browser name to analyze.

    :return: A normalized (simplified/standardised) browser name
        or "Unknown".
    :rtype: str
    """
    compatible_browsers = [
        'Firefox',
        'Brave',
        'Opera GX',
        'Opera',
        'Chrome',
        'Edge'
    ]

    for compatible_browser in compatible_browsers:
        if compatible_browser.lower() in browser_name.lower():
            if compatible_browser.lower() == 'edge' and 'microsoft' in browser_name.lower():
                return 'Microsoft Edge'
            else:
                return compatible_browser

    return "Unknown"


def get_auth_token_from_leveldb_folder(leveldb_folder: str, interactive: bool=True) -> str | None:
    """Gets a Fansly authorization token from a leveldb folder.
    
    :param str leveldb_folder: The leveldb folder.

    :return: A Fansly authorization token or None.
    :rtype: str | None
    """
    try:
        db = plyvel.DB(leveldb_folder, compression='snappy')

        key = b'_https://fansly.com\x00\x01session_active_session'
        value = db.get(key)

        if value:
            session_active_session = value.decode('utf-8').replace('\x00', '').replace('\x01', '')
            auth_token = json.loads(session_active_session).get('token')
            db.close()
            return auth_token

        else:
            db.close()
            return None

    except plyvel._plyvel.IOError as e:
        error_message = str(e)
        used_browser = parse_browser_from_string(error_message)

        if not interactive:
            # Do not forcefully close user's browser in non-interactive/scheduled mode.
            return None

        print_config(
            f"{used_browser} browser is open but it needs to be closed for automatic configurator"
            f"\n{19*' '}to search your Fansly account in the browser's storage."
            f"\n{19*' '}Please save any important work within the browser & close the browser yourself"
            f"\n{19*' '}or it will be closed automatically after continuing."
        )

        input(f"\n{19*' '}► Press <ENTER> to continue! ")

        close_browser_by_name(used_browser)

        # recursively restart function
        return get_auth_token_from_leveldb_folder(leveldb_folder, interactive)

    except Exception:
        return None
