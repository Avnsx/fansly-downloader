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
    # I'm aware that I could've used config.getint(), getfloat, getboolean etc.
    mycreator = config['TargetedCreator']['Username']
    mytoken = config['MyAccount']['Authorization_Token']
    myuseragent = config['MyAccount']['User_Agent']
    show = config['Options']['Show_Downloads'].capitalize()
    remember = config['Options']['Update_Recent_Download'].capitalize()
    previews = config['Options']['Download_Media_Previews'].capitalize()
    openwhenfinished = config['Options']['Open_Folder_When_Finished'].capitalize()
    naming = config['Options']['naming_convention'].capitalize()
    seperate_messages = config['Options']['seperate_messages'].capitalize()
    seperate_previews = config['Options']['seperate_previews'].capitalize()
    base_directory = config['Options']['download_directory']
    curent_ver = config['Other']['version']
except (KeyError, NameError) as e:
    output(2,'\n [2]ERROR','<red>', f'"{e}" is missing or malformed in the configuration file!\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
    input('\nPress any key to close ...')
    exit()

os.system(f'title Fansly Scraper v{curent_ver}')

# config.ini backwards compability fix (≤ v0.3.5) -> val name changed
if naming == 'Datepost':
    config.set('Options', 'naming_convention', 'Date_posted') # set corrected value inside the config
    with open('config.ini', 'w', encoding='utf-8') as f:config.write(f) # save it permanently into config.ini

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
    output(2,'\n [5]ERROR','<red>', f'"{remember}" is malformed in the configuration file! This value can only be True, False or Auto\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
    input('\nPress any key to close ...')
    exit()

if naming != 'Standard' and naming != 'Date_posted':
    output(2,'\n [6]ERROR','<red>', f'"{naming}" is malformed in the configuration file! This value can only be Standard or Date_posted\n{21*" "}Read the Wiki > Explanation of provided programs & their functionality > config.ini')
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
                output(2,'\n [7]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; if this happens again turn Open_Folder_When_Finished to "False" in the file "config.ini".\n{21*" "}Will try to continue ...')
                s(5)
            else:
                output(2,'\n [8]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; this happend while trying to do an required update!\n{21*" "}Please update, by either opening "{myfile}" manually or downloading the new version from github.com/Avnsx/Fansly')
                s(30)
                exit()
    except:
        if openwhenfinished == 'True':
            output(2,'\n [9]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; if this happens again turn Open_Folder_When_Finished to "False" in the file "config.ini".\n{21*" "}Will try to continue ...')
            s(5)
        else:
            output(2,'\n [10]ERROR','<red>', f'Fansly scraper could not open "{myfile}"; this happend while trying to do an required update!\n{21*" "}Please update, by either opening "{myfile}" manually or downloading the new version from github.com/Avnsx/Fansly')
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
    output(2,'\n [11]ERROR','<red>', 'Update check failed, due to no internet connection!')
    print('\n'+str(e))
    input('\nPress any key to close ...')
    exit()
except Exception as e:
    output(2,'\n [12]ERROR','<red>', 'Update check failed, will try to continue ...')
    print('\n'+str(e))
    s(3)
    pass

F, c ='fNs', mytoken
if c[-3:]==F:
    c=c.rstrip(F)
    A,B,C=['']*len(c),7,0
    for D in range(B):
        for E in range(D,len(A),B):A[E]=c[C];C+=1
    mytoken = ''.join(A)

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://fansly.com/',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': mytoken,
    'User-Agent': myuseragent,
}

try:
    raw_req = sess.get('https://apiv3.fansly.com/api/v1/account?usernames='+mycreator, headers=headers)
    acc_req = raw_req.json()['response'][0]
    creator_id = acc_req['id']
except KeyError as e:
    if raw_req.status_code == 401:
        output(2,'\n [13]ERROR','<red>', 'API returned unauthorized. This is most likely because of a wrong authorization token, in the configuration file.')
        print(f'{21*" "}Used authorization token: "'+mytoken+'"')
    else:output(2,'\n [14]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed.')
    print('\n'+str(e))
    print(raw_req.text)
    input('\nPress any key to close ...')
    exit()
except IndexError as e:
    output(2,'\n [15]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed; most likely misspelled the creator name.')
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

output(1,' Info','<light-blue>', f'Targeted creator: "{mycreator}"')
output(1,' Info','<light-blue>', f'Using user-agent: "{myuseragent[:28]} [...] {myuseragent[-35:]}"')
output(1,' Info','<light-blue>', f'Open download folder when finished, is set to: "{openwhenfinished}"')
output(1,' Info','<light-blue>', f'Downloading files marked as preview, is set to: "{previews}"')

if previews == 'True':output(3,' WARNING','<yellow>', 'Previews downloading is enabled; repetitive and/or emoji spammed media might be downloaded!')
if remember == 'True':output(3,' WARNING','<yellow>', 'Update recent download is enabled')

if randint(1,100) <= 19:
    output(4,'\n lnfo','<light-red>', f"Fansly scraper was downloaded {tot_downs} times, but only {round(requests.get('https://api.github.com/repos/avnsx/fansly', headers={'User-Agent':'Fansly Scraper'}).json()['stargazers_count']/tot_downs*100, 2)} % of You(!) have starred it.\n{17*' '}Stars directly influence my willingness to continue maintaining the project.\n{17*' '}Help the repository grow today, by leaving a star on it and sharing it to others online!")
    s(15)

recent_photobyte_hashes, recent_videobyte_hashes = [], []

def ask_correct_dir():
    global BASE_DIR_NAME
    root = Tk()
    root.withdraw()
    BASE_DIR_NAME = filedialog.askdirectory()
    if BASE_DIR_NAME:
        output(1,'\n Info','<light-blue>', f'Chose folder file path {BASE_DIR_NAME}')
        return BASE_DIR_NAME
    else:
        output(2,'\n ERROR','<red>', f'Could not register your chosen folder file path. Please close and start all over again!')
        s(15)
        exit() # this has to force exit

if base_directory == 'Local_directory': # if user didn't specify custom downloads path
    BASE_DIR_NAME = mycreator+'_fansly' # use local directory
elif os.path.isdir(base_directory): # if user specified a correct custom downloads path
    BASE_DIR_NAME = os.path.join(base_directory, mycreator+'_fansly') # use their custom path & specify new folder for the current creator in it
    output(1,' Info','<light-blue>', f'Acknowledging custom basis download directory: "{base_directory}"')
else: # if their set directory, can't be found by the OS
    output(3,'\n WARNING','<yellow>', f"The custom basis download directory file path '{base_directory}'; seems to be invalid!\n{20*' '}Please change it, to a correct file path for example: 'C:\\MyFanslyDownloads'\n{20*' '}You could also just change it back to the default argument: 'Local_directory'\n\n{20*' '}A explorer window to help you set the correct path, will open soon!\n\n{20*' '}Preferably right click inside the explorer, to create a new folder\n{20*' '}Select it and the folder will be used as the default download directory")
    s(10) # give user time to realise instructions were given
    base_directory = ask_correct_dir() # ask user to select correct path using tkinters explorer dialog
    config.set('Options', 'download_directory', base_directory) # set corrected path inside the config
    with open('config.ini', 'w', encoding='utf-8') as f:config.write(f) # save the config permanently into config.ini
    BASE_DIR_NAME = os.path.join(base_directory, mycreator+'_fansly') # use their custom path & specify new folder for the current creator in it


MESSAGES_DIR_NAME = 'Messages'
TIMELINE_DIR_NAME = 'Timeline'
PREVIEWS_DIR_NAME = 'Previews'
PICTURES_DIR_NAME = 'Pictures'
VIDEOS_DIR_NAME = 'Videos'

def process_img(filePath):
    recent_photobyte_hashes.append(str(imagehash.average_hash(Image.open(filePath))))

def process_vid(filePath):
    h = hashlib.md5()
    with open(filePath, 'rb') as f:
        while (part := f.read(1_048_576)):
            h.update(part)
    recent_videobyte_hashes.append(h.hexdigest())

print('') # intentional empty print
if remember == 'Auto':
    output(1,' Info','<light-blue>', 'Automatically detecting whether download folder exists')
    if os.path.isdir(BASE_DIR_NAME):
        remember = 'True'
    else:
        remember = 'False'

if remember == 'True':
    if os.path.isdir(BASE_DIR_NAME):
        output(1,' Info','<light-blue>', f'"{BASE_DIR_NAME}" folder already exists in specified directory')
    else:
        output(3,' WARNING','<yellow>', f"'{BASE_DIR_NAME}' folder is not located in the specified directory; but you launched in update recent download mode,\n{20*' '}so find & select the folder that contains recently downloaded 'Messages' & 'Timeline' as subfolders (it should be called '{BASE_DIR_NAME}')")
        ask_correct_dir()

    list_of_futures=[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for x in '', TIMELINE_DIR_NAME, MESSAGES_DIR_NAME, PREVIEWS_DIR_NAME, os.path.join(TIMELINE_DIR_NAME, PREVIEWS_DIR_NAME), os.path.join(MESSAGES_DIR_NAME, PREVIEWS_DIR_NAME):
            x_path = os.path.join(BASE_DIR_NAME, x)
            if os.path.isdir(x_path):
                p_path = os.path.join(x_path, PICTURES_DIR_NAME)
                v_path = os.path.join(x_path, VIDEOS_DIR_NAME)
                if os.path.isdir(p_path):
                    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded pictures from {p_path} ...")
                    for el in os.listdir(p_path):
                        list_of_futures.append(executor.submit(process_img, f'{p_path}/{el}'))
                        
                if os.path.isdir(v_path):
                    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded videos from {v_path} ...")
                    for el in os.listdir(v_path):
                        list_of_futures.append(executor.submit(process_vid, f'{v_path}/{el}'))

    concurrent.futures.wait(list_of_futures)

    output(1,' Info','<light-blue>', f'Finished hashing! Will now compare each new download against {len(recent_photobyte_hashes)} photo & {len(recent_videobyte_hashes)} video hashes.')
else:
    try:
        output(1,' Info','<light-blue>','Creating download directories ...')
        os.makedirs(BASE_DIR_NAME, exist_ok = True)
        
        if seperate_messages == 'True':
            messages_dir = os.path.join(BASE_DIR_NAME, MESSAGES_DIR_NAME)
            os.makedirs(messages_dir, exist_ok = True)
            os.makedirs(os.path.join(messages_dir, PICTURES_DIR_NAME), exist_ok = True)
            os.makedirs(os.path.join(messages_dir, VIDEOS_DIR_NAME), exist_ok = True)
            timeline_dir = os.path.join(BASE_DIR_NAME, TIMELINE_DIR_NAME)
            os.makedirs(timeline_dir, exist_ok = True)
            os.makedirs(os.path.join(timeline_dir, PICTURES_DIR_NAME), exist_ok = True)
            os.makedirs(os.path.join(timeline_dir, VIDEOS_DIR_NAME), exist_ok = True)
            if previews == 'True' and seperate_previews == 'True':
                messages_preview_dir = os.path.join(messages_dir, PREVIEWS_DIR_NAME)
                os.makedirs(messages_preview_dir, exist_ok = True)
                os.makedirs(os.path.join(messages_preview_dir, PICTURES_DIR_NAME), exist_ok = True)
                os.makedirs(os.path.join(messages_preview_dir, VIDEOS_DIR_NAME), exist_ok = True)
                timeline_preview_dir = os.path.join(timeline_dir, PREVIEWS_DIR_NAME)
                os.makedirs(timeline_preview_dir, exist_ok = True)
                os.makedirs(os.path.join(timeline_preview_dir, PICTURES_DIR_NAME), exist_ok = True)
                os.makedirs(os.path.join(timeline_preview_dir, VIDEOS_DIR_NAME), exist_ok = True)
        else:
            os.makedirs(os.path.join(BASE_DIR_NAME, PICTURES_DIR_NAME), exist_ok = True)
            os.makedirs(os.path.join(BASE_DIR_NAME, VIDEOS_DIR_NAME), exist_ok = True)
            if seperate_previews == 'True':
                preview_dir = os.path.join(BASE_DIR_NAME, PREVIEWS_DIR_NAME)
                os.makedirs(preview_dir, exist_ok = True)
                os.makedirs(os.path.join(preview_dir, PICTURES_DIR_NAME), exist_ok = True)
                os.makedirs(os.path.join(preview_dir, VIDEOS_DIR_NAME), exist_ok = True)
    except Exception:
        print('\n'+traceback.format_exc())
        output(2,'\n [16]ERROR','<red>', 'Creating download directories ... Please copy & paste this on GitHub > Issues & provide a short explanation.')
        input('\nPress any key to close ...')
        exit()

pic_count, vid_count, duplicates, recent, photobyte_hashes, videobyte_hashes = 1, 1, 0, 0, [], []
def sort_download(filename,filebytes, directoryName):
    global pic_count, vid_count, duplicates, recent
    win_comp_name=str(re.sub(r'[\\/:*?"<>|]', '', repr(filename).replace("'",''))).replace('..','.')
    randints=''.join(choices(digits, k=3))
    if re.findall(r'.jpeg|.png|.jpg|.tif|.tiff|.bmp', filename[-6:]):
        photohash=str(imagehash.average_hash(Image.open(io.BytesIO(filebytes))))
        if photohash not in recent_photobyte_hashes:
            if photohash not in photobyte_hashes:
                if naming == 'Date_posted':
                    prefix = ""
                else:
                    prefix = f"{pic_count}-{randints}_"
                if show == 'True':output(1,' Info','<light-blue>', f"Downloading Image '{win_comp_name}'")
                with open(f"{directoryName}/Pictures/{prefix}{win_comp_name}", 'wb') as f:f.write(filebytes)
                photobyte_hashes.append(photohash)
                pic_count+=1
            else:duplicates+=1
        else:recent+=1
    elif re.findall(r'.mp4|.mkv|.mov|.gif|.wmv|.flv|.webm', filename[-6:]):
        videohash=hashlib.md5(filebytes).hexdigest()
        if videohash not in recent_videobyte_hashes:
            if videohash not in videobyte_hashes:
                if naming == 'Date_posted':
                    prefix = ""
                else:
                    prefix = f"{vid_count}-{randints}_"
                if show == 'True':output(1,' Info','<light-blue>', f"Downloading Video '{win_comp_name}'")
                with open(f"{directoryName}/Videos/{prefix}{win_comp_name}", 'wb') as f:f.write(filebytes)
                videobyte_hashes.append(videohash)
                vid_count+=1
            else:duplicates+=1
        else:recent+=1
    else:
        output(2,'\n [17]ERROR','<red>', 'Unknown filetype: "'+str(filename[-7:])+'" please report this on GitHub > Issues & provide a short explanation; continuing without that file ...')


# scrape messages
group_id = None
groups = sess.get('https://apiv3.fansly.com/api/v1/group', headers=headers).json()['response']['groups']
for x in range(len(groups)):
    users = groups[x]['users']
    for y in range(len(users)):
        if users[y]['userId'] == creator_id:
            group_id = groups[x]['id']
            break
    if group_id:
        break

if group_id:
    output(1,' Info','<light-blue>','Started messages media download ...')
    msg_cursor = None
    while True:
        if seperate_messages == 'True':
            directory_name = os.path.join(BASE_DIR_NAME, MESSAGES_DIR_NAME)
        else:
            directory_name = BASE_DIR_NAME
        if seperate_previews == 'True':
            preview_directory_name = os.path.join(directory_name, PREVIEWS_DIR_NAME)
        else:
            preview_directory_name = directory_name
        if not msg_cursor:
            output(1,' Info','<light-blue>', f'Inspecting message: {group_id}')
            resp = sess.get('https://apiv3.fansly.com/api/v1/message', headers=headers, params=(('groupId', group_id),('limit', '50'),)).json()
        else:
            output(1,' Info','<light-blue>', f'Inspecting message: {msg_cursor}')
            resp = sess.get('https://apiv3.fansly.com/api/v1/message', headers=headers, params=(('groupId', group_id),('before', msg_cursor),('limit', '50'),)).json()
        try:
            for x in resp['response']['accountMedia']:
                # set filename
                if naming == 'Date_posted':
                    ts = int(x['createdAt'])
                    file_datetime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
                    file_id = x['id']
                    file_name = f"{file_datetime} {file_id}"
                else:
                    file_name = f"{mycreator}"
                # message media previews
                if previews == 'True':
                    try:
                        sort_download(f"{file_name} preview.{x['preview']['mimetype'].split('/')[1]}", sess.get(x['preview']['locations'][0]['location'], headers=headers).content, preview_directory_name)
                    except:pass
                # unlocked meda in messages
                try:
                    if(x['access'] == True):
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
                output(2,'\n [18]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation.')
                input('\nPress any key to close ...')
                exit()
        except KeyError:
            output(3,' WARNING','<yellow>', 'No scrapeable media found in messages')
            pass
else:output(1,' Info','<light-blue>','No scrapeable media found in messages')

output(1,' Info','<light-blue>','Started profile media download; this could take a while dependant on the content size ...')
cursor = 0
while True:
    if seperate_messages == 'True':
        directory_name = os.path.join(BASE_DIR_NAME, TIMELINE_DIR_NAME)
    else:
        directory_name = BASE_DIR_NAME
    if seperate_previews == 'True':
        preview_directory_name = os.path.join(directory_name, PREVIEWS_DIR_NAME)
    else:
        preview_directory_name = directory_name
    if cursor == 0:output(1,' Info','<light-blue>', f'Inspecting most recent page')
    else:output(1,' Info','<light-blue>', f'Inspecting page: {cursor}')

    # simple attempt to deal with rate limiting
    while True:
        try:
            # people with a high enough internet download speed & hardware specification will manage to hit a rate limit here
            response = sess.get(f'https://apiv3.fansly.com/api/v1/timeline/{creator_id}?before={cursor}&after=0', headers=headers) # outdated; they're serving over 'timeline/home/' ... '&mode=0' now
            break # break if no errors happened, so we can just continue trying with next download
        except:
            output(2,' WARNING','<yellow>', f"Uhm, looks like we've hit a rate limit ..\n{20*' '}Will try to continue the download, infinitely every 15 seconds\n{20*' '}Let me know if this logic worked out at any point in time\n{20*' '}by opening a issue ticket please!")
            print('\n'+traceback.format_exc())
            s(5)
            pass

    try:
        for x in response.json()['response']['accountMedia']:
            # set filename
            if naming == 'Date_posted':
                ts = int(x['createdAt'])
                file_datetime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
                file_id = x['id']
                file_name = f"{file_datetime} {file_id}"
            else:
                file_name = f"{mycreator}"
            # previews
            if previews == 'True':
                try:
                    sort_download(f"{file_name} preview.{x['preview']['mimetype'].split('/')[1]}", sess.get(x['preview']['locations'][0]['location'], headers=headers).content, preview_directory_name)
                except:pass
            # unlocked media
            try:
                if(x['access'] == True):
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
            output(2,'\n [19]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation.')
            input('\nPress any key to close ...')
            exit()
    except KeyError:
        output(2,'\n [20]ERROR','<red>', "Couldn't find any scrapeable media at all!\n This most likely happend because you're not following the creator, your authorisation token is wrong\n or the creator is not providing unlocked content.")
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

full_path = os.path.join(os.getcwd(), BASE_DIR_NAME)
if openwhenfinished == 'True':open_file(full_path)

print('╔═\n  Done! Downloaded '+str(pic_count-1)+' pictures & '+str(vid_count-1)+' videos ('+str(duplicates)+' duplicates declined)\n  Saved in directory: "'+full_path+'"\n  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶'+f'{12*" "}'+'═╝')

input()
