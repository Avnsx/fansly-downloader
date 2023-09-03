"""Self-Update Utility Functions"""


import dateutil.parser
import os
import platform
import re
import requests
import subprocess
import sys

import fansly_downloader.errors as errors

from pathlib import Path
from pkg_resources._vendor.packaging.version import parse as parse_version
from shutil import unpack_archive

from fansly_downloader.config import FanslyConfig
from fansly_downloader.textio import clear_terminal, print_error, print_info, print_update, print_warning
from fansly_downloader.utils.web import get_release_info_from_github


def delete_deprecated_files() -> None:
    """Deletes deprecated files after an update."""
    old_files = [
        "old_updater",
        "updater",
        "Automatic Configurator",
        "Fansly Scraper",
        "deprecated_version",
        "old_config"
    ]

    directory = Path.cwd()

    for root, _, files in os.walk(directory):
        for file in files:

            file_object = Path(file)

            if file_object.suffix.lower() != '.py' and file_object.stem in old_files:

                file_path = Path(root) / file

                if file_path.exists():
                    file_path.unlink()


def display_release_notes(program_version: str, release_notes: str) -> None:
    """Displays the release notes of a Fansly Downloader version.
    
    :param str program_version: The Fansly Downloader version.
    :param str release_notes: The corresponding release notes.
    """
    print_update(f"Successfully updated to version {program_version}!\n\n► Release Notes:\n{release_notes}")
    print()
    input('Press <ENTER> to start Fansly Downloader ...')

    clear_terminal()


def parse_release_notes(release_info: dict) -> str | None:
    """Parse the release notes from the release info dictionary
    obtained from GitHub.

    :param dict release_info: Program release information from GitHub.

    :return: The release notes or None if there was empty content or
        a parsing error.
    :rtype: str | None
    """
    release_body = release_info.get("body")

    if not release_body:
        return None

    body_match = re.search(
        r"```(.*)```",
        release_body,
        re.DOTALL | re.MULTILINE
    )

    if not body_match:
        return None

    release_notes = body_match[1]

    if not release_notes:
        return None

    return release_notes


