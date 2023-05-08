"""
This code was written over a time span of 3 years and contributed to, by various people.
We've reached a stage where this needs a full re-write, to make this code more readable
and maybe separate functions into sub-files etc. for better maintenance in the future
"""
import requests, os, re, base64, hashlib, imagehash, io, traceback, sys, platform, subprocess, concurrent.futures
from string import digits
from random import choices, randint
from tkinter import Tk, filedialog
from loguru import logger as log
from functools import partialmethod
from PIL import Image
from time import sleep as s
from configparser import RawConfigParser
from datetime import datetime
from os.path import join, exists
from os import makedirs
os.system('title Fansly Scraper')
sess = requests.Session()

def exit():os._exit(0) # pyinstaller

# base64 code to display logo in console
print(base64.b64decode('CiAg4paI4paI4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKWiOKWiOKWiOKVlyDilojilojilojilZcgICDilojilojilZfilojilojilojilojilojilojilojilZfilojilojilZcgIOKWiOKWiOKVlyAgIOKWiOKWiOKVlyAgICDilojilojilojilojilojilojilojilZcg4paI4paI4paI4paI4paI4paI4pWX4paI4paI4paI4paI4paI4paI4pWXICDilojilojilojilojilojilZcg4paI4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVl+KWiOKWiOKWiOKWiOKWiOKWiOKVlyAKICDilojilojilZTilZDilZDilZDilZDilZ3ilojilojilZTilZDilZDilojilojilZfilojilojilojilojilZcgIOKWiOKWiOKVkeKWiOKWiOKVlOKVkOKVkOKVkOKVkOKVneKWiOKWiOKVkSAg4pWa4paI4paI4pWXIOKWiOKWiOKVlOKVnSAgICDilojilojilZTilZDilZDilZDilZDilZ3ilojilojilZTilZDilZDilZDilZDilZ3ilojilojilZTilZDilZDilojilojilZfilojilojilZTilZDilZDilojilojilZfilojilojilZTilZDilZDilojilojilZfilojilojilZTilZDilZDilZDilZDilZ3ilojilojilZTilZDilZDilojilojilZcKICDilojilojilojilojilojilZcgIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVkeKWiOKWiOKVlOKWiOKWiOKVlyDilojilojilZHilojilojilojilojilojilojilojilZfilojilojilZEgICDilZrilojilojilojilojilZTilZ0gICAgIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVl+KWiOKWiOKVkSAgICAg4paI4paI4paI4paI4paI4paI4pWU4pWd4paI4paI4paI4paI4paI4paI4paI4pWR4paI4paI4paI4paI4paI4paI4pWU4pWd4paI4paI4paI4paI4paI4pWXICDilojilojilojilojilojilojilZTilZ0KICDilojilojilZTilZDilZDilZ0gIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVkeKWiOKWiOKVkeKVmuKWiOKWiOKVl+KWiOKWiOKVkeKVmuKVkOKVkOKVkOKVkOKWiOKWiOKVkeKWiOKWiOKVkSAgICDilZrilojilojilZTilZ0gICAgICDilZrilZDilZDilZDilZDilojilojilZHilojilojilZEgICAgIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVlOKVkOKVkOKWiOKWiOKVkeKWiOKWiOKVlOKVkOKVkOKVkOKVnSDilojilojilZTilZDilZDilZ0gIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVlwogIOKWiOKWiOKVkSAgICAg4paI4paI4pWRICDilojilojilZHilojilojilZEg4pWa4paI4paI4paI4paI4pWR4paI4paI4paI4paI4paI4paI4paI4pWR4paI4paI4paI4paI4paI4paI4paI4pWX4paI4paI4pWRICAgICAgIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVkeKVmuKWiOKWiOKWiOKWiOKWiOKWiOKVl+KWiOKWiOKVkSAg4paI4paI4pWR4paI4paI4pWRICDilojilojilZHilojilojilZEgICAgIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVl+KWiOKWiOKVkSAg4paI4paI4pWRCiAg4pWa4pWQ4pWdICAgICDilZrilZDilZ0gIOKVmuKVkOKVneKVmuKVkOKVnSAg4pWa4pWQ4pWQ4pWQ4pWd4pWa4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWd4pWa4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWd4pWa4pWQ4pWdICAgICAgIOKVmuKVkOKVkOKVkOKVkOKVkOKVkOKVnSDilZrilZDilZDilZDilZDilZDilZ3ilZrilZDilZ0gIOKVmuKVkOKVneKVmuKVkOKVnSAg4pWa4pWQ4pWd4pWa4pWQ4pWdICAgICDilZrilZDilZDilZDilZDilZDilZDilZ3ilZrilZDilZ0gIOKVmuKVkOKVnQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBkZXZlbG9wZWQgb24gZ2l0aHViLmNvbS9Bdm5zeC9mYW5zbHkK').decode('utf-8'))

