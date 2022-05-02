import requests,os,re,base64,hashlib,imagehash,io,traceback,sys,platform,subprocess,concurrent.futures
from string import digits
from random import choices, randint
from tkinter import Tk, filedialog
from loguru import logger as log
from functools import partialmethod
from PIL import Image
from time import sleep as s
from configparser import RawConfigParser
from datetime import datetime
os.system('title Fansly Scraper')
sess = requests.Session()

def exit():os._exit(0) # pyinstaller

print(base64.b64decode('IC5kODg4ICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4UCIgICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4ODg4IDg4ODhiLiA4ODg4Yi4gIC5kODg4OGIgIDg4IDg4ICA4OCAgICAgIC5kODg4OGIgIC5kODg4OGIgLjhkODg4IDg4ODhiLiAuODg4OGIuICAuZDg4Yi4gIC44OGQ4ODgKIDg4ICAgICAgICI4OCA4OCAiODhiIDg4SyAgICAgIDg4IDg4ICA4OCAgICAgIDg4SyAgICAgIDg4UCIgICAgODhQIiAgICAgICI4OCA4OCAiODhiIGQ4UCAgWThiIDg4UCIgICAKIDg4ICAgLmQ4ODg4OCA4OCAgODg4ICJZODg4OGIuIDg4IDg4ICA4OCAgICAgICJZODg4OGIuIDg4ICAgICAgODggICAgLmQ4ODg4OCA4OCAgODg4IDg4ODg4ODg4IDg4ICAgICAKIDg4ICAgODg4ICA4OCA4OCAgODg4ICAgICAgWDg4IDg4IDg4YiA4OCAgICAgICAgICAgWDg4IDg4Yi4gICAgODggICAgODg4ICA4OCA4OCBkODhQIFk4Yi4gICAgIDg4ICAgICAKIDg4ICAgIlk4ODg4OCA4OCAgODg4ICA4ODg4OFAnIDg4IFk4ODg4OCAgICAgICA4ODg4OFAnICJZODg4OFAgODggICAgIlk4ODg4OCA4ODg4UCIgICAiWTg4ODggIDg4ICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDhiIGQ4OCAgICBodHRwczovL2dpdGh1Yi5jb20vQXZuc3gvZmFuc2x5ICA4OCAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICJZODhQIiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICA=').decode('ascii'))

def output(level,type,color,mytext):
    try:log.level(type, no=level, color=color)
    except TypeError:pass # level failsave
    log.__class__.type = partialmethod(log.__class__.log, type)
    log.remove()
    log.add(sys.stdout, format="<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>", level=type)
    log.type(mytext)

output(1,'\n Info','<light-blue>','Reading config.ini file ...')
config = RawConfigParser()
if len(config.read('config.ini')) != 1:
    output(2,'\n [1]ERROR','<red>', 'config.ini file not found or can not be read. Please download it & make sure it is in the same directory as Fansly Scraper.exe')
    input('\nPress any key to close ...')
    exit()

try:
    mycreator = config['TargetedCreator']['Username']
    mytoken = config['MyAccount']['Authorization_Token']
    myuseragent = config['MyAccount']['User_Agent']
    show = config['Options']['Show_Downloads'].capitalize()
    remember = config['Options']['Update_Recent_Download'].capitalize()
    previews = config['Options']['Download_Media_Previews'].capitalize()
    openwhenfinished = config['Options']['Open_Folder_When_Finished'].capitalize()
    naming = config['Options']['naming_convention'].capitalize()
    seperate_messages = config['Options']['seperate_messages'].capitalize()
    seperate_previews = config['Options']['seperate_messages'].capitalize()
    curent_ver = config['Other']['version']
