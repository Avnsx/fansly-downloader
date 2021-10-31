import requests,os,re,base64,hashlib,imagehash,io,traceback,sys
from loguru import logger as log
from functools import partialmethod
from PIL import Image
from time import sleep as s
from configparser import ConfigParser
os.system('title Fansly Scraper')
sess = requests.Session()

print(base64.b64decode('IC5kODg4ICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4UCIgICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4ODg4IDg4ODhiLiA4ODg4Yi4gIC5kODg4OGIgIDg4IDg4ICA4OCAgICAgIC5kODg4OGIgIC5kODg4OGIgLjhkODg4IDg4ODhiLiAuODg4OGIuICAuZDg4Yi4gIC44OGQ4ODgKIDg4ICAgICAgICI4OCA4OCAiODhiIDg4SyAgICAgIDg4IDg4ICA4OCAgICAgIDg4SyAgICAgIDg4UCIgICAgODhQIiAgICAgICI4OCA4OCAiODhiIGQ4UCAgWThiIDg4UCIgICAKIDg4ICAgLmQ4ODg4OCA4OCAgODg4ICJZODg4OGIuIDg4IDg4ICA4OCAgICAgICJZODg4OGIuIDg4ICAgICAgODggICAgLmQ4ODg4OCA4OCAgODg4IDg4ODg4ODg4IDg4ICAgICAKIDg4ICAgODg4ICA4OCA4OCAgODg4ICAgICAgWDg4IDg4IDg4YiA4OCAgICAgICAgICAgWDg4IDg4Yi4gICAgODggICAgODg4ICA4OCA4OCBkODhQIFk4Yi4gICAgIDg4ICAgICAKIDg4ICAgIlk4ODg4OCA4OCAgODg4ICA4ODg4OFAnIDg4IFk4ODg4OCAgICAgICA4ODg4OFAnICJZODg4OFAgODggICAgIlk4ODg4OCA4ODg4UCIgICAiWTg4ODggIDg4ICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDhiIGQ4OCAgICBodHRwczovL2dpdGh1Yi5jb20vQXZuc3gvZmFuc2x5ICA4OCAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICJZODhQIiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICA=').decode('ascii'))

def output(level,type,color,mytext):
    try:log.level(type, no=level, color=color)
    except TypeError:pass # level failsave
    log.__class__.type = partialmethod(log.__class__.log, type)
    log.remove()
    log.add(sys.stdout, format="<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>", level=type)
    log.type(mytext)

output(1,'\n Info','<light-blue>','Reading config.ini file ...')
config = ConfigParser()
config.read('config.ini')

try:
    mycreator = config['TargetedCreator']['Username']
    mytoken = config['MyAccount']['Authorization_Token']
    myuseragent = config['MyAccount']['User_Agent']
    previews = config['Options']['Download_Media_Previews'].capitalize()
    openwhenfinished = config['Options']['Open_Folder_When_Finished'].capitalize()
except (KeyError, NameError) as e:
    output(2,'\n [1]ERROR','<red>', '"'+str(e)+'" is missing or malformed in the configuration file! Read the ReadMe file for assistance.')
    s(60)
    exit()

for x in mycreator,mytoken,myuseragent,previews,openwhenfinished:
    if x == '' or x == 'ReplaceMe':
        output(2,'\n [2]ERROR','<red>', '"'+str(x)+'" is unmodified, missing or malformed in the configuration file! Read the ReadMe file for assistance.')
        s(60)
        exit()

current_ver='0.2'
try:
    newest_ver=requests.get('https://github.com/Avnsx/fansly/releases/latest', headers={'authority': 'github.com','user-agent': myuseragent,'accept-language': 'en-US,en;q=0.9',}).url.split('/v')[-1]
    if newest_ver > current_ver:output(3,' WARNING','<yellow>', 'Your version (v'+str(current_ver)+') of fansly scraper is outdated, please update! Newest version: v'+str(newest_ver))
