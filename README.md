# [Fansly Downloader / Fansly Scraper ](https://github.com/Avnsx/fansly)
![Downloads](https://img.shields.io/github/downloads/Avnsx/fansly/total?color=0078d7&label=🔽%20Downloads.exe&style=flat-square) ![Compatibility](https://img.shields.io/static/v1?style=flat-square&label=%F0%9F%90%8D%20Python&message=3.6%2B&color=blue) [![Discord](https://img.shields.io/discord/522310203828338701?color=6A7EC2&label=Discord&logo=discord&logoColor=ffffff&style=flat-square)](https://discord.gg/Dr8wt84z2E) ![Stars](https://img.shields.io/github/stars/Avnsx/fansly?style=flat-square&label=⭐%20Stars&color=ffc83d)

![UI Banner](https://i.imgur.com/EhL42m3.jpg)

## Description:
On click code, to scrape your favorite fansly creators media content. After you've ran the code, it'll create a folder named ``CreatorName_fansly`` in the same directory you launched the code from. That folder will have two sub-folders called Pictures & Videos, which will contain the downloaded content sorted into them.
This is pretty useful for example; if you dislike the website theming and would like to view the media on your local machine instead. This code does not bypass any paywalls & no end user information is collected during usage.

[Click me if you want a detailed description on each of the components of this software!](https://github.com/Avnsx/fansly/wiki/Explanation-of-provided-programs-&-their-functionality)

## Installation
You can just install the [Executable version](https://github.com/Avnsx/fansly/releases/latest), skip the entire installation section & go to [Quick Start](https://github.com/Avnsx/fansly#quick-start)

#### Requirements
	pip install requests loguru imagehash pillow python-dateutil psutil keyboard selenium-wire undetected_chromedriver==3.0.6 pycryptodome pywin32
or you can use [``requirements.txt``](https://github.com/Avnsx/fansly/blob/main/requirements.txt) to install the requirements above.

If you get an error while installing requirements with ``pywin32``; it is a windows only library and is not definitely required for the scraper itsself. Only ``automatic_configurator.py`` needs it. If for some reason you can't install it with pip, you can also install it [through pywin32's github](https://github.com/mhammond/pywin32/releases) or you might also be able to install that by ``pip install pypiwin32`` or ``conda install pywin32``

## Quick Start
**Quick start is only compatible with Windows & you to have to have recently logged into fansly in any of the following browsers: Chrome, FireFox, Opera, Brave or Microsoft Edge and one of those browsers has to be set as your default browser in windows settings.**
1. Make sure the browser you set as default browser in windows settings, is also the browser that you've browsed fansly with in the past
2. Click on Automatic Configurator and wait for it [to do its thing](https://github.com/Avnsx/fansly/wiki/Explanation-of-provided-programs-&-their-functionality#2-automatic-configurator)
3. If it was successful(``config.ini`` should now only show a single ``ReplaceMe`` the targeted creator name) open the ``config.ini`` file and replace the value for ``[TargetedCreator]`` > ``Username =`` with whatever content creator you wish to have scraped
4. Save the ``config.ini`` file(into the same directory as fansly scraper) with the changes you've done to it, close it & then start up Fansly Scraper by clicking on it

**!!! If you are using a different OS or are encountering a bug with quick start please head over to [Get Started](https://github.com/Avnsx/fansly/wiki/Get-Started) instead !!!**

After completing any of the configuration tutorials [Quick Start](https://github.com/Avnsx/fansly#quick-start) / [Get Started](https://github.com/Avnsx/fansly/wiki/Get-Started); in the future you'll only need to change the creator name for Targeted Creator > Username in ``config.ini`` for every further use case on other creators.


## FAQ
Do you have any unanswered questions or want to know more about fansly scraper? Head over to the [Wiki](https://github.com/Avnsx/fansly/wiki)

Q: "Could you add X feature or do X change?"
A: Star the project and I'll think about it. Otherwise you could always [open a pull request](https://github.com/Avnsx/fansly/pulls)

Q: "I'm encountering an actual bug, that is actually pointing to a coding mistake."
A: Open an Issue, I'll look at it asap

Q: "I used the automatic way and my browser now displays insecure on fansly.com!"
A: That's a rare bug, caused by automatic configurator just press on the lock icon in the left side of your url bar, while being on fansly.com > click on cookies > remove & refresh the site and you're good

## Funding
Dependent on how many people show me that they're liking the code by giving ⭐'s on this repo, I'll expand functionality & push more quality of life updates.
Would you like to help out more? Any crypto donations are welcome!

BTC: bc1q82n68gmdxwp8vld524q5s7wzk2ns54yr27flst

ETH: 0x645a734Db104B3EDc1FBBA3604F2A2D77AD3BDc5

## Disclaimer
"Fansly" or fansly.com is operated by Select Media LLC as stated on their "Contact" page. This repository (Avnsx/"fansly") and the provided content in it isn't in any way affiliated with, sponsored by, or endorsed by Select Media LLC or "Fansly". The developer(referred to: "Avnsx" in the following) of this code is not responsible for the end users actions, no unlawful activities of any kind are being encouraged. Statements and processes described in this repository only represent best practice guidance aimed at fostering an effective software usage. The repository was written purely for educational purposes, in an entirely theoretical environment. Thus, any information is presented on the condition that the developer of this code shall not be held liable in no event to you or anyone else for any direct, special, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including without limitation, loss of profit, loss of use, savings or revenue, or the claims of third parties, whether the developer has advised of the possibility of such loss, however caused and on any theory of liability, arising out of or in connection with the possession, use or performance of this software. The material embodied in this repository is supplied to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty of fitness. This disclaimer is preliminary and is subject to revision.
##
Written with python 3.9.7 for Windows 10, Version 21H1 Build 19043.1237
