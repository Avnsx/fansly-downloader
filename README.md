# Fansly Scraper
![GitHub Banner](https://i.imgur.com/CT4B17a.png)
## Description
On click code, to scrape your favorite fansly creators media content. After you've ran the code, it'll create a folder named ``CreatorName_fansly`` in the same directory you launched the code from. That folder will have two sub-folders called Pictures & Videos, which will contain the downloaded content sorted into them.
This is pretty usefull for example; if you dislike the website theming, but would like to view the media on your local machine instead.

## How To
1. If you don't want to use the executeable version [Soon], download the GitHub repo
2. Go to whatever creators account page and open your browsers developer console (Most often Key: F12)
3. Reload the website by using the rotating arrow symbol to the left of your browsers search bar, while the developer console is open. Do the steps on the picture:
4. ![GitHub Banner](https://i.imgur.com/X2L9XFo.png)
5. Now paste both of the strings - that were on the right side of ``authorization:`` & ``User-Agent:`` - which you just copied, as shown in the picture above. Into the configuration file (config.ini) and replace the two strings with their coressponding values. (1. ``[MyAccount]`` > ``Authorization_Token=`` paste the value for ``authorization:``; 2. ``[MyAccount]`` > ``User_Agent=`` paste the value for ``User-Agent:``.
6. Replace the value for ``[TargetedCreator]`` > ``Username=`` with whatever content creator you wish.
7. Save the file & then start up ``fansly_scraper.py``

## Installation
You can just install the executable file from the releases section on the right side on the github section. [Soon]
Else you'll need to install python and the dependencies below through python.

## Dependencies
If you are using the raw source, paste below in cmd:

	pip install requests

Dependant on how many people show me that they're liking the code by giving ⭐'s on this repo, I'll expand functionality & push more quality of life updates.

## Disclaimer
Of course I've never even used this code myself ever before and haven't experienced its intended functionality on my local machine. This was written purely for educational purposes. "Fansly" or fansly.com is operated by Select Media LLC as stated on their "Contact" page. This code (Avnsx/fansly) isn't in any way affiliated with, sponsored by, or endorsed by Select Media LLC or "Fansly".