except requests.exceptions.ConnectionError as e:
    output(2,'\n [3]ERROR','<red>', 'Update check failed, due to no internet connection! Closing in 60 seconds.')
    print('\n'+str(e))
    s(60)
    exit()
except Exception as e:
    output(2,'\n [4]ERROR','<red>', 'Update check failed, will try to continue ...')
    print('\n'+str(e))
    s(10)
    pass

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://fansly.com/',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': mytoken,
    'User-Agent': myuseragent,
}

try:
    raw_req = sess.get('https://apiv2.fansly.com/api/v1/account?usernames='+mycreator, headers=headers)
    acc_req = raw_req.json()['response'][0]
    creator_id = acc_req['avatar']['accountId']
except KeyError as e:
    if raw_req.status_code == 401:
        output(2,'\n [5]ERROR','<red>', 'API returned unauthorized. This is most likely because of a wrong authorization token, in the configuration file.')
        print(f'{21*" "}Used authorization token: "'+mytoken+'" [DO NOT SHARE]')
    else:output(2,'\n [6]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed.')
    print('\n'+str(e))
    print(raw_req.text)
    s(60)
    exit()
except IndexError as e:
    output(2,'\n [7]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed; most likely misspelled the creator name.')
    print('\n'+str(e))
    print(raw_req.text)
    s(60)
    exit()

try:following = acc_req['following']
except KeyError:following = False
try:subscribed = acc_req['subscribed']
except KeyError:subscribed = False
total_photos = acc_req['timelineStats']['imageCount']
total_videos = acc_req['timelineStats']['videoCount']

output(1,' Info','<light-blue>','Targeted creator: "'+mycreator+'"')
output(1,' Info','<light-blue>','Using authorisation token: "'+mytoken+'"')
output(1,' Info','<light-blue>','Using user-agent: "'+myuseragent[:28]+' [...] '+myuseragent[-35:]+'"')
output(1,' Info','<light-blue>','Open download folder when finished, is set to: "'+openwhenfinished+'"')
output(1,' Info','<light-blue>','Downloading files marked as preview, is set to: "'+previews+'"')

if previews == 'True':output(3,' WARNING','<yellow>', 'Previews downloading is enabled; repetitive and/or emoji spammed media might be downloaded!')

try:
    output(1,'\n Info','<light-blue>','Creating download directories ...')
    basedir=mycreator+'_fansly'
    os.makedirs(basedir, exist_ok = True)
    os.makedirs(basedir+'/Pictures', exist_ok = True)
    os.makedirs(basedir+'/Videos', exist_ok = True)
