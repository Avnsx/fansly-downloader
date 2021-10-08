import requests,os,re,base64
from time import sleep as s
from configparser import ConfigParser

print(base64.b64decode('IC5kODg4ICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4UCIgICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgIDg4ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKIDg4ODg4IDg4ODhiLiA4ODg4Yi4gIC5kODg4OGIgIDg4IDg4ICA4OCAgICAgIC5kODg4OGIgIC5kODg4OGIgLjhkODg4IDg4ODhiLiAuODg4OGIuICAuZDg4Yi4gIC44OGQ4ODgKIDg4ICAgICAgICI4OCA4OCAiODhiIDg4SyAgICAgIDg4IDg4ICA4OCAgICAgIDg4SyAgICAgIDg4UCIgICAgODhQIiAgICAgICI4OCA4OCAiODhiIGQ4UCAgWThiIDg4UCIgICAKIDg4ICAgLmQ4ODg4OCA4OCAgODg4ICJZODg4OGIuIDg4IDg4ICA4OCAgICAgICJZODg4OGIuIDg4ICAgICAgODggICAgLmQ4ODg4OCA4OCAgODg4IDg4ODg4ODg4IDg4ICAgICAKIDg4ICAgODg4ICA4OCA4OCAgODg4ICAgICAgWDg4IDg4IDg4YiA4OCAgICAgICAgICAgWDg4IDg4Yi4gICAgODggICAgODg4ICA4OCA4OCBkODhQIFk4Yi4gICAgIDg4ICAgICAKIDg4ICAgIlk4ODg4OCA4OCAgODg4ICA4ODg4OFAnIDg4IFk4ODg4OCAgICAgICA4ODg4OFAnICJZODg4OFAgODggICAgIlk4ODg4OCA4ODg4UCIgICAiWTg4ODggIDg4ICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDhiIGQ4OCAgICBodHRwczovL2dpdGh1Yi5jb20vQXZuc3gvZmFuc2x5ICA4OCAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICJZODhQIiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA4OCAgICAgICAgICAgICAgICAgICAgICA=').decode('ascii'))

print("\nReading configuration (.ini) file ...")
config = ConfigParser()
config.read('config.ini')
sess = requests.Session()

try:
    mycreator = config['TargetedCreator']['Username']
    mytoken = config['MyAccount']['Authorization_Token']
    myuseragent = config['MyAccount']['User_Agent']
    previews = config['Options']['Download_Media_Previews'].capitalize()
    openwhenfinished = config['Options']['Open_Folder_When_Finished'].capitalize()
except (KeyError, NameError) as e:
    print('ERROR: "'+str(e)+'" is missing or malformed in the configuration file! Read the ReadMe file for assistance.')
    s(15)
    exit()

for x in mycreator,mytoken,myuseragent,previews,openwhenfinished:
    if x == '' or x == 'ReplaceMe':
        print('ERROR: "'+str(x)+'" is unmodified, missing or malformed in the configuration file! Read the ReadMe file for assistance.')
        s(15)
        exit()

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://fansly.com/',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': mytoken,
    'User-Agent': myuseragent,
}

try:
    creator_id = sess.get('https://apiv2.fansly.com/api/v1/account?usernames='+mycreator, headers=headers).json()['response'][0]['avatar']['accountId']
except KeyError:
    print('ERROR: No response from fansly API. Please make sure your configuration file is not malformed.')
    s(15)
    exit()

print('Targeted creator: "'+mycreator+'"\nUsing authorisation token: "'+mytoken+'"\nUsing useragent: "'+myuseragent+'"\nOpen download folder when finished, is set to: "'+openwhenfinished+'"\nDownloading files marked as preview, is set to: "'+previews+'"\n')
if previews == 'True':print('> WARNING: Previews downloading is enabled; repetitive and/or emoji spammed media might be downloaded!\n')

try:
    print('Creating download directories ...')
    basedir=mycreator+'_fansly'
    os.makedirs(basedir, exist_ok = True)
    os.makedirs(basedir+'/Pictures', exist_ok = True)
    os.makedirs(basedir+'/Videos', exist_ok = True)
except Exception as e:
    print(e)
    print('ERROR: Creating download directories ... Please copy & paste this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
    s(60)
    exit()

pic_count=1
vid_count=1
def sort_download(filename,fileloc):
    global pic_count, vid_count
    if re.findall(r'.jpeg|.png|.jpg|.tif|.tiff|.bmp', filename[-6:]):
        with open(basedir+'/Pictures/'+str(pic_count)+'_'+filename, 'wb') as f:f.write(fileloc)
        pic_count+=1
    elif re.findall(r'.mp4|.mkv|.mov|.gif|.wmv|.flv|.webm', filename[-6:]):
        with open(basedir+'/Videos/'+str(vid_count)+'_'+filename, 'wb') as f:f.write(fileloc)
        vid_count+=1
    else:
        print('\nERROR: Unknown filetype: "'+str(filename[-7:])+'" please report this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
        s(60)
        exit()

print('Starting media download ...')
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
            except Exception as e:
                print(e)
                print('\nERROR: Please copy & paste this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
                s(60)
                exit()
        # get next cursor
        try:
            cursor = response.json()['response']['posts'][-1]['id']
            print('Downloading media from page: '+cursor)
        except IndexError:break #break if end is reached
        except Exception as e:
            print(e)
            print('\nERROR: Please copy & paste this on GitHub > Issues & provide a short explanation; closing in 60 seconds.')
            s(60)
            exit()
    except KeyError:
        print("\nERROR: Couldn't find any scrapeable media at all!\nThis most likely happend because you're not following the creator, your authorisation token is wrong or the creator is not providing unlocked content.\nClosing in 15 Seconds.")
        s(15)
        exit()

full_path=os.getcwd()+'\\'+basedir
print('\n╔═\n  Media downloaded! Your configuration returned '+str(pic_count-1)+' pictures & '+str(vid_count-1)+' videos.\n  Saved in directory: "'+full_path+'"\n  Please leave a Star on the GitHub Repository if you like the code!\n  Also would appreciate it, if you supported with Crypto:\n  BTC: bc1q82n68gmdxwp8vld524q5s7wzk2ns54yr27flst\n  ETH: 0x645a734Db104B3EDc1FBBA3604F2A2D77AD3BDc5'+f'{20*" "}'+'═╝')

if previews == 'False':
    m_s="\n> INFO: Low amount of edit detected; check if you're following the creator.\n Otherwise try setting preview downloads on, this helps if the creator marks all his content as previews."
    if pic_count < 8:print(m_s.replace('edit','Pictures'))
    if vid_count < 5:print(m_s.replace('edit','Videos'))

if openwhenfinished == 'True':os.startfile(full_path)

s(60)
exit()