except (KeyError, NameError) as e:
    output(2,'\n [2]ERROR','<red>', f'"{e}" is missing or malformed in the configuration file!\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
    input('\nPress any key to close ...')
    exit()

os.system(f'title Fansly Scraper v{curent_ver}')

for x in mycreator,mytoken,myuseragent:
    if x == '' or x == 'ReplaceMe':
        output(2,'\n [3]ERROR','<red>', f'"{x}" is unmodified, missing or malformed in the configuration file!\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
        input('\nPress any key to close ...')
        exit()

for x in show,previews,openwhenfinished,seperate_messages,seperate_previews:
    if x != 'True' and x != 'False':
        output(2,'\n [4]ERROR','<red>', f'"{x}" is malformed in the configuration file! This value can only be True or False\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
        input('\nPress any key to close ...')
        exit()

if remember != 'True' and remember != 'False' and remember != 'Auto':
    output(2,'\n [4]ERROR','<red>', f'"{remember}" is malformed in the configuration file! This value can only be True, False or Auto\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
    input('\nPress any key to close ...')
    exit()

if naming != 'Standard' and naming != 'Datepost':
    output(2,'\n [4]ERROR','<red>', f'"{naming}" is malformed in the configuration file! This value can only be Standard or DatePost\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
    input('\nPress any key to close ...')
    exit()

def open_file(myfile):
    os_v=platform.system()
    try:
        if os_v == 'Windows':os.startfile(myfile)
        elif os_v == 'Linux':subprocess.Popen(['xdg-open', myfile])
        elif os_v == 'Darwin':subprocess.Popen(['open', myfile])
        else:
            if openwhenfinished == 'True':
                output(2,'\n [5]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; if this happens again turn Open_Folder_When_Finished to "False" in the file "config.ini".\n{21*" "}Will try to continue ...')
                s(5)
            else:
                output(2,'\n [6]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; this happend while trying to do an required update!\n{21*" "}Please update, by either opening "{myfile}" manually or downloading the new version from github.com/Avnsx/Fansly')
                s(30)
                exit()
    except:
        if openwhenfinished == 'True':
            output(2,'\n [7]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; if this happens again turn Open_Folder_When_Finished to "False" in the file "config.ini".\n{21*" "}Will try to continue ...')
            s(5)
        else:
            output(2,'\n [8]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; this happend while trying to do an required update!\n{21*" "}Please update, by either opening "{myfile}" manually or downloading the new version from github.com/Avnsx/Fansly')
            s(30)
            exit()


tot_downs=0
try:
    api_req=requests.get('https://api.github.com/repos/avnsx/fansly/releases', headers={'user-agent': f'Fansly Scraper {curent_ver}','referer':f'Fansly Scraper {curent_ver}', 'accept-language': 'en-US,en;q=0.9','accept-language': 'en-US,en;q=0.9',}).json()
    for x in api_req:tot_downs+=x['assets'][0]['download_count']
    if api_req[0]['tag_name'].lstrip('v') > curent_ver:
        output(3,' WARNING','<yellow>', f'Your version (v{curent_ver}) of fansly scraper is outdated; starting updater ...')
        s(3)
        open_file('updater.exe')
        s(10)
        exit()
except requests.exceptions.ConnectionError as e:
    output(2,'\n [9]ERROR','<red>', 'Update check failed, due to no internet connection!')
    print('\n'+str(e))
    input('\nPress any key to close ...')
    exit()
except Exception as e:
    output(2,'\n [10]ERROR','<red>', 'Update check failed, will try to continue ...')
    print('\n'+str(e))
    s(3)
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
    creator_id = acc_req['id']
except KeyError as e:
    if raw_req.status_code == 401:
        output(2,'\n [11]ERROR','<red>', 'API returned unauthorized. This is most likely because of a wrong authorization token, in the configuration file.')
        print(f'{21*" "}Used authorization token: "'+mytoken+'"')
    else:output(2,'\n [12]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed.')
    print('\n'+str(e))
    print(raw_req.text)
    input('\nPress any key to close ...')
    exit()
except IndexError as e:
    output(2,'\n [13]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed; most likely misspelled the creator name.')
    print('\n'+str(e))
    print(raw_req.text)
    input('\nPress any key to close ...')
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
if remember == 'True':output(3,' WARNING','<yellow>', 'Update recent download is enabled')

if randint(1,100) <= 19:
    output(4,'\n lnfo','<light-red>', f"Fansly scraper was downloaded {tot_downs} times, but only {round(requests.get('https://api.github.com/repos/avnsx/fansly', headers={'User-Agent':'Fansly Scraper'}).json()['stargazers_count']/tot_downs*100, 2)} % of You(!) have starred it\n{19*' '}Stars directly influence my willingness to continue maintaining the project\n{23*' '}Help the repository grow today, by leaving a star on it!")
    s(15)

recent_photobyte_hashes=[]
recent_videobyte_hashes=[]

basedir=mycreator+'_fansly'

def process_img(name):
    recent_photobyte_hashes.append(str(imagehash.average_hash(Image.open(basedir+'/Pictures/'+name))))

def process_vid(name):
    with open(basedir+'/Videos/'+name, 'rb') as f:
        recent_videobyte_hashes.append(hashlib.md5(f.read()).hexdigest())

print('')
if remember == 'Auto':
    output(1,' Info','<light-blue>', 'Automatically detecting whether download folder exists')
    if os.path.isdir(basedir):
        remember = 'True'
    else:
        remember = 'False'

if remember == 'True':
    if os.path.isdir(basedir):
        output(1,' Info','<light-blue>', f'"{basedir}" folder exists in local directory')
    else:
        output(3,' WARNING','<yellow>', f"'{basedir}' folder is not located in the local directory; but you launched in update recent download mode,\n{20*' '}so find & select the folder that contains recently downloaded 'Photos' & 'Videos' as subfolders (it should be called '{basedir}')")
        root = Tk()
        root.withdraw()
        basedir = filedialog.askdirectory()
        if basedir:
            output(1,' Info','<light-blue>', f'Chose folder path {basedir}')
        else:
            output(2,'\n [14]ERROR','<red>', f'Could not register your chosen folder path, please start all over again. Closing in 30 seconds')
            s(30)
            exit()

    # pictures
    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded pictures ...")
    list_of_futures=[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for el in os.listdir(basedir+'/Pictures'):
            list_of_futures.append(executor.submit(process_img, el))
        concurrent.futures.wait(list_of_futures)

    # videos
    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded videos ...")
    list_of_futures=[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for el in os.listdir(basedir+'/Videos'):
            list_of_futures.append(executor.submit(process_vid, el))
        concurrent.futures.wait(list_of_futures)

    output(1,' Info','<light-blue>', f'Finished hashing! Will now compare each new download against {len(recent_photobyte_hashes)} photo & {len(recent_videobyte_hashes)} video hashes.')
else:
    try:
        output(1,' Info','<light-blue>','Creating download directories ...')
        os.makedirs(basedir, exist_ok = True)
        
        if seperate_messages == 'True':
            os.makedirs(basedir+'/Messages', exist_ok = True)
            os.makedirs(basedir+'/Messages/Pictures', exist_ok = True)
            os.makedirs(basedir+'/Messages/Videos', exist_ok = True)
            os.makedirs(basedir+'/Timeline', exist_ok = True)
            os.makedirs(basedir+'/Timeline/Pictures', exist_ok = True)
            os.makedirs(basedir+'/Timeline/Videos', exist_ok = True)
            if previews == 'True' and seperate_previews == 'True':
                os.makedirs(basedir+'/Messages/Previews', exist_ok = True)
                os.makedirs(basedir+'/Messages/Previews/Pictures', exist_ok = True)
                os.makedirs(basedir+'/Messages/Previews/Videos', exist_ok = True)
                os.makedirs(basedir+'/Timeline/Previews', exist_ok = True)
                os.makedirs(basedir+'/Timeline/Previews/Pictures', exist_ok = True)
                os.makedirs(basedir+'/Timeline/Previews/Videos', exist_ok = True)
        else:
            os.makedirs(basedir+'/Pictures', exist_ok = True)
            os.makedirs(basedir+'/Videos', exist_ok = True)
            if seperate_previews == 'True':
                os.makedirs(basedir+'/Previews', exist_ok = True)
                os.makedirs(basedir+'/Previews/Pictures', exist_ok = True)
                os.makedirs(basedir+'/Previews/Videos', exist_ok = True)
    except Exception:
        print('\n'+traceback.format_exc())
        output(2,'\n [15]ERROR','<red>', 'Creating download directories ... Please copy & paste this on GitHub > Issues & provide a short explanation.')
        input('\nPress any key to close ...')
        exit()

pic_count=1
vid_count=1
duplicates=0
recent=0
photobyte_hashes=[]
videobyte_hashes=[]
def sort_download(filename,filebytes, directoryName):
    global pic_count, vid_count, duplicates, recent
    win_comp_name=str(re.sub(r'[\\/:*?"<>|]', '', repr(filename).replace("'",''))).replace('..','.')
    randints=''.join(choices(digits, k=3))
    if re.findall(r'.jpeg|.png|.jpg|.tif|.tiff|.bmp', filename[-6:]):
        photohash=str(imagehash.average_hash(Image.open(io.BytesIO(filebytes))))
        if photohash not in recent_photobyte_hashes:
            if photohash not in photobyte_hashes:
                if naming == 'Datepost':
                    prefix = ""
                else:
                    prefix = f"{pic_count}-{randints}_"
                if show == 'True':output(1,' Info','<light-blue>', f"Downloading Image '{win_comp_name}'")
                with open(f"{ directoryName }/Pictures/{prefix}{win_comp_name}", 'wb') as f:f.write(filebytes)
                photobyte_hashes.append(photohash)
                pic_count+=1
            else:duplicates+=1
        else:recent+=1
    elif re.findall(r'.mp4|.mkv|.mov|.gif|.wmv|.flv|.webm', filename[-6:]):
        videohash=hashlib.md5(filebytes).hexdigest()
        if videohash not in recent_videobyte_hashes:
            if videohash not in videobyte_hashes:
                if naming == 'Datepost':
                    prefix = ""
                else:
                    prefix = f"{vid_count}-{randints}_"
                if show == 'True':output(1,' Info','<light-blue>', f"Downloading Video '{win_comp_name}'")
                with open(f"{ directoryName }/Videos/{prefix}{win_comp_name}", 'wb') as f:f.write(filebytes)
                videobyte_hashes.append(videohash)
                vid_count+=1
            else:duplicates+=1
        else:recent+=1
    else:
        output(2,'\n [16]ERROR','<red>', 'Unknown filetype: "'+str(filename[-7:])+'" please report this on GitHub > Issues & provide a short explanation; continuing without that file ...')

# scrape messages
group_id = None
groups = sess.get('https://apiv2.fansly.com/api/v1/group', headers=headers).json()['response']['groups']
for x in range(len(groups)):
    if groups[x]['users'][0]['userId'] == creator_id:
        group_id = groups[x]['id']
        break

if group_id:
    output(1,' Info','<light-blue>','Started messages media download ...')
    msg_cursor = None
    while True:
        if seperate_messages == 'True':
            directory_name = f'{ basedir }/messages'
        else:
            directory_name = f'{basedir}'
        if seperate_previews == 'True':
            preview_directory_name = f'{ directory_name }/previews'
        else:
            preview_directory_name = directory_name
        if not msg_cursor:
            output(1,' Info','<light-blue>', f'Inspecting message: {group_id}')
            resp = sess.get('https://apiv2.fansly.com/api/v1/message', headers=headers, params=(('groupId', group_id),('limit', '50'),)).json()
        else:
            output(1,' Info','<light-blue>', f'Inspecting message: {msg_cursor}')
            resp = sess.get('https://apiv2.fansly.com/api/v1/message', headers=headers, params=(('groupId', group_id),('before', msg_cursor),('limit', '50'),)).json()
        try:
            for x in resp['response']['accountMedia']:
                # set filename
                if naming == 'Datepost':
                    ts = int(x['createdAt'])
                    file_datetime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
                    file_id = x['id']
                    file_name = f"{ file_datetime } { file_id }"
                else:
                    file_name = f"{mycreator}"
                # message media previews
                if previews == 'True':
                    try:
                        if x['access'] != False:
                            sort_download(f"{file_name} preview.{x['media']['mimetype'].split('/')[1]}", sess.get(x['preview']['locations'][0]['location'], headers=headers).content, preview_directory_name)
                        if x['access'] == False:
                            sort_download(f"{file_name} preview.png", sess.get(x['preview']['locations'][0]['location'], headers=headers).content, preview_directory_name)
                    except:pass
                # unlocked meda in messages
                try:
                    locurl=x['media']['locations'][0]['location']
                    sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, headers=headers).content, directory_name)
                # unlocked messages without corresponding location url
                except IndexError:
                    for f in range(0,len(x['media']['variants'])):
                        try:
                            locurl=x['media']['variants'][f]['locations'][0]['location']
                            sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, headers=headers).content, directory_name)
                            break
                        except:pass # silently passing locked media in messages
                    pass
                except:pass
            # get next cursor
            try:
                msg_cursor = resp['response']['messages'][-1]['id']
            except IndexError:break # break if end is reached
            except Exception:
                print('\n'+traceback.format_exc())
                output(2,'\n [17]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation.')
                input('\nPress any key to close ...')
                exit()
        except KeyError:
            output(3,' WARNING','<yellow>', 'No scrapeable media found in mesages')
            pass
else:output(1,' Info','<light-blue>','No scrapeable media found in mesages')

output(1,' Info','<light-blue>','Started profile media download; this could take a while dependant on the content size ...')
cursor = 0
while True:
    if seperate_messages == 'True':
        directory_name = f'{ basedir }/timeline'
    else:
        directory_name = f'{basedir}'
    if seperate_previews == 'True':
        preview_directory_name = f'{ directory_name }/previews'
    else:
        preview_directory_name = directory_name
    if cursor == 0:output(1,' Info','<light-blue>', f'Inspecting most recent page')
    else:output(1,' Info','<light-blue>', f'Inspecting page: {cursor}')
    response = sess.get('https://apiv2.fansly.com/api/v1/timeline/'+creator_id+'?before='+str(cursor)+'&after=0', headers=headers)
    try:
        for x in response.json()['response']['accountMedia']:
            # set filename
            if naming == 'Datepost':
                ts = int(x['createdAt'])
                file_datetime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
                file_id = x['id']
                file_name = f"{ file_datetime } { file_id }"
            else:
                file_name = f"{mycreator}"
            # previews
            if previews == 'True':
                try:
                    if x['access'] != False:
                        sort_download(f"{file_name} preview.{x['media']['mimetype'].split('/')[1]}", sess.get(x['preview']['locations'][0]['location'], headers=headers).content, preview_directory_name)
                    if x['access'] == False:
                        sort_download(f"{file_name} preview.png", sess.get(x['preview']['locations'][0]['location'], headers=headers).content, preview_directory_name)
                except:pass
            # unlocked media
            try:
                locurl=x['media']['locations'][0]['location']
                sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, headers=headers).content, directory_name)
            # unlocked media without corresponding location url
            except IndexError:
                for f in range(0,len(x['media']['variants'])):
                    try:
                        locurl=x['media']['variants'][f]['locations'][0]['location']
                        sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, headers=headers).content, directory_name)
                        break
                    except:pass # silently passing locked media
                pass
            except:pass
        # get next cursor
        try:
            cursor = response.json()['response']['posts'][-1]['id']
        except IndexError:break # break if end is reached
        except Exception:
            print('\n'+traceback.format_exc())
            output(2,'\n [18]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation.')
            input('\nPress any key to close ...')
            exit()
    except KeyError:
        output(2,'\n [19]ERROR','<red>', "Couldn't find any scrapeable media at all!\n This most likely happend because you're not following the creator, your authorisation token is wrong\n or the creator is not providing unlocked content.")
        input('\nPress any key to close ...')
        exit()
    if remember == 'True' and recent > int(total_photos+total_videos) * 0.2:
        print(f"\n╔═\n  Finished download; it looks like we've had already or have just downloaded all possible new content.\n\t\t  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶{10*' '}═╝")
        s(120)
        exit()