except Exception:
    print('\n'+traceback.format_exc())
    output(2,'\n [8]ERROR','<red>', 'Creating download directories ... Please copy & paste this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
    s(60)
    exit()

pic_count=1
vid_count=1
duplicates=0
photobyte_hashes=[]
videobyte_hashes=[]
def sort_download(filename,filebytes):
    global pic_count, vid_count, duplicates
    win_comp_name=re.sub(r'[\\/:*?"<>|]', '', repr(filename).replace("'",'')) # better solution?
    if re.findall(r'.jpeg|.png|.jpg|.tif|.tiff|.bmp', filename[-6:]):
        photohash=imagehash.average_hash(Image.open(io.BytesIO(filebytes)))
        if photohash not in photobyte_hashes:
            with open(basedir+'/Pictures/'+str(pic_count)+'_'+win_comp_name, 'wb') as f:f.write(filebytes)
            photobyte_hashes.append(photohash)
            pic_count+=1
        else:duplicates+=1
    elif re.findall(r'.mp4|.mkv|.mov|.gif|.wmv|.flv|.webm', filename[-6:]):
        videohash=hashlib.md5(filebytes).hexdigest() # better solution?
        if videohash not in videobyte_hashes:
            with open(basedir+'/Videos/'+str(vid_count)+'_'+win_comp_name, 'wb') as f:f.write(filebytes)
            videobyte_hashes.append(videohash)
            vid_count+=1
        else:duplicates+=1
    else:
        output(2,'\n [9]ERROR','<red>', 'Unknown filetype: "'+str(filename[-7:])+'" please report this on GitHub > Issues & provide a short explanation; continuing without that file in 60 seconds.')
        s(60)

output(1,' Info','<light-blue>','Started media download; this could take a while dependant on the content size ...')
cursor = 0
while True:
    response = sess.get('https://apiv2.fansly.com/api/v1/timeline/'+creator_id+'?before='+str(cursor)+'&after=0', headers=headers)
    try:
        for x in response.json()['response']['accountMedia']:
            # previews
            if previews == 'True':
                try:
                    if x['access'] != False:
                        sort_download(x['media']['filename'], sess.get(x['preview']['locations'][0]['location'], headers=headers).content)
                    if x['access'] == False:
                        sort_download(x['preview']['filename'], sess.get(x['preview']['locations'][0]['location'], headers=headers).content)
                except:pass
            # unlocked media
            try:
                locurl=x['media']['locations'][0]['location']
                sort_download(x['media']['filename'], sess.get(locurl, headers=headers).content)
            # unlocked media without corresponding location url
            except IndexError:
                for f in range(0,len(x['media']['variants'])):
                    try:
                        locurl=x['media']['variants'][f]['locations'][0]['location']
                        sort_download(x['media']['variants'][f]['filename'], sess.get(locurl, headers=headers).content)
                        break
                    except:pass # silently passing locked media
                pass
            except Exception:
                print('\n'+traceback.format_exc())
                output(2,'\n [10]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
                s(60)
                exit()
        # get next cursor
        try:
            cursor = response.json()['response']['posts'][-1]['id']
            output(1,' Info','<light-blue>','Downloading media from page: '+cursor)
        except IndexError:break #break if end is reached
        except Exception:
            print('\n'+traceback.format_exc())
            output(2,'\n [11]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
            s(60)
            exit()
    except KeyError:
        output(2,'\n [12]ERROR','<red>', "Couldn't find any scrapeable media at all!\n This most likely happend because you're not following the creator, your authorisation token is wrong\n or the creator is not providing unlocked content. Closing in 60 Seconds.")
        s(60)
        exit()

print('')
issue=False
if pic_count-1 <= total_photos * 0.2:
    output(3,' WARNING','<yellow>', 'Low amount of content scraped. Creators total Pictures: '+str(total_photos)+', downloaded Pictures: '+str(pic_count-1))
    issue = True

if vid_count-1 <= total_videos * 0.2:
    output(3,' WARNING','<yellow>', 'Low amount of content scraped. Creators total Videos: '+str(total_videos)+', downloaded Videos: '+str(vid_count-1))
    issue = True

if issue == True:
    if following == False:print(f'{20*" "}Follow the creator; to be able to scrape more media!')
    if subscribed == False:print(f'{20*" "}Subscribe to the creator; if you would like to get the entire content.')
    if previews == 'False':print(f'{20*" "}Try setting Media Preview Downloads on, this helps if the creator marks all his content as previews.')
    print('')

full_path=os.getcwd()+'\\'+basedir
if openwhenfinished == 'True':os.startfile(full_path)
print('╔═\n  Done! Downloaded '+str(pic_count-1)+' pictures & '+str(vid_count-1)+' videos ('+str(duplicates)+' duplicates declined)\n  Saved in directory: "'+full_path+'"\n  Please leave a Star on the GitHub Repository if you like the code!\n  Would appreciate it; if you spread the word/support with Crypto:\n  BTC: bc1q82n68gmdxwp8vld524q5s7wzk2ns54yr27flst\n  ETH: 0x645a734Db104B3EDc1FBBA3604F2A2D77AD3BDc5'+f'{20*" "}'+'═╝')

s(120)
exit()
