import os, plyvel, json, requests, traceback, psutil, platform, sqlite3, sys
from functools import partialmethod
from loguru import logger as log
from os.path import join
from time import sleep as s

# overwrite default exit, with a pyinstaller compatible one
def exit():
    os._exit(0)

def output(level: int, log_type: str, color: str, mytext: str):
    try:
        log.level(log_type, no = level, color = color)
    except TypeError:
        pass # level failsafe
    log.__class__.type = partialmethod(log.__class__.log, log_type)
    log.remove()
    log.add(sys.stdout, format = "<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>", level=log_type)
    log.type(mytext)

# Function to recursively search for "storage" folders and process SQLite files
def process_storage_folders(directory):
    for root, _, files in os.walk(directory):
        if "storage" in root:
            for file in files:
                if file.endswith(".sqlite"):
                    sqlite_file = join(root, file)
                    session_active_session = process_sqlite_file(sqlite_file)
                    if session_active_session:
                        return session_active_session


# Function to read SQLite file and retrieve key-value pairs
def process_sqlite_file(sqlite_file):
    session_active_session = None
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        # Get all table names in the SQLite database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            for row in rows:
                if row[0] == 'session_active_session':
                    session_active_session = json.loads(row[5].decode('utf-8'))['token']
                    break

        conn.close()

        return session_active_session
    
    except sqlite3.Error as e:
        sqlite_error = str(e)
        if 'locked' in sqlite_error and 'irefox' in sqlite_file:
            output(5,'\n Config','<light-magenta>', f"Firefox browser is open, but it needs to be closed for automatic configurator\n\
            {11*' '}to search your fansly account in the browsers storage.\n\
            {11*' '}Please save any important work within the browser & close the browser yourself,\n\
            {11*' '}else press Enter to close it programmatically and continue configuration.")
            input(f"\n{19*' '} ► Press Enter to continue! ")
            close_browser_by_name('firefox')
            return process_sqlite_file(sqlite_file) # recursively restart function
        else:
            print(f"Unexpected Error processing SQLite file: {traceback.format_exc()}")
    except Exception:
        print(f'Unexpected Error, parsing out of firefox SQLite {traceback.format_exc()}')
    return None


def get_browser_paths():
    if platform.system() == 'Windows':
        local_appdata = os.getenv('localappdata')
        appdata = os.getenv('appdata')
        browser_paths = [
            join(local_appdata, 'Google', 'Chrome', 'User Data'),
            join(local_appdata, 'Microsoft', 'Edge', 'User Data'),
            join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
            join(appdata, 'Opera Software', 'Opera Stable'),
            join(appdata, 'Opera Software', 'Opera GX Stable'),
            join(local_appdata, 'BraveSoftware', 'Brave-Browser', 'User Data'),
        ]
    elif platform.system() == 'Darwin': # macOS
        home = os.path.expanduser("~")
        # regarding safari comp: https://stackoverflow.com/questions/58479686/permissionerror-errno-1-operation-not-permitted-after-macos-catalina-update
        browser_paths = [
        join(home, 'Library', 'Application Support', 'Google', 'Chrome'),
        join(home, 'Library', 'Application Support', 'Microsoft Edge'),
        join(home, 'Library', 'Application Support', 'Firefox', 'Profiles'),
        join(home, 'Library', 'Application Support', 'com.operasoftware.Opera'),
        join(home, 'Library', 'Application Support', 'com.operasoftware.OperaGX'),
        join(home, 'Library', 'Application Support', 'BraveSoftware'),
        ]
    elif platform.system() == 'Linux':
        home = os.path.expanduser("~")
        browser_paths = [
            join(home, '.config', 'google-chrome', 'Default'),
            join(home, '.mozilla', 'firefox'), # firefox non-snap (couldn't verify with ubuntu)
            join(home, 'snap', 'firefox', 'common', '.mozilla', 'firefox'), # firefox snap
            join(home, '.config', 'opera'), # btw opera gx, does not exist for linux
            join(home, '.config', 'BraveSoftware', 'Brave-Browser', 'Default'),
        ]
    return browser_paths


def find_leveldb_folders(root_path):
    leveldb_folders = set()
    for root, dirs, files in os.walk(root_path):
        for dir_name in dirs:
            if 'leveldb' in dir_name.lower():
                leveldb_folders.add(join(root, dir_name))
                break
        for file in files:
            if file.endswith('.ldb'):
                leveldb_folders.add(root)
                break
    return leveldb_folders


def close_browser_by_name(browser_name):
    # microsoft edge names its process msedge
    if browser_name == 'Microsoft Edge':
        browser_name = 'msedge'
    # opera gx just names its process opera
    elif browser_name == 'Opera Gx':
        browser_name = 'opera'

    browser_processes = [proc for proc in psutil.process_iter(attrs=['name']) if browser_name.lower() in proc.info['name'].lower()]
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
        output(5,'\n Config','<light-magenta>', f"Succesfully closed {browser_name} browser.")
        s(3) # give browser time to close its children processes

def parse_browser_from_string(string):
    compatible = ['Firefox', 'Brave', 'Opera GX', 'Opera', 'Chrome', 'Edge']
    for browser in compatible:
        if browser.lower() in string.lower():
            if browser.lower() == 'edge' and 'microsoft' in string.lower():
                return 'Microsoft Edge'
            else:
                return browser
    return "Unknown"

def get_auth_token_from_leveldb_folder(leveldb_folder):
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
        output(5,'\n Config','<light-magenta>', f"{used_browser} browser is open, but it needs to be closed for automatic configurator\n\
        {11*' '}to search your fansly account in the browsers storage.\n\
        {11*' '}Please save any important work within the browser & close the browser yourself,\n\
        {11*' '}else press Enter to close it programmatically and continue configuration.")
        input(f"\n{19*' '} ► Press Enter to continue! ")
        close_browser_by_name(used_browser)
        return get_auth_token_from_leveldb_folder(leveldb_folder) # recursively restart function
    except Exception:
        return None


def link_fansly_downloader_to_account(auth_token):
    headers = {
        'authority': 'apiv3.fansly.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en;q=0.8,en-US;q=0.7',
        'authorization': auth_token,
        'origin': 'https://fansly.com',
        'referer': 'https://fansly.com/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    me_req = requests.get('https://apiv3.fansly.com/api/v1/account/me', params={'ngsw-bypass': 'true'}, headers=headers)
    if me_req.status_code == 200:
        me_req = me_req.json()['response']['account']
        account_username = me_req['username']
        if account_username:
            return account_username
    return None
