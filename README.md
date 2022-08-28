# Fansly Scraper / Fansly Downloader
![Downloads](https://img.shields.io/github/downloads/Avnsx/fansly/total?color=0078d7&label=🔽%20Downloads.exe&style=flat-square) ![Compatibility](https://img.shields.io/static/v1?style=flat-square&label=%F0%9F%90%8D%20Python&message=3.6%2B&color=blue) ![Stars](https://img.shields.io/github/stars/Avnsx/fansly?style=flat-square&label=⭐%20Stars&color=ffc83d)

![UI Banner](https://i.imgur.com/EhL42m3.jpg)

## 👋 Introducing ``Fansly Scraper``
Easy to use Fansly Downloader for Videos and Photos from your favorite fansly creators. After you've launched the program, it'll create a folder named ``CreatorName_fansly`` in the same directory you launched it from. That folder will have two sub-folders called Pictures & Videos, which will contain the downloaded content sorted into them.
This is pretty useful for example; if you dislike the website theming and would like to view the media on your local machine instead. This code does not bypass any paywalls & no end user information is collected during usage.

[Click me if you want a detailed description on each of the components of this software!](https://github.com/Avnsx/fansly/wiki/Explanation-of-provided-programs-&-their-functionality)

### Many Thanks to all the `Stargazers` who have supported this project with stars(⭐)

[![Stargazers repo roster for @Avnsx/fansly](https://reporoster.com/stars/Avnsx/fansly)](https://github.com/Avnsx/fansly/stargazers)

## 🏗️ Set up
You can just install the [Executable version](https://github.com/Avnsx/fansly/releases/latest), skip the entire set up section & go to [Quick Start](https://github.com/Avnsx/fansly#-quick-start)

#### Requirements
If you want to use the python source directly, please install following requirements into your environment:

	pip install requests loguru imagehash pillow python-dateutil psutil keyboard "undetected_chromedriver>=3.1.5" pycryptodome pywin32
or you can use [``requirements.txt``](https://github.com/Avnsx/fansly/blob/main/requirements.txt) with ``pip install --user -r requirements.txt`` into ``cmd.exe`` from project download folder to install them.

If you get an error while installing requirements with ``pywin32``; it is a windows only library and is not definitely required for the scraper itsself. Only ``automatic_configurator.py`` needs it. If for some reason you can't install it with pip, you can also install it [through pywin32's github](https://github.com/mhammond/pywin32/releases) or you might also be able to install that by ``pip install pypiwin32`` or ``conda install pywin32``. If you can't install pywin32 that obviously means that you won't be able to run automatic configurator and need to use [Get Started](https://github.com/Avnsx/fansly/wiki/Get-Started) instead to set it up.

## 🚀 Quick Start
**Quick start is only compatible with Windows & you to have to have recently logged into fansly in any of the following browsers: Chrome, FireFox, Opera, Brave or Microsoft Edge and that browser has to be [set as your default browser in windows settings](https://www.avast.com/c-change-default-browser-windows#:~:text=Open%20the%20Start%20menu%20and,is%20the%20current%20default%20browser.).**
1. Make sure the browser you set as default browser [in windows settings](https://www.avast.com/c-change-default-browser-windows#:~:text=Open%20the%20Start%20menu%20and,is%20the%20current%20default%20browser.), is also the browser that you've browsed fansly with in the past
2. Click on Automatic Configurator and wait for it [to do its thing](https://github.com/Avnsx/fansly/wiki/Explanation-of-provided-programs-&-their-functionality#2-automatic-configurator)
3. If it was successful(``config.ini`` should now *only* show a *single* ``ReplaceMe`` the targeted creator name) open the ``config.ini`` file and replace the value for ``[TargetedCreator]`` > ``Username =`` with whatever content creator you wish to have scraped
4. Save the ``config.ini`` file(into the same directory as fansly scraper) with the changes you've done to it, close it & then start up Fansly Scraper by clicking on it

**⚠️ If you are not using Windows or are encountering a bug with quick start please head over to [Get Started](https://github.com/Avnsx/fansly/wiki/Get-Started) instead ⚠️**

## 🤔 FAQ
Do you have any unanswered questions or want to know more about fansly scraper? Head over to the [Wiki](https://github.com/Avnsx/fansly/wiki)

+ **Q**: "Why do some executables show detections on them in VirusTotal?"
**A**: They are false positives (invalid detections). I literally e-mail each release of the scraper, for manual analysis to antivirus providers and the not 💩 providers actually analyse and unflag them, while others don't even bother reading their e-mails, but for some reason managed to get on VirusTotals file scanning system.

+ **Q**: "Could you add X feature or do X change?"
**A**: Star the project and I'll think about it. Otherwise you could always [open a pull request](https://github.com/Avnsx/fansly/pulls)

+ **Q**: "I used the automatic configurator and my browser now displays insecure on fansly.com!"
**A**: That's a rare bug, caused by automatic configurator just press on the lock icon in the left side of your url bar, while being on fansly.com > click on cookies > remove & refresh the site and you're good

+ **Q**: "Will you add any payment bypassing features to fansly scraper?"
**A**: No, as the intention of this repository is not to harm fansly

## 🤝 Contributing to `Fansly Scraper`
Any kind of positive contribution is welcome! Please help it grow by contributing to the project.

The currently most needed changes are:
+ adding linux and macOS compability to automatic configurator
+ providing windows builds for [plyvel](https://github.com/wbolster/plyvel/issues/137) to be able to integrate it into automatic configurator

Less important:
+ a way to visually display (e.g. loading bar) how much content is arleady scraped and how much is left

Please open a [open a pull request](https://github.com/Avnsx/fansly/pulls)!

## 🙏 Support
We all need support and motivation. This downloader for fansly is not an exception. Please give this project a ⭐️ to encourage and show that you liked it.

If you found the programs helpful, consider supporting me with crypto

BTC: 33s58gfMUec6HMebsccZ2w4tRTcHbRLpzp

ETH: 0x10C683fab5E946df3936DbCA788080b4aDc81233

Tether: 0x6a7b80a6a926eac349aCD0fAE9a3Bd24Af9fc4F1

Bitcoin Cash: qzs9ayfnm5e4vtzrsk8eh34upc097m8vrv80eqefrn

## 🛡️ License
This project (including executables) is licensed under the GPL-3.0 License - see the [`LICENSE`](LICENSE) file for details.

## Disclaimer
"Fansly" or fansly.com is operated by Select Media LLC as stated on their "Contact" page. This repository (Avnsx/"fansly") and the provided content in it isn't in any way affiliated with, sponsored by, or endorsed by Select Media LLC or "Fansly". The developer(referred to: "Avnsx" in the following) of this code is not responsible for the end users actions, no unlawful activities of any kind are being encouraged. Statements and processes described in this repository only represent best practice guidance aimed at fostering an effective software usage. The repository was written purely for educational purposes, in an entirely theoretical environment. Thus, any information is presented on the condition that the developer of this code shall not be held liable in no event to you or anyone else for any direct, special, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including without limitation, loss of profit, loss of use, savings or revenue, or the claims of third parties, whether the developer has advised of the possibility of such loss, however caused and on any theory of liability, arising out of or in connection with the possession, use or performance of this software. The material embodied in this repository is supplied to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty of fitness. This disclaimer is preliminary and is subject to revision.
##
Written with python 3.8.10 for Windows 10
