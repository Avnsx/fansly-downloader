## 👋 Introducing `Fansly Downloader`: The Ultimate Fansly Content Downloading App
![Downloads](https://img.shields.io/github/downloads/Avnsx/fansly-downloader/total?color=0078d7&label=🔽%20Downloads.exe&style=flat-square) ![Compatibility](https://img.shields.io/static/v1?style=flat-square&label=%F0%9F%90%8D%20Python&message=3.6%2B&color=blue) ![Stars](https://img.shields.io/github/stars/Avnsx/fansly-downloader?style=flat-square&label=⭐%20Stars&color=ffc83d)

![UI Banner](https://i.imgur.com/EhL42m3.jpg)

Fansly Downloader is the go-to app for all your bulk media downloading needs. Download photos, videos or any other media from Fansly, this powerful tool has got you covered! Say goodbye to the hassle of individually downloading each piece of media – now you can download them all or just some, with just a few clicks.

## ✨ Features

<table>
  <tr>
    <td align="middle" colspan="3">
      Whether functionality you're looking for, Fansly Downloader has it all:
    </td>
  </tr>
  <tr>
    <td align="middle"></td>
    <td align="middle"></td>
    <td align="middle"></td>
  </tr>
  <tr>
    <td align="middle">
      <strong>📥 Download Modes</strong>
      <hr>
      <ul align="left">
        <li>Bulk: Timeline, Messages, Collection</li>
        <li>or specific Single Posts by post ID</li>
      </ul>
    </td>
    <td align="middle">
      <strong>♻️ Updates</strong>
      <hr>
      <ul align="left">
        <li>Easily update prior download folders</li>
        <li>App keeps itself up-to-date with fansly</li>
      </ul>
    </td>
    <td align="middle">
      <strong>🖥️ Cross-Platform Compatibility</strong>
      <hr>
      <ul align="left">
        <li>Compatible with Windows, Linux & MacOS</li>
        <li>Executable app only ships for Windows</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td align="middle">
      <strong>⚙️ Customizability</strong>
      <hr>
      <ul align="left">
        <li>Separate media into sub-folders?</li>
        <li>Want to download previews?</li>
      </ul>
    </td>
    <td align="middle">
      <strong>🔎 Deduplication</strong>
      <hr>
      <ul align="left">
        <li>Downloads only unique content</li>
        <li>resulting in less bandwidth usage</li>
      </ul>
    </td>
    <td align="middle">
      <strong>💸 Free of Charge</strong>
      <hr>
      <ul align="left">
        <li>Open source, community driven project</li>
        <li>Development based on popularity</li>
      </ul>
    </td>
  </tr>
</table>


<img src="https://i.imgur.com/fj0sjQy.png" alt="Computer Mouse Icon" width="23" height="23">[Configuration Settings in detail](https://github.com/Avnsx/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#4-configini)

[Detailed description on each of the components of this software](https://github.com/Avnsx/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality)<img src="https://i.imgur.com/iIsCcGU.png" alt="Computer Mouse Icon" width="20" height="20">

## Many Thanks to all the `Stargazers` who have supported this project with stars(⭐)

[![Stargazers repo roster for @Avnsx/fansly-downloader](https://reporoster.com/stars/Avnsx/fansly-downloader)](https://github.com/Avnsx/fansly-downloader/stargazers)

## 🏗️ Set up
On windows you can just install the [Executable version](https://github.com/Avnsx/fansly-downloader/releases/latest), skip the entire set up section & go to [Quick Start](https://github.com/Avnsx/fansly-downloader#-quick-start)

#### Requirements
If you intend to use the Python source directly, please ensure that [Python is installed](https://www.python.org/downloads/) on your system. Once Python is installed, you can proceed by installing the following requirements using [Python's package manager](https://realpython.com/what-is-pip/) within your systems terminal type:

	pip install requests loguru imagehash pillow python-dateutil psutil keyboard av m3u8 pycryptodome "undetected_chromedriver==3.4.6" "pywin32; platform_system == 'Windows'"
Alternatively you can use [``requirements.txt``](https://github.com/Avnsx/fansly-downloader/blob/main/requirements.txt) through opening your system's terminal (e.g.: cmd.exe) and navigating to the project's download folder & executing the following command: ``pip install --user -r requirements.txt``

If you are on windows and can't install the windows only library called ``pywin32`` with pip, you can also install it [through pywin32's github](https://github.com/mhammond/pywin32/releases). Not being able to install pywin32, means that you won't be able to run automatic configurator and need to use [Get Started](https://github.com/Avnsx/fansly-downloader/wiki/Get-Started) instead to set Fansly Downloader up.

## 🚀 Quick Start
**Quick start is only compatible with Windows & you have to have recently logged into fansly in any of the following browsers: Chrome, FireFox, Opera, Brave or Microsoft Edge and that browser has to be [set as your default browser in windows settings](https://www.avast.com/c-change-default-browser-windows#:~:text=Open%20the%20Start%20menu%20and,is%20the%20current%20default%20browser).**

1. Make sure the browser you set as default browser [in windows settings](https://www.avast.com/c-change-default-browser-windows#:~:text=Open%20the%20Start%20menu%20and,is%20the%20current%20default%20browser), is also the browser that you've browsed fansly with in the past
2. Click on Automatic Configurator and wait for it [to do its thing](https://github.com/Avnsx/fansly-downloader/wiki/Explanation-of-provided-programs-&-their-functionality#2-automatic-configurator)
3. If it was successful(``config.ini`` should now *only* show a *single* ``ReplaceMe`` the targeted creator name) open the ``config.ini`` file and replace the value for ``[TargetedCreator]`` > ``Username =`` with whatever content creator you wish to have scraped
4. Save the ``config.ini`` file(into the same directory as Fansly Downloader) with the changes you've done to it, close it & then start up Fansly Downloader by clicking on it

**⚠️ If you are not using Windows or are encountering a bug with quick start please head over to [Get Started](https://github.com/Avnsx/fansly-downloader/wiki/Get-Started) instead ⚠️**

After completing any of the configuration tutorials [Quick Start](https://github.com/Avnsx/fansly-downloader#-quick-start) / [Get Started](https://github.com/Avnsx/fansly-downloader/wiki/Get-Started); in the future you'll only need to change the creator name for Targeted Creator > Username in ``config.ini`` for every further use case on other creators.

## 🤔 FAQ
Do you have any unanswered questions or want to know more about Fansly Downloader? Head over to the [Wiki](https://github.com/Avnsx/fansly-downloader/wiki) or check if your topic was mentioned in [Discussions](https://github.com/Avnsx/fansly-downloader/discussions) or [Issues](https://github.com/Avnsx/fansly-downloader/issues)

+ **Q**: "Why do some executables show detections on them in VirusTotal?"
**A**: They are false positives (invalid detections). I literally e-mail each release of the scraper, for manual analysis to antivirus providers and the not 💩 providers actually analyse and unflag them, while others don't even bother reading their e-mails, but for some reason managed to get on VirusTotals file scanning system.

+ **Q**: "Could you add X feature or do X change?"
**A**: Star the project and I'll think about it. Otherwise you could always [open a pull request](https://github.com/Avnsx/fansly-downloader/pulls)

+ **Q**: "Will you add any payment bypassing features to Fansly Downloader?"
**A**: No, as the intention of this repository is not to harm fansly

## 🤝 Contributing to `Fansly Downloader`
Any kind of positive contribution is welcome! Please help it grow by contributing to the project.

The currently most needed changes are:
+ adding plyvel, linux & macOS compatibility to automatic configurator
+ a way to visually display (e.g. loading bar) how much content is already scraped and how much is left

Please open a [open a pull request](https://github.com/Avnsx/fansly-downloader/pulls)!

## 🙏 Support
+ As this is not a commercialised product, please give this project a star(⭐️) to encourage further development

+ Maximise your support for Fansly Downloader by recommending it to others online 🌍

## 🛡️ License
This project (including executables) is licensed under the GPL-3.0 License - see the [`LICENSE`](LICENSE) file for details.

## Disclaimer
"Fansly" or [fansly.com](https://fansly.com/) is operated by Select Media LLC as stated on their "Contact" page. This repository and the provided content in it isn't in any way affiliated with, sponsored by, or endorsed by Select Media LLC or "Fansly". The developer(referred to: "Avnsx" in the following) of this code is not responsible for the end users actions, no unlawful activities of any kind are being encouraged. Statements and processes described in this repository only represent best practice guidance aimed at fostering an effective software usage. The repository was written purely for educational purposes, in an entirely theoretical environment. Thus, any information is presented on the condition that the developer of this code shall not be held liable in no event to you or anyone else for any direct, special, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including without limitation, loss of profit, loss of use, savings or revenue, or the claims of third parties, whether the developer has advised of the possibility of such loss, however caused and on any theory of liability, arising out of or in connection with the possession, use or performance of this software. The material embodied in this repository is supplied to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty of fitness. Finally it is important to note that this GitHub repository is the sole branch maintained and owned by the developer and any third-party websites or entities are in no way affiliated with Fansly Downloader, either directly or indirectly. This disclaimer is preliminary and is subject to revision.
##
Written with python on Windows 11