# most of the time, we utilize this to display colored output rather than logging or prints
def output(level, log_type, color, mytext):
    try:log.level(log_type, no=level, color=color)
    except TypeError:pass # level failsave
    log.__class__.type = partialmethod(log.__class__.log, log_type)
    log.remove()
    log.add(sys.stdout, format="<level>{level}</level> | <white>{time:HH:mm}</white> <level>|</level><light-white>| {message}</light-white>", level=log_type)
    log.type(mytext)

output(1,'\n Info','<light-blue>','Reading config.ini file ...')
config = RawConfigParser()
if len(config.read('config.ini')) != 1:
    output(2,'\n [1]ERROR','<red>', 'config.ini file not found or can not be read. Please download it & make sure it is in the same directory as Fansly Scraper')
    input('\nPress any key to close ...')
    exit()


# config.ini backwards compability fix (≤ v0.3.6) -> fix spelling mistake "seperate"
if 'seperate_messages' in config['Options']:
    config['Options']['separate_messages'] = config['Options'].pop('seperate_messages')
if 'seperate_previews' in config['Options']:
    config['Options']['separate_previews'] = config['Options'].pop('seperate_previews')
with open('config.ini', 'w', encoding='utf-8') as f:config.write(f)


# I'm aware that I could've used config.getint(), getfloat, getboolean etc.
try:
    # TargetedCreator
    mycreator = config['TargetedCreator']['Username'] # string

    # MyAccount
    mytoken = config['MyAccount']['Authorization_Token'] # string
    myuseragent = config['MyAccount']['User_Agent'] # string

    # Options
    download_mode = config['Options']['download_mode'].capitalize() # Normal (Timeline & Messages), Single (Single by post id), Collections
    show = config['Options']['show_downloads'].capitalize() # True, False
    remember = config['Options']['update_recent_download'].capitalize() # Auto, True, False
    previews = config.getboolean('Options', 'download_media_previews') # True, False -> this is the only var that is treated as a boolean
    openwhenfinished = config['Options']['open_folder_when_finished'].capitalize() # True, False
    naming = config['Options']['naming_convention'].capitalize() # Date_posted, Standard
    separate_messages = config['Options']['separate_messages'].capitalize() # True, False
    separate_previews = config['Options']['separate_previews'].capitalize() # True, False
    base_directory = config['Options']['download_directory'] # Local_directory, C:\MyCustomFolderFilePath

    # Other
    curent_ver = config['Other']['version'] # float
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

for x in show,previews,openwhenfinished,separate_messages,separate_previews:
    if x != 'True' and x != 'False' and x != True and x != False:
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


#########################################################################################################
# handles download_directory changes, has to be on top here now, because there's multiple download_mode's

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


def generate_base_dir(creator_name_to_create_for):
    global BASE_DIR_NAME, base_directory
    if base_directory == 'Local_directory': # if user didn't specify custom downloads path
        if "Collection" in download_mode:
            BASE_DIR_NAME = join(os.getcwd(), 'Collections')
        else:
            BASE_DIR_NAME = creator_name_to_create_for+'_fansly' # use local directory
    elif os.path.isdir(base_directory): # if user specified a correct custom downloads path
        if "Collection" in download_mode:
            BASE_DIR_NAME = join(base_directory, 'Collections')
        else:
            BASE_DIR_NAME = join(base_directory, creator_name_to_create_for+'_fansly') # use their custom path & specify new folder for the current creator in it
        output(1,' Info','<light-blue>', f'Acknowledging custom basis download directory: "{base_directory}"')
    else: # if their set directory, can't be found by the OS
        output(3,'\n WARNING','<yellow>', f"The custom basis download directory file path '{base_directory}'; seems to be invalid!\n{20*' '}Please change it, to a correct file path for example: 'C:\\MyFanslyDownloads'\n{20*' '}You could also just change it back to the default argument: 'Local_directory'\n\n{20*' '}A explorer window to help you set the correct path, will open soon!\n\n{20*' '}Preferably right click inside the explorer, to create a new folder\n{20*' '}Select it and the folder will be used as the default download directory")
        s(10) # give user time to realise instructions were given
        base_directory = ask_correct_dir() # ask user to select correct path using tkinters explorer dialog
        config.set('Options', 'download_directory', base_directory) # set corrected path inside the config
        with open('config.ini', 'w', encoding='utf-8') as f:config.write(f) # save the config permanently into config.ini
        if "Collection" in download_mode:
            BASE_DIR_NAME = join(base_directory, 'Collections')
        else:
            BASE_DIR_NAME = join(base_directory, creator_name_to_create_for+'_fansly') # use their custom path & specify new folder for the current creator in it
    return BASE_DIR_NAME

