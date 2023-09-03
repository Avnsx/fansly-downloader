"""Console Output"""


import os
import platform
import subprocess
import sys

from functools import partialmethod
from time import sleep
from loguru import logger
from pathlib import Path


LOG_FILE_NAME: str = 'fansly_downloader.log'


# most of the time, we utilize this to display colored output rather than logging or prints
def output(level: int, log_type: str, color: str, message: str) -> None:
    try:
        logger.level(log_type, no = level, color = color)

    except TypeError:
        # level failsafe
        pass 

    logger.__class__.type = partialmethod(logger.__class__.log, log_type)

    logger.remove()

    logger.add(
        sys.stdout,
        format="<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>",
        level=log_type,
    )
    logger.add(
        Path.cwd() / LOG_FILE_NAME,
        encoding='utf-8',
        format="[{level} ] [{time:YYYY-MM-DD} | {time:HH:mm}]: {message}",
        level=log_type,
        rotation='1MB',
        retention=5,
    )

    logger.type(message)


def print_config(message: str) -> None:
    output(5, ' Config', '<light-magenta>', message)


def print_debug(message: str) -> None:
    output(7,' DEBUG', '<light-red>', message)


def print_error(message: str, number: int=-1) -> None:
    if number >= 0:
        output(2, f' [{number}]ERROR', '<red>', message)
    else:
        output(2, ' ERROR', '<red>', message)


def print_info(message: str) -> None:
    output(1, ' Info', '<light-blue>', message)


def print_info_highlight(message: str) -> None:
    output(4, ' lnfo', '<light-red>', message)


def print_update(message: str) -> None:
    output(6,' Updater', '<light-green>', message)


def print_warning(message: str) -> None:
    output(3, ' WARNING', '<yellow>', message)


def input_enter_close(interactive: bool=True) -> None:
    """Asks user for <ENTER> to close and exits the program.
    In non-interactive mode sleeps instead, then exits.
    """
    if interactive:
        input('\nPress <ENTER> to close ...')

    else:
        print('\nExiting in 15 seconds ...')
        sleep(15)

    exit()


def input_enter_continue(interactive: bool=True) -> None:
    """Asks user for <ENTER> to continue.
    In non-interactive mode sleeps instead.
    """
    if interactive:
        input('\nPress <ENTER> to attempt to continue ...')
    else:
        print('\nContinuing in 15 seconds ...')
        sleep(15)


# clear the terminal based on the operating system
def clear_terminal() -> None:
    system = platform.system()

    if system == 'Windows':
        os.system('cls')

    else: # Linux & macOS
        os.system('clear')


# cross-platform compatible, re-name downloaders terminal output window title
def set_window_title(title) -> None:
    current_platform = platform.system()

    if current_platform == 'Windows':
        subprocess.call('title {}'.format(title), shell=True)

    elif current_platform == 'Linux' or current_platform == 'Darwin':
        subprocess.call(['printf', r'\33]0;{}\a'.format(title)])
