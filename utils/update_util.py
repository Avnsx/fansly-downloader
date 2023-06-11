# have to eventually remove dateutil requirement
import os, requests, re, platform, sys, subprocess
from os.path import join
from os import getcwd
from loguru import logger as log
from functools import partialmethod
import dateutil.parser as dp
from shutil import unpack_archive
from configparser import RawConfigParser


# most of the time, we utilize this to display colored output rather than logging or prints
def output(level: int, log_type: str, color: str, mytext: str):
    try:
        log.level(log_type, no = level, color = color)
    except TypeError:
        pass # level failsafe
    log.__class__.type = partialmethod(log.__class__.log, log_type)
    log.remove()
    log.add(sys.stdout, format = "<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>", level=log_type)
    log.type(mytext)


# clear the terminal based on the operating system
def clear_terminal():
    system = platform.system()
    if system == 'Windows':
        os.system('cls')
    else: # Linux & macOS
        os.system('clear')


def apply_old_config_values():
    current_directory = getcwd()
    old_config_path = join(current_directory, 'old_config.ini')
    new_config_path = join(current_directory, 'config.ini')

    if os.path.isfile(old_config_path) and os.path.isfile(new_config_path):
        old_config = RawConfigParser()
        old_config.read(old_config_path)

        new_config = RawConfigParser()
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


def delete_deprecated_files():
    executables = ["old_updater", "updater", "Automatic Configurator", "Fansly Scraper", "deprecated_version", "old_config"]
    directory = getcwd()

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if file_extension.lower() != '.py' and file_name in executables:
                file_path = join(root, file)
                if os.path.exists(file_path):
                    os.remove(file_path)


def display_release_notes(version_string: str, code_contents: str):
    output(6,'\n Updater', '<light-green>', f"Successfully updated to version {version_string}\n\n ► Release Notes:{code_contents}")

    input('Press Enter to start Fansly Downloader ...')

    clear_terminal()


def get_release_description(version_string, response_json):
    release_body = response_json.get("body")
    if not release_body:
        return None

    code_contents = re.search(r"```(.*)```", release_body, re.DOTALL | re.MULTILINE)[1]
    if not code_contents:
        return None

    display_release_notes(version_string, code_contents)


def handle_update(current_version: str, release: dict):
    output(3, '\n WARNING', '<yellow>', f"A new version of fansly downloader has been found on GitHub; update required!")
    
    output(1, '\n info', '<light-blue>', f"Latest Build:\n{18*' '}Version: {release['release_version']}\n{18*' '}Published: {release['created_at']}\n{18*' '}Download count: {release['download_count']}\n\n{17*' '}Your version: {current_version} is outdated!")
    
    # if current environment is pure python, prompt user to update fansly downloader himself
    if not getattr(sys, 'frozen', False):
        output(3, '\n WARNING', '<yellow>', f"To update Fansly Downloader, please download the latest version from the GitHub repository.\n{20*' '}Only executable versions of the downloader, receive & apply updates automatically.\n")
        return False # but we don't care if user updates or just wants to see this prompt on every execution further on
    
    # if in executable environment, allow self-update
    output(6,'\n Updater', '<light-green>', 'Please be patient, automatic update initialized ...')

    # download new release
    release_download = requests.get(release['download_url'], allow_redirects = True, headers = {'user-agent': f'Fansly Downloader {current_version}', 'accept-language': 'en-US,en;q=0.9'})
    if not release_download.ok:
        output(2,'\n ERROR', '<red>', f"Failed downloading latest build. Release request status code: {release_download.status_code} | Body: \n{release_download.text}")
        return False
    
    # re-name current executable, so that the new version can delete it
    try:
        if platform.system() == 'Windows':
            os.rename(join(getcwd(), 'Fansly Downloader.exe'), join(getcwd(), 'deprecated_version.exe'))
        else:
            os.rename(join(getcwd(), 'Fansly Downloader'), join(getcwd(), 'deprecated_version'))
    except FileNotFoundError:
        pass
    
    # re-name old config ini, so new executable can read, compare and delete old one
    try:
        os.rename(join(getcwd(), 'config.ini'), join(getcwd(), 'old_config.ini'))
    except Exception:
        pass

    # declare new release filepath
    new_release_filepath = join(getcwd(), release['release_name'])

    # write to disk
    with open(new_release_filepath, 'wb') as f:
        f.write(release_download.content)
    
    # unpack if possible; for macOS .dmg this won't work though
    try:
        unpack_archive(new_release_filepath) # must be a common archive format (.zip, .tar, .tar.gz, .tar.bz2, etc.)
        os.remove(new_release_filepath) # remove .zip leftovers
    except Exception:
        pass

    # start executable from just downloaded latest platform compatible release, with a start argument
    # which instructs it to delete old executable & display release notes for newest version
    plat = platform.system()
    filename = 'Fansly Downloader' # from now on; executable always has to be called Fansly Downloader
    if plat == 'Windows':
        filename = filename+'.exe'
    filepath = join(getcwd(), filename)

    if plat == 'Windows':
        arguments = ['--update', release['release_version']] # i'm open for improvement suggestions, which will be insensitive to file paths & succeed passing start arguments to compiled executables
        subprocess.run(['powershell', '-Command', f"Start-Process -FilePath \'{filepath}\' -ArgumentList {', '.join(arguments)}"], shell=True)
    elif plat == 'Linux':
        subprocess.run([filepath, '--update', release['release_version']], shell=True) # still sensitive to file paths?
    elif plat == 'Darwin':
        subprocess.run(['open', filepath, '--update', release['release_version']], shell=False) # still sensitive to file paths?
    else:
        input(f"Platform {plat} not supported for auto update, please manually update instead.")
    
    os._exit(0)


def check_latest_release(update_version: str = 0, current_version: str = 0, intend: str = None): # intend: update / check
    try:
        url = f"https://api.github.com/repos/avnsx/fansly-downloader/releases/latest"
        response = requests.get(url, allow_redirects = True, headers={'user-agent': f'Fansly Downloader {update_version if update_version is not None else current_version}', 'accept-language': 'en-US,en;q=0.9'})
        response.raise_for_status()
    except Exception:
        return False
    
    if not response.ok:
        return False
    
    response_json = response.json()
    if intend == 'update':
        get_release_description(update_version, response_json)
    elif intend == 'check':
        # we don't want to ship drafts or pre-releases
        if response_json["draft"] or response_json["prerelease"]:
            return False
        
        # remove the string "v" from the version tag
        if not update_version:
            update_version = response_json["tag_name"].split('v')[1]
        
        # we do only want current platform compatible updates
        release = None
        current_platform = 'macOS' if platform.system() == 'Darwin' else platform.system()
        for release in response_json['assets']:
            if current_platform in release['name']:
                d=dp.isoparse(release['created_at']).replace(tzinfo=None)
                parsed_date = f"{d.strftime('%d')} {d.strftime('%B')[:3]} {d.strftime('%Y')}"
                release = {'release_name': release['name'], 'release_version': update_version, 'created_at': parsed_date, 'download_count': release['download_count'], 'download_url': release['browser_download_url']}
        if not release or any(value is None for key, value in release.items() if key != 'download_count'):
            return False
        
        # just return if our current version is still sufficient
        if current_version >= update_version:
            return
        else:
            handle_update(current_version, release)