#########################################################################################################

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


# new function to sort downloads, should later on be utilised with normal & messages download also
# misses: hashing compability, intentionally don't want to add naming_convention support (realistically no one uses anything else but Date_posted anyways, so we just default to it in the future)
def sort_download_NEW(accessible_media):
    # these are also globally defined, in old code, but for now just want them local
    pic_count, vid_count = 0, 0
    
    # loop through the accessible_media and download the media files
    for post in accessible_media:
        # extract the necessary information from the post
        media_id = post['media_id']
        created_at = datetime.utcfromtimestamp(int(post['created_at'])).strftime('%Y-%m-%d %H-%M-%S')
        mimetype = post['mimetype']
        download_url = post['download_url']
    
        # determine the file format from the mimetype
        file_format = mimetype.split('/')[-1]

        filename = f"{created_at} {media_id}.{file_format}"

        if "Collection" in download_mode:
            # for collections downloads we just put everything into the same folder
            save_path = join(BASE_DIR_NAME, filename)
            save_dir = join(BASE_DIR_NAME, filename) # compability for "Download finished...!" print

            if not exists(BASE_DIR_NAME):
                makedirs(BASE_DIR_NAME)
        
        elif "Single" in download_mode:
            # for single post downloads, we do want to determine the directory to save the media file based on the mimetype
            if 'image' in mimetype:
                save_dir = join(BASE_DIR_NAME, "Pictures")
            elif 'video' in mimetype:
                save_dir = join(BASE_DIR_NAME, "Videos")
            else:
                # if the mimetype is neither image nor video, skip the download
                output(3,' WARNING','<yellow>', f'Unknown mimetype; skipping download for mimetype: "{mimetype}" | media_id: {media_id} ')
                continue
            save_path = join(save_dir, filename)

            if not exists(save_dir):
                makedirs(save_dir)
    
        # download the media file
        response = sess.get(download_url, stream=True, headers=headers)
        if response.ok:
            # if show_downloads is True / downloads should be shown
            if show == 'True':
                output(1,' Info','<light-blue>', f"Downloading {mimetype.split('/')[-2]} '{filename}'")

            with open(save_path, 'wb') as f:
                # iterate over the response data in chunks of 1024
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        # we only count them if the file was actually written
                        pic_count += 1 if 'image' in mimetype else 0; vid_count += 1 if 'video' in mimetype else 0
        else:
            output(2,'\n [15]ERROR','<red>', f"Download failed on filename: {filename} - due to an network error --> status_code: {response.status_code} | content: \n{response.content}")
            input()
            exit()

    # for now this won't support naming_convention (i dont really want that option anymore anyways)
    # as later on I plan to make one function and then tunnel everything (normal, single, messages, collection) through it and that way shorten this codes line length by like 50%
    print(f'\n╔═\n  Finished {download_mode} type, download of {pic_count} pictures & {vid_count} videos!\n  Saved content in directory: "{save_dir}"\n  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶\n{74*" "}═╝')
    input()
    exit()



