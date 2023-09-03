# Rewrite Notes

Notes about the challenges and important changes during the major rewrite.

* Used an IMHO good IDE - Visual Studio Code with the official Python module and Pylance - which has great code quality (potentially unininitalized variables, unused variables, ...) and refactoring features (renaming, find usages, ...). There is also an excellent TODO Tree extension.
* Code developed and tested on Python 3.11.4 x64 for Windows.
* Introduced static typing where I thought of it especially functions and classes. This makes functions interfaces and their intentions clear, where code breaks them and what is expected to be passed around where.
* Documented functions as much as I could to also improve my understanding of the code. This also led to function renames to express their purpose more clearly.
* Partitioned code into functions to modularize it.
* Spread out functions in modules and separate files especially long functions.
* Switched to Context Managers (`with`) where appropriate to avoid potentially leaking resources on unexpected exceptions.
* Switched to the often more elegant `pathlib` library and `Path` where fesasible. Only `os.walk()` has no alternative yet.
* Used `fallback=` in `configparser` getters to be more resilient and allow minimal configuration files. Default values match the contents of the original `config.ini` from the repository.
* Renamed `utilise_duplicate_threshold` to `use_duplicate_threshold` but code retains compatibility with older `config.ini` files.
* Introduced `use_suffix` option in `config.ini`. If I have a folder for all my Fansly downloads, I do not see the point of suffixing every creator's subfolder with `_fansly`. This especially makes no sense any more since the rewritten code does not need to parse out the creator's folder from an arbitrary path in odd places. I did, however, retain the previous behavior - it defaults to `True`.
* Having the program version in a config file (`config.ini`) makes no sense and is potentially dangerous. The program version should (and is now) in a proper file heading block and can be read from there. Versioning a config file might make sense in some cases but all the changes to config structure so far can easily be handled by the config read/validation functions without reliance on versioning.
* While reworking `delete_deprecated_files()` I found a bug - `os.path.splitext()` includes the full path to the file name thus the `in` must have always failed. (See https://docs.python.org/3/library/os.path.html - "`root + ext == path`")
* I corrected the ratios for `rich`'s `TextColumn`/`BarColumn`: They are `int`s now, I assumed 2/5 thus 1; 5 (were: 0.355; 2).
* Switched to `Enum`s (`StrEnum`) for `download_mode` and `download_type` to be explicit and prevent magical string values floating around
* I made all hard errors `raise` and introduced an `interactive` flag (also as `config.ini` option) to bypass any `Press <ENTER> to continue` prompts. Thus you can now automate/schedule it using `Task Scheduler` on Windows or `cron` on Linux/UNIX or just have it run through while you are away. What is more, this also helps multiple user processing - an account info error due to invalid user name should not prevent all other users from being downloaded and can be caught in the user loop.
* There also now distinct program exit codes to facilitate automation.
* There is now a `prompt_on_exit` setting. This might seem redundant to `interactive` but helps for semi-automated runs (`interactive=False`) letting the computer run and when coming back wanting to see what happened meanwhile in the console window. For a truly automated/scheduled experience you need to set both `interactive` and `prompt_on_exit` to `False`.
* I made - hopefully - arg parsing foolproof by using a separate temporary `config_args.ini` for that scenario. Thus the validation functions, which may alter and save the config, are prevented from overwriting the users' original configuration as are other cases where `save_config_or_raise()` might be called.
* What's to difficult to test for me is the self-updating functionality. I rewrote it to the best of my knowledge but since it references the original repo and such, only accepted PR and time will tell.
* Renamed `use_suffix` to `use_folder_suffix` to be more clear and better convey meaning.
* All `config.ini` options have finally been implemented as command-line arguments.
* Since everything is now properly defaulted and handled (I hope) you are now able to run `Fansly Downloader` with empty config files or no `config.ini` at all :D You just need the executable and are good to go.
* Als worked around an issue in Firefox token retrieval where differently encoded DBs woult throw `sqlite3.OperationalError`.
* `Fansly Downloader` now also logs output to file, at least all stuff going through `loguru`. Log-rollover is at 1 MiB size and keeping the last 5 files.

-- prof79
