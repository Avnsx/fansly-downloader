# Fansly Downloader (fansly-dl)

![Downloads](https://img.shields.io/github/downloads/Avnsx/fansly/total?color=0078d7&label=🔽%20Downloads.exe&style=flat-square) ![Compatibility](https://img.shields.io/static/v1?style=flat-square&label=%F0%9F%90%8D%20Python&message=3.6%2B&color=blue) ![Stars](https://img.shields.io/github/stars/Avnsx/fansly?style=flat-square&label=⭐%20Stars&color=ffc83d)

![UI Banner](https://i.imgur.com/EhL42m3.jpg)

## 👋 Introducing ``fansly-dl``
**fansly-dl** is a fork from the original [Fansly Downloader](https://github.com/Avnsx/fansly) repo with priminarly Linux users in mind.

This project aims to be an easy to use Fansly media downloader (Videos and Photos) from your favorite (and subriscribed) fansly creators. 

After you've launched the program, it'll create a sub-folder with the ``CreatorName`` in the directory you set in the parameter ``download_dir`` of the ``config.ini`` file. That folder will have two sub-folders called ``Pictures`` and ``Videos``, which will contain the downloaded content sorted into them.

This code **does not bypass any paywalls** & **no user information is ever collected.**

[Click me if you want a detailed description on each of the components of this software!](https://github.com/Avnsx/fansly/wiki/Explanation-of-provided-programs-&-their-functionality)

### Many Thanks to all the `Avnsx` who have made this project possible! [![@Avnsx/fansly repo](https://github.com/Avnsx/fansly)]

## 🏗️ Set up

1. Clone this project repo:
	* ``$ git clone https://github.com/romfetchr/fansly-dl.git``
	* ``$ cd fansly-dl``
3. Install the necessary Python packages: 
	* ``$ sudo apt install python3-tk``
	* ``$ sudo dpkg-reconfigure python3-tk``
	* ``$ pip install --user -r requirements.txt``
4. Get your Fansly.com account details to configure fansly-dl:
	* Make sure you have registered an account on fansly and are logged in with it in your browser, or you'll not be able to get an **authorization token** from Developer Console;
	* Go to whatever creator's account page and open your browsers developer console (Most often Key: F12);
	* Reload the website by using the rotating arrow symbol to the left of your browsers search bar(Key: F5), while the developer console is open. Now do the steps on the following picture:
	![image](https://user-images.githubusercontent.com/97050167/167995208-4ca0a829-ec2e-4ff4-8f64-e49ea1114de8.png)
	* Copy the string that is on the right side of `authorization:` then **replace** the text `YourAuthToken` (inside the ``config.ini`` file) with the value you just coppied;
	* Copy the string that is on the right side of `User-Agent:` then **replace** the text `YourUsrAgent` (inside the ``config.ini`` file) with latest coppied string.

After completing the configuration, you'll only need to change the creator name from `ReplaceWithCreator` in ``config.ini`` for every further use case on other creators.

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


## 🛡️ License
This project (including executables) is licensed under the GPL-3.0 License - see the [`LICENSE`](LICENSE) file for details.

## Disclaimer
"Fansly" or fansly.com is operated by Select Media LLC as stated on their "Contact" page. This repository (romfetchr/fansly-dl) and the provided content in it isn't in any way affiliated with, sponsored by, or endorsed by Select Media LLC or "Fansly". The developer(referred to: "romfetchr" in the following) of this code is not responsible for the end users actions, no unlawful activities of any kind are being encouraged. Statements and processes described in this repository only represent best practice guidance aimed at fostering an effective software usage. The repository was written purely for educational purposes, in an entirely theoretical environment. Thus, any information is presented on the condition that the developer of this code shall not be held liable in no event to you or anyone else for any direct, special, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including without limitation, loss of profit, loss of use, savings or revenue, or the claims of third parties, whether the developer has advised of the possibility of such loss, however caused and on any theory of liability, arising out of or in connection with the possession, use or performance of this software. The material embodied in this repository is supplied to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty of fitness. This disclaimer is preliminary and is subject to revision.
##
Written with python 3.8.10 for Windows 10