# atm this function is only being utilised by single post & collections download, but will prolly use this for everything in a re-write / re-factoring of the whole code
def parse_media_info(media_info):
    # initialize variables
    highest_resolution_url, download_url =  None, None
    created_at, media_id, highest_resolution = 0, 0, 0

    # get mimetype
    mimetype = media_info['media']['mimetype']

    # check if media is a preview
    is_preview = media_info['previewId'] is not None

    # get download URL from media location
    if 'location' in media_info['media']:
        variants = media_info['media']['variants']
        for image in variants:
            if image.get('locations'):
                location_url = image['locations'][0]['location']

                resolution = image['width'] * image['height']
                if resolution > highest_resolution:
                    highest_resolution = resolution
                    highest_resolution_url = location_url
                    media_id = image['id']
                    """
                    too many timestamps were similar with bundles,
                    it wouldn't have worked for unique naming convention titles
                    so like this, it comes closest to a unique creation date
                    """
                    try:
                        created_at = int(image['updatedAt'] + randint(-3600, 3600))
                    except KeyError:
                        created_at = int(media_info['media']['createdAt'] + randint(-3600, 3600))
        download_url = highest_resolution_url

    # if media location is not found, get the preview instead
    if not download_url and 'preview' in media_info:
        for location in media_info['preview']['locations']:
            media_id = media_info['preview']['id']
            created_at = media_info['preview']['createdAt']
            download_url = location['location']

    return {'media_id': media_id, 'created_at': created_at, 'mimetype': mimetype, 'is_preview': is_preview, 'download_url': download_url}


## starting here: download_mode = Single
if download_mode == "Single":
    output(1,' Info','<light-blue>', f'You have launched in single post download mode\n{17*" "}Please enter the ID of the post you would like to download\n{17*" "}After you click on a post, it will show in your browsers url bar')
    
    while True:
        post_id = input(f'\n{17*" "}Post ID: ')
        if post_id.isdigit() and len(post_id) >= 10 and not any(char.isspace() for char in post_id):
            break
        else:
            output(2,'\n [13]ERROR','<red>', f'The input string "{post_id}" can not be a valid post ID.\n{22*" "}The last few numbers in the url is the post ID\n{22*" "}Example: "https://fansly.com/post/1283998432982"\n{22*" "}In the example "1283998432982" would be the post ID')

    post_req = sess.get('https://apiv3.fansly.com/api/v1/post', params={'ids': post_id, 'ngsw-bypass': 'true',}, headers=headers)

    if post_req.status_code == 200:
        creator_username, creator_display_name = None, None # from: "accounts"
        accessible_media = None
        contained_posts = []

        # post object contains: posts, aggregatedPosts, accountMediaBundles, accountMedia, accounts, tips, tipGoals, stories, polls
        post_object = post_req.json()['response']

        # iterate through object and fetch relevant information
        for __ in post_object:

            # parse post creator name
            if not creator_username:
                creator_username = post_object['accounts'][0]['username'] # using this to generate custom download path for single posts
                creator_display_name = post_object['accounts'][0]['displayName'] # warning; contains unicode characters

                if creator_display_name and creator_username:
                    output(1,' Info','<light-blue>', f'Inspecting a post by {creator_display_name} (@{creator_username})')
                else:
                    output(1,' Info','<light-blue>', f'Inspecting a post by {creator_username.capitalize()}')

            # parse relevant details about the post
            if not accessible_media:
                # loop through the list of dictionaries and find the highest quality media URL for each one
                for obj in post_object['accountMedia']:
                    # add details into a list
                    contained_posts += [parse_media_info(obj)]

                # summarise all scrapable & wanted media
                accessible_media = [item for item in contained_posts if item.get('download_url') and (item.get('is_preview') == previews or not item.get('is_preview'))]

    else:
        output(2,'\n [14]ERROR','<red>', f'Failed single post download. Fetch post information request, response code: {post_req.status_code}\n{post_req.text}')

    # at this point we have already parsed the whole post object and determined what is scrapable with the code above
    output(1,' Info','<light-blue>', f"Amount of Media: {len(post_object['accountMedia'])} (scrapable: {len(accessible_media)})")

    """
    generate a base dir based on various factors, except this time we ovewrite the username from config.ini
    with the custom username we analysed through single post download mode's post_object. this is because
    the user could've decide to just download some random creators post instead of the one that he currently
    set as creator for > TargetCreator > username in config.ini
    """
    generate_base_dir(creator_username)

    # download it
    sort_download_NEW(accessible_media)