print('')
issue=False
if pic_count-1 <= total_photos * 0.2 and remember == 'False':
    output(3,' WARNING','<yellow>', 'Low amount of content scraped. Creators total Pictures: '+str(total_photos)+', downloaded Pictures: '+str(pic_count-1))
    issue = True

if vid_count-1 <= total_videos * 0.2 and remember == 'False':
    output(3,' WARNING','<yellow>', 'Low amount of content scraped. Creators total Videos: '+str(total_videos)+', downloaded Videos: '+str(vid_count-1))
    issue = True

if issue == True:
    if following == False:print(f'{20*" "}Follow the creator; to be able to scrape more media!')
    if subscribed == False:print(f'{20*" "}Subscribe to the creator; if you would like to get the entire content.')
    if previews == 'False':print(f'{20*" "}Try setting Media Preview Downloads on, this helps if the creator marks all his content as previews.')
    print('')

full_path=os.getcwd()+'\\'+basedir
if openwhenfinished == 'True':open_file(full_path)

print('╔═\n  Done! Downloaded '+str(pic_count-1)+' pictures & '+str(vid_count-1)+' videos ('+str(duplicates)+' duplicates declined)\n  Saved in directory: "'+full_path+'"\n  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶'+f'{12*" "}'+'═╝')

input()