def perform_update(program_version: str, release_info: dict) -> bool:
    """Performs a self-update of Fansly Downloader.

    :param str program_version: The current program version.
    :param dict releas_info: Release information from GitHub.

    :return: True if successful or False otherwise.
    :rtype: bool
    """
    print_warning(f"A new version of fansly downloader has been found on GitHub - update required!")
    
    print_info(f"Latest Build:\n{18*' '}Version: {release_info['release_version']}\n{18*' '}Published: {release_info['created_at']}\n{18*' '}Download count: {release_info['download_count']}\n\n{17*' '}Your version: {program_version} is outdated!")
    
    # if current environment is pure python, prompt user to update fansly downloader himself
    if not getattr(sys, 'frozen', False):
        print_warning(f"To update Fansly Downloader, please download the latest version from the GitHub repository.\n{20*' '}Only executable versions of the downloader receive & apply updates automatically.\n")
        # but we don't care if user updates or just wants to see this prompt on every execution further on
        return False
    
    # if in executable environment, allow self-update
    print_update('Please be patient, automatic update initialized ...')

    # download new release
    release_download = requests.get(
        release_info['download_url'],
        allow_redirects=True,
        headers = {
            'user-agent': f'Fansly Downloader {program_version}',
            'accept-language': 'en-US,en;q=0.9'
        }
    )

    if release_download.status_code != 200:
        print_error(f"Failed downloading latest build. Status code: {release_download.status_code} | Body: \n{release_download.text}")
        return False
    
    # re-name current executable, so that the new version can delete it
    try:
        downloader_name = 'Fansly Downloader'
        new_name = 'deprecated_version'
        suffix = ''

        if platform.system() == 'Windows':
            suffix = '.exe'

        downloader_path = Path.cwd() / f'{downloader_name}{suffix}'
        downloader_path.rename(downloader_path.parent / f'{new_name}{suffix}')

    except FileNotFoundError:
        pass
    
    # re-name old config ini, so new executable can read, compare and delete old one
    try:
        config_file = Path.cwd() / 'config.ini'
        config_file.rename(config_file.parent / 'old_config.ini')

    except Exception:
        pass

    # declare new release filepath
    new_release_archive = Path.cwd() / release_info['release_name']

    # write to disk
    with open(new_release_archive, 'wb') as f:
        f.write(release_download.content)
    
    # unpack if possible; for macOS .dmg this won't work though
    try:
        # must be a common archive format (.zip, .tar, .tar.gz, .tar.bz2, etc.)
        unpack_archive(new_release_archive)
        # remove .zip leftovers
        new_release_archive.unlink()

    except Exception:
        pass

    # start executable from just downloaded latest platform compatible release, with a start argument
    # which instructs it to delete old executable & display release notes for newest version
    current_platform = platform.system()
    # from now on executable will be called Fansly Downloader
    filename = 'Fansly Downloader'

    if current_platform == 'Windows':
        filename = filename + '.exe'

    filepath = Path.cwd() / filename

    # Carry command-line arguments over
    additional_arguments = ['--updated-to', release_info['release_version']]
    arguments = sys.argv[1:] + additional_arguments
    
    if current_platform == 'Windows':
        # i'm open for improvement suggestions, which will be insensitive to file paths & succeed passing start arguments to compiled executables
        subprocess.run(['powershell', '-Command', f"Start-Process -FilePath '{filepath}' -ArgumentList {', '.join(arguments)}"], shell=True)

    elif current_platform == 'Linux':
        # still sensitive to file paths?
        subprocess.run([filepath, *arguments], shell=True)

    elif current_platform == 'Darwin':
        # still sensitive to file paths?
        subprocess.run(['open', filepath, *arguments], shell=False)

    else:
        input(f"Platform {current_platform} not supported for auto-update, please update manually instead.")
        os._exit(errors.UPDATE_MANUALLY)
    
    os._exit(errors.UPDATE_SUCCESS)


def post_update_steps(program_version: str, release_info: dict | None) -> None:
    """Performs necessary steps after  a self-update.
    
    :param str program_version: The program version updated to.
    :param dict release_info: The version's release info from GitHub.
    """
    if release_info is not None:
        release_notes = parse_release_notes(release_info)

        if release_notes is not None:
            display_release_notes(program_version, release_notes)


def check_for_update(config: FanslyConfig) -> bool:
    """Checks for an updated program version.

    :param FanslyConfig config: The program configuration including the
        current version number.

    :return: False if anything went wrong (network errors, ...)
        or True otherwise.
    :rtype: bool
    """
    release_info = get_release_info_from_github(config.program_version)

    if release_info is None:
        return False
    
    else:
        # we don't want to ship drafts or pre-releases
        if release_info["draft"] or release_info["prerelease"]:
            return False
        
        # remove the string "v" from the version tag
        new_version = release_info["tag_name"].split('v')[1]
        
        # we do only want current platform compatible updates
        new_release = None
        current_platform = 'macOS' if platform.system() == 'Darwin' else platform.system()

        for new_release in release_info['assets']:
            if current_platform in new_release['name']:
                d = dateutil.parser.isoparse(new_release['created_at']).replace(tzinfo=None)

                parsed_date = f"{d.strftime('%d')} {d.strftime('%B')[:3]} {d.strftime('%Y')}"

                new_release = {
                    'release_name': new_release['name'],
                    'release_version': new_version,
                    'created_at': parsed_date,
                    'download_count': new_release['download_count'],
                    'download_url': new_release['browser_download_url']
                }

        if new_release is None:
            return False
    
        empty_values = [
            value is None for key, value in new_release.items()
            if key != 'download_count'
        ]

        if any(empty_values):
            return False

        # just return if our current version is still sufficient
        if parse_version(config.program_version) >= parse_version(new_version):
            return True

        else:
            return perform_update(config.program_version, release_info)