## starting here: download_mode = Collection(s)
if "Collection" in download_mode:
    output(1,' Info','<light-blue>', f'Running in collections mode')
    # send a first request to get all available "accountMediaId" ids, which are basically media ids of every graphic listed on /collections
    collections_req = sess.get('https://apiv3.fansly.com/api/v1/account/media/orders/', params={'limit': '100','offset': '0','ngsw-bypass': 'true'}, headers=headers)
    collections_req = collections_req.json()
    
    # format all ids from /account/media/orders (collections)
    accountMediaIds = ','.join([order['accountMediaId'] for order in collections_req['response']['accountMediaOrders']])
    
    # input them into /media?ids= to get all relevant information about each purchased media in a 2nd request
    post_object = sess.get(f'https://apiv3.fansly.com/api/v1/account/media?ids={accountMediaIds}', headers=headers)
    post_object = post_object.json()
    
    contained_posts = []
    
    for obj in post_object['response']:
        # add details into a list
        contained_posts += [parse_media_info(obj)]
    
    # count only amount of scrapable media (is_preview check not really necessary since everything in collections is always paid, but w/e)
    accessible_media = [item for item in contained_posts if item.get('download_url') and (item.get('is_preview') == previews or not item.get('is_preview'))]

    output(1,' Info','<light-blue>', f"Amount of Media: {len(post_object['response'])} (scrapable: {len(accessible_media)})")
    
    generate_base_dir(mycreator)

    # download it
    sort_download_NEW(accessible_media)




## starting here: download_mode = Normal
generate_base_dir(mycreator) # generate a base directory for download_mode: Normal

try:
    raw_req = sess.get(f'https://apiv3.fansly.com/api/v1/account?usernames={mycreator}', headers=headers)
    acc_req = raw_req.json()['response'][0]
    creator_id = acc_req['id']
except KeyError as e:
    if raw_req.status_code == 401:
        output(2,'\n [16]ERROR','<red>', 'API returned unauthorized. This is most likely because of a wrong authorization token, in the configuration file.')
        print(f'{21*" "}Used authorization token: "'+mytoken+'"')
    else:output(2,'\n [17]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed.')
    print('\n'+str(e))
    print(raw_req.text)
    input('\nPress any key to close ...')
    exit()
except IndexError as e:
    output(2,'\n [18]ERROR','<red>', 'Bad response from fansly API. Please make sure your configuration file is not malformed; most likely misspelled the creator name.')
    print('\n'+str(e))
    print(raw_req.text)
    input('\nPress any key to close ...')
    exit()

try:following = acc_req['following']
except KeyError:following = False
try:subscribed = acc_req['subscribed']
except KeyError:subscribed = False
try:
    total_photos = acc_req['timelineStats']['imageCount']
except KeyError:
    output(2,'\n [19]ERROR','<red>', 'Can not get timelineStats for creator username; most likely creator username misspelled')
    input('\nPress any key to close ...')
    exit()
total_videos = acc_req['timelineStats']['videoCount']

output(1,' Info','<light-blue>', f'Targeted creator: "{mycreator}"')
output(1,' Info','<light-blue>', f'Using user-agent: "{myuseragent[:28]} [...] {myuseragent[-35:]}"')
output(1,' Info','<light-blue>', f'Open download folder when finished, is set to: "{openwhenfinished}"')
output(1,' Info','<light-blue>', f'Downloading files marked as preview, is set to: "{previews}"')

if previews == True:output(3,' WARNING','<yellow>', 'Previews downloading is enabled; repetitive and/or emoji spammed media might be downloaded!')
if remember == 'True':output(3,' WARNING','<yellow>', 'Update recent download is enabled')

if randint(1,100) <= 19:
    output(4,'\n lnfo','<light-red>', f"Fansly scraper was downloaded {tot_downs} times, but only {round(requests.get('https://api.github.com/repos/avnsx/fansly', headers={'User-Agent':'Fansly Scraper'}).json()['stargazers_count']/tot_downs*100, 2)} % of You(!) have starred it.\n{17*' '}Stars directly influence my willingness to continue maintaining the project.\n{17*' '}Help the repository grow today, by leaving a star on it and sharing it to others online!")
    s(15)

recent_photobyte_hashes, recent_videobyte_hashes = [], []

MESSAGES_DIR_NAME = 'Messages'
TIMELINE_DIR_NAME = 'Timeline'
PREVIEWS_DIR_NAME = 'Previews'
PICTURES_DIR_NAME = 'Pictures'
VIDEOS_DIR_NAME = 'Videos'
COLLECTIONS_DIR_NAME = 'Collections' # this is not even getting utilized atm

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


# if separate_collections == 'True':
#     collections_dir = join(BASE_DIR_NAME, COLLECTIONS_DIR_NAME)
#     makedirs(collections_dir, exist_ok = True)
#     makedirs(join(collections_dir, PICTURES_DIR_NAME), exist_ok = True)
#     makedirs(join(collections_dir, VIDEOS_DIR_NAME), exist_ok = True)


if remember == 'True':
    if os.path.isdir(BASE_DIR_NAME):
        output(1,' Info','<light-blue>', f'"{BASE_DIR_NAME}" folder already exists in specified directory')
    else:
        output(3,' WARNING','<yellow>', f"'{BASE_DIR_NAME}' folder is not located in the specified directory; but you launched in update recent download mode,\n{20*' '}so find & select the folder that contains recently downloaded 'Messages', 'Timeline' & 'Collections' as subfolders (it should be called '{BASE_DIR_NAME}')")
        ask_correct_dir()

    list_of_futures=[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for x in '', TIMELINE_DIR_NAME, MESSAGES_DIR_NAME, COLLECTIONS_DIR_NAME, PREVIEWS_DIR_NAME, join(TIMELINE_DIR_NAME, PREVIEWS_DIR_NAME), join(MESSAGES_DIR_NAME, PREVIEWS_DIR_NAME), join(COLLECTIONS_DIR_NAME, PREVIEWS_DIR_NAME):
            x_path = join(BASE_DIR_NAME, x)
            if os.path.isdir(x_path):
                p_path = join(x_path, PICTURES_DIR_NAME)
                v_path = join(x_path, VIDEOS_DIR_NAME)
                c_path = join(x_path, COLLECTIONS_DIR_NAME)

                if os.path.isdir(p_path):
                    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded pictures from {p_path} ...")
                    for el in os.listdir(p_path):
                        list_of_futures.append(executor.submit(process_img, f'{p_path}/{el}'))
                        
                if os.path.isdir(v_path):
                    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded videos from {v_path} ...")
                    for el in os.listdir(v_path):
                        list_of_futures.append(executor.submit(process_vid, f'{v_path}/{el}'))

                if os.path.isdir(v_path):
                    output(1,' Info','<light-blue>', f"Hashing {mycreator}'s recently downloaded videos from {v_path} ...")
                    for el in os.listdir(v_path):
                        list_of_futures.append(executor.submit(process_vid, f'{v_path}/{el}'))

    concurrent.futures.wait(list_of_futures)

    output(1,' Info','<light-blue>', f'Finished hashing! Will now compare each new download against {len(recent_photobyte_hashes)} photo & {len(recent_videobyte_hashes)} video hashes.')
else:
    try:
        output(1,' Info','<light-blue>','Creating download directories ...')
        makedirs(BASE_DIR_NAME, exist_ok = True)

        if separate_messages == 'True':
            messages_dir = join(BASE_DIR_NAME, MESSAGES_DIR_NAME)
            makedirs(messages_dir, exist_ok = True)
            makedirs(join(messages_dir, PICTURES_DIR_NAME), exist_ok = True)
            makedirs(join(messages_dir, VIDEOS_DIR_NAME), exist_ok = True)
            timeline_dir = join(BASE_DIR_NAME, TIMELINE_DIR_NAME)
            makedirs(timeline_dir, exist_ok = True)
            makedirs(join(timeline_dir, PICTURES_DIR_NAME), exist_ok = True)
            makedirs(join(timeline_dir, VIDEOS_DIR_NAME), exist_ok = True)
            if previews == True and separate_previews == 'True':
                messages_preview_dir = join(messages_dir, PREVIEWS_DIR_NAME)
                makedirs(messages_preview_dir, exist_ok = True)
                makedirs(join(messages_preview_dir, PICTURES_DIR_NAME), exist_ok = True)
                makedirs(join(messages_preview_dir, VIDEOS_DIR_NAME), exist_ok = True)
                timeline_preview_dir = join(timeline_dir, PREVIEWS_DIR_NAME)
                makedirs(timeline_preview_dir, exist_ok = True)
                makedirs(join(timeline_preview_dir, PICTURES_DIR_NAME), exist_ok = True)
                makedirs(join(timeline_preview_dir, VIDEOS_DIR_NAME), exist_ok = True)
        else:
            makedirs(join(BASE_DIR_NAME, PICTURES_DIR_NAME), exist_ok = True)
            makedirs(join(BASE_DIR_NAME, VIDEOS_DIR_NAME), exist_ok = True)
            if separate_previews == 'True':
                preview_dir = join(BASE_DIR_NAME, PREVIEWS_DIR_NAME)
                makedirs(preview_dir, exist_ok = True)
                makedirs(join(preview_dir, PICTURES_DIR_NAME), exist_ok = True)
                makedirs(join(preview_dir, VIDEOS_DIR_NAME), exist_ok = True)
    except Exception:
        print('\n'+traceback.format_exc())
        output(2,'\n [20]ERROR','<red>', 'Issue while creating download directories ... Please copy & paste this on GitHub > Issues & provide a short explanation.')
        input('\nPress any key to close ...')
        exit()


# this function handles the downloading from messages & normal site content. single post downloads have their own function to download
pic_count, vid_count, duplicates, recent, photobyte_hashes, videobyte_hashes = 1, 1, 0, 0, [], []
def sort_download(filename, responseObject, directoryName):
    global pic_count, vid_count, duplicates, recent
    filebytes = responseObject.content
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
                with open(f"{directoryName}/Pictures/{prefix}{win_comp_name}", 'wb') as f:
                    for chunk in responseObject.iter_content(chunk_size=1024): # Iterate over the response data in chunks; optimises memory usage
                        if chunk:
                            f.write(chunk)
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
                with open(f"{directoryName}/Videos/{prefix}{win_comp_name}", 'wb') as f:
                    for chunk in responseObject.iter_content(chunk_size=1024): # Iterate over the response data in chunks; optimises memory usage
                        if chunk:
                            f.write(chunk)
                videobyte_hashes.append(videohash)
                vid_count+=1
            else:duplicates+=1
        else:recent+=1
    else:
        output(2,'\n [21]ERROR','<red>', 'Unknown filetype: "'+str(filename[-7:])+'" please report this on GitHub > Issues & provide a short explanation; continuing without that file ...')



# Messages Media Logic
group_id = None
groups = sess.get('https://apiv3.fansly.com/api/v1/group', headers=headers).json()['response']['groups']

for group in groups:
    for user in group['users']:
        if user['userId'] == creator_id:
            group_id = group['id']
            break
    if group_id:
        break

if group_id:
    output(1, ' Info', '<light-blue>', 'Started Messages media download ...')
    msg_cursor = None
    while True:
        directory_name = join(BASE_DIR_NAME, MESSAGES_DIR_NAME) if separate_messages == 'True' else BASE_DIR_NAME
        preview_directory_name = join(directory_name, PREVIEWS_DIR_NAME) if separate_previews == 'True' else directory_name
        resp = sess.get('https://apiv3.fansly.com/api/v1/message', headers=headers, params={'groupId': group_id, 'before': msg_cursor, 'limit': '50'} if msg_cursor else {'groupId': group_id, 'limit': '50'}).json()
        try:
            for x in resp['response']['accountMedia']:
                ts = int(x['createdAt'])
                file_datetime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H-%M-%S')
                file_id = x['id']
                file_name = f"{file_datetime} {file_id}" if naming == 'Date_posted' else f"{mycreator}"
                if previews == True:
                    try:
                        sort_download(f"{file_name} preview.{x['preview']['mimetype'].split('/')[1]}", sess.get(x['preview']['locations'][0]['location'], stream=True, headers=headers), preview_directory_name)
                    except:
                        pass
                try:
                    if x['access']:
                        locurl = x['media']['locations'][0]['location']
                        sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, stream=True, headers=headers), directory_name)
                except IndexError:
                    for f in range(len(x['media']['variants'])):
                        try:
                            locurl = x['media']['variants'][f]['locations'][0]['location']
                            sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, stream=True, headers=headers), directory_name)
                            break
                        except:
                            pass
                except:
                    pass
            try:
                msg_cursor = resp['response']['messages'][-1]['id']
            except IndexError:
                break
            except Exception as e:
                print(f"\nError: {e}")
                output(2, '\n [22]ERROR', '<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation.')
                input('\nPress any key to close ...')
                exit()
        except KeyError:
            output(3, 'WARNING', '<yellow>', 'No scrapable media found in messages')
            pass
else:
    output(1, 'Info', '<light-blue>', 'No scrapable media found in messages')



# Timeline Media Logic
output(1,' Info','<light-blue>','Started Timeline media download; this could take a while dependant on the content size ...')
cursor = 0
while True:
    directory_name = join(BASE_DIR_NAME, TIMELINE_DIR_NAME) if separate_messages == 'True' else BASE_DIR_NAME
    preview_directory_name = join(directory_name, PREVIEWS_DIR_NAME) if separate_previews == 'True' else directory_name

    if cursor == 0:output(1,' Info','<light-blue>', f'Inspecting most recent page')
    else:output(1,' Info','<light-blue>', f'Inspecting page: {cursor}')
    
    # simple attempt to deal with rate limiting
    for itera in range(9999):
        try:
            # people with a high enough internet download speed & hardware specification will manage to hit a rate limit here
            response = sess.get(f'https://apiv3.fansly.com/api/v1/timeline/{creator_id}?before={cursor}&after=0', headers=headers) # timeline
            break # break if no errors happened, so we can just continue trying with next download
        except:
            if itera == 0: # on first ever rate limitation; we hope /timelinenew silently bypasses the rate limit for /timeline
                try:
                    response = sess.get(f'https://apiv3.fansly.com/api/v1/timelinenew/{creator_id}?before={cursor}&after=0', headers=headers) # timelinenew
                    break # break if no errors happened, so we can just continue trying with next download
                except:continue
            elif itera == 1: # if we get here, we know that /timelinenew has the same rate limits as /timeline, so just now we start notifying the user
                output(2,' WARNING','<yellow>', f"Uhm, looks like we've hit a rate limit ..\n{20*' '}Using a VPN, might fix this issue entirely.\n{20*' '}Regardless, will now try to continue the download, infinitely every 15 seconds\n{20*' '}Let me know if this logic worked out at any point in time\n{20*' '}by opening a issue ticket please!")
                print('\n'+traceback.format_exc())
            else: # user got notified already and can now enjoy seeing infinite attempts on /timeline
                print(f'attempt {itera} ...')
            s(15)

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
            if previews == True:
                try:
                    sort_download(f"{file_name} preview.{x['preview']['mimetype'].split('/')[1]}", sess.get(x['preview']['locations'][0]['location'], stream=True, headers=headers), preview_directory_name)
                except:pass
            # unlocked media
            try:
                if(x['access'] == True):
                    locurl=x['media']['locations'][0]['location']
                    sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, stream=True, headers=headers), directory_name)
            # unlocked media without corresponding location url
            except IndexError:
                for f in range(0,len(x['media']['variants'])):
                    try:
                        locurl=x['media']['variants'][f]['locations'][0]['location']
                        sort_download(f"{file_name}.{x['media']['mimetype'].split('/')[1]}", sess.get(locurl, stream=True, headers=headers), directory_name)
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
            output(2,'\n [23]ERROR','<red>', 'Please copy & paste this on GitHub > Issues & provide a short explanation.')
            input('\nPress any key to close ...')
            exit()
    except KeyError:
        output(2,'\n [24]ERROR','<red>', "Couldn't find any scrapable media at all!\n This most likely happend because you're not following the creator, your authorisation token is wrong\n or the creator is not providing unlocked content.")
        input('\nPress any key to close ...')
        exit()
    if remember == 'True' and recent > int(total_photos+total_videos) * 0.2:
        print(f"\n╔═\n  Finished download; it looks like we've had already or have just downloaded all possible new content.\n\t\t  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶{10*' '}═╝")
        s(120)
        exit()

print('')
issue=False
if pic_count-1 <= total_photos * 0.2 and remember == 'False':
    output(3,' WARNING','<yellow>', f'Low amount of content scraped. Creators total Pictures: {total_photos}, downloaded Pictures: {pic_count-1}')
    issue = True

if vid_count-1 <= total_videos * 0.2 and remember == 'False':
    output(3,' WARNING','<yellow>', f'Low amount of content scraped. Creators total Videos: {total_videos}, downloaded Videos: {vid_count-1}')
    issue = True

if issue == True:
    if following == False:print(f'{20*" "}Follow the creator; to be able to scrape more media!')
    if subscribed == False:print(f'{20*" "}Subscribe to the creator; if you would like to get the entire content.')
    if previews == False:print(f'{20*" "}Try setting Media Preview Downloads on, this helps if the creator marks all his content as previews.')
    print('')

full_path = join(os.getcwd(), BASE_DIR_NAME)
if openwhenfinished == 'True':open_file(full_path)

print(f'╔═\n  Done! Downloaded {pic_count-1} pictures & {vid_count-1} videos ({duplicates} duplicates declined)\n  Saved in directory: "{full_path}"\n  ✶ Please leave a Star on the GitHub Repository, if you are satisfied! ✶{12*" "}═╝')

input()
