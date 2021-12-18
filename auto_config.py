"""
this would've been way easier if leveldb / plyvel were scalable compatible
github.com/wbolster/plyvel/issues/137

and if sublime devs were not lazy, I would've implemented input instead of awaiting keypress
github.com/sublimehq/sublime_text/issues/5111

please do not use the code provided for malicious purposes
"""

import platform
os_v=platform.system()
if os_v == 'Windows':print('Detected Supported OS; Windows')
else:
	print(f'Detected Unsupported OS; {os_v} - please enter data manually into config.ini')
	s(60)
	exit()

import time,psutil,re,sqlite3,traceback,os,json,win32con,win32api,win32gui,win32process,win32crypt,requests,keyboard,shutil,base64
from seleniumwire.undetected_chromedriver import uc
from time import sleep as s
from re import search
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
from configparser import ConfigParser
from Crypto.Cipher import AES
sess = requests.Session()

print('Reading config.ini file ...')
config = ConfigParser()
if len(config.read('config.ini')) != 1:
	print('config.ini file not found or can not be read. Please download it & make sure it is in the same directory as Fansly Scraper & auto_config')
	s(60)
	exit()

ti=0
def save_changes(arg1, arg2):
	global ti, cur, db
	if ti == 0:
		print(f'\nFound required strings with {compatible}!\nAuthorization_Token = {auth}\nUser_Agent = {ua}\n\nOverwriting config.ini ...')
		ti+=1
	config.set('MyAccount', arg1, arg2)
	with open('config.ini', 'w', encoding='utf-8') as configfile:config.write(configfile)
	if ti == 1:
		print('Done! Now all you have to do is; write your Fansly content creators name into the config.ini file and you can start Fansly Scraper!')
		try:cur.close()
		except:pass
		try:db.close()
		except:pass
		try:os.remove('chromedriver')
		except:pass
		try:os.remove('log_d.db')
		except:pass
		s(60)
		os._exit(1)

print('Reading default browser from registry ...')
with OpenKey(HKEY_CURRENT_USER, r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice') as key:used_browser=QueryValueEx(key, 'ProgId')[0] # win only

compatible = None
for x in ['Firefox','Brave','Opera','Chrome','MSEdge']:
	if search(x, used_browser):
		compatible=x
		break
if search('App', used_browser):compatible='MSEdge'

if compatible:print(f'Good News! Your default browser is {compatible} -> a compatible browser for auto configuration!')
if not compatible:
	print(f'Your browser ({used_browser}) is not supported, please enter data manually into config.ini')
	s(60)
	exit()

if compatible == 'Chrome':
	fp=os.getenv('localappdata')+r'\Google\Chrome\User Data'
if compatible == 'MSEdge':
	fp=os.getenv('localappdata')+r'\Microsoft\Edge\User Data'
if compatible == 'Brave':
	fp=os.getenv('localappdata')+r'\BraveSoftware\Brave-Browser\User Data'
if compatible == 'Opera':
	fp=os.getenv('appdata')+r'\Opera Software\Opera Stable'
if compatible == 'Firefox':
	bp = os.getenv('appdata')+r'\Mozilla\Firefox\Profiles'
	myprofiles=[]
	for file in os.listdir(bp):myprofiles.append(os.path.join(file))
	if len(myprofiles) == 0:
		print('ERROR: Required files were not found at all, enter data manually into config.ini')
		s(60)
		exit()
	prf_c=1
	for prf in myprofiles:
		fp = f'{bp}\\{prf}\\'
		db_directory = fp+'webappsstore.sqlite'
		try:
			with sqlite3.connect(db_directory) as db:
				cur = db.cursor()
				statement = "SELECT value FROM webappsstore2 WHERE key='session_active_session';"
				results = cur.execute(statement).fetchall()
				auth = json.loads(results[0][0])['token']
			with open(fp+r'\prefs.js', 'r', encoding='utf-8') as f:fire_ver=re.search(r'appversion\", \"(.+)\"\);', f.read())[1]
			ua=f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{fire_ver}) Gecko/20100101 Firefox/{fire_ver}'
			save_changes('authorization_token', auth)
			save_changes('user_agent', ua)
		except IndexError:
			print(f'ERROR: Required token was not found in file; please browse fansly - while logged in with {compatible} - & execute again or enter data manually into config.ini')
			try:cur.close()
			except:pass
			s(60)
			exit()
		except sqlite3.OperationalError:
			if prf_c == len(myprofiles):
				print(f'ERROR: Required token was not found in profile directories, enter data manually into config.ini')
				try:cur.close()
				except:pass
				s(60)
				exit()
			elif prf_c < len(myprofiles):
				prf_c+=1
				pass


try:
	local_s=fp+r'\Local State'
	if compatible == 'Opera':login_d=fp+r'\Login Data'
	else:login_d=fp+r'\Default\Login Data'

	with open(local_s, 'r', encoding='utf-8') as f:local_state = json.loads(f.read())
	master_key = win32crypt.CryptUnprotectData(base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:], None, None, None, 0)[1]
	shutil.copy2(login_d, 'log_d.db')

	fansly_accs=set()
	try:
		with sqlite3.connect('log_d.db') as db:
			cur = db.cursor()
			results = cur.execute("SELECT username_value, password_value FROM logins WHERE origin_url or signon_realm LIKE '%fansly.%' or username_element='fansly_login'").fetchall()
		for r in results:
			username = r[0]
			crypt_p = r[1]
			decrypt_p = AES.new(master_key, AES.MODE_GCM, crypt_p[3:15]).decrypt(crypt_p[15:])[:-16].decode()
			# print(f'Username: {username}\nPassword: {decrypt_p}\n{"~"*30}')
			fansly_accs.add(f'{username}:{decrypt_p}')
		if len(fansly_accs) > 1:
			print(f'\nWarning: Found multiple ({len(fansly_accs)}) fansly accounts -> press "y" to use with fansly scraper, else press "n"')
			for x in list(fansly_accs):
				usr=x.split(':')[0]
				pw=x.split(':')[1]
				if len(fansly_accs) != 1:
					print(f'\tUse account "{usr}"?')
					while True:
						if keyboard.is_pressed('y'):
							inp = 'y'
							break
						elif keyboard.is_pressed('n'):
							fansly_accs.remove(x)
							inp = 'n'
							break
					if inp == 'y':
						fansly_accs.clear()
						fansly_accs.add(f'{usr}:{pw}')
						break
					s(.3)
		fns_acc=list(fansly_accs)[0]
		usr=fns_acc.split(':')[0]
		pw=fns_acc.split(':')[1]
		print(f'\nWill use "{usr}"!')
		# get device id
		ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
		headers = {
			'authority': 'apiv2.fansly.com',
			'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
			'accept': 'application/json, text/plain, */*',
			'sec-ch-ua-mobile': '?0',
			'user-agent': ua,
			'sec-ch-ua-platform': '"Windows"',
			'origin': 'https://fansly.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'referer': 'https://fansly.com/',
			'accept-language': 'en-US;q=0.8,en;q=0.7',
		}
		try:
			device_id=sess.get('https://apiv2.fansly.com/api/v1/device/id', headers=headers).json()['response']
		except:
			print('ERROR: Issue in device id request ...')
			print('\n'+traceback.format_exc())
			pass
		# send login request to get token
		headers = {
			'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
			'Accept': 'application/json, text/plain, */*',
			'Referer': 'https://fansly.com/',
			'Content-Type': 'application/json',
			'sec-ch-ua-mobile': '?0',
			'User-Agent': ua,
			'sec-ch-ua-platform': '"Windows"',
		}
		try:
			auth_req = json.loads(sess.post('https://apiv2.fansly.com/api/v1/login', headers=headers, data='{"username":"'+usr+'","password":"'+pw+'","deviceId":"'+device_id+'"}').text)
			if auth_req['success'] == True:
				auth = auth_req['response']['session']['token']
				if auth:
					save_changes('Authorization_Token', auth)
					save_changes('User_Agent', ua)
			else:
				print('ERROR: Something went wrong in auth_req\n')
				print(auth_req)
		except:
			print('ERROR: Issue in token request ...')
			print('\n'+traceback.format_exc())
			pass
	except IndexError:
		print(f'ERROR: Your fansly account was not found in your browsers login storage. Did you not allow your browser to save it?\nTrying a different method now ...')
		print('\n'+traceback.format_exc())
		pass
	except sqlite3.OperationalError:
		if prf_c == len(myprofiles):
			print(f'ERROR: Your entire browser login storage was not found\nTrying a different method now ...')
			cur.close()
		elif prf_c < len(myprofiles):
			prf_c+=1
			pass
	cur.close()
	db.close()
except Exception as e:
	print('\n'+traceback.format_exc())
	pass
try:os.remove('log_d.db')
except:pass

if compatible == 'Opera':
	print('Unfortunately, you will have to enter your data manually, please read the ReadMe > Manual part of the ReadMe file to know how to.')
	s(60)
	exit()
else:print('\n\n\t >>> Well that did not work as intended; but do not worry, we will try something else! <<<\n')

def modify_process(kill, pids=None):
	try:
		if pids is None:pids = []
		for p in pids:
			if kill == True:psutil.Process(p).terminate()
	except Exception:
		print('ERROR: Unexpected error in modify_process')
		print('\n'+traceback.format_exc())
		s(60)
		exit()

def proc_name(name):
	procs = []
	for p in psutil.process_iter(['name']):
		if p.info['name'] == name:
			procs.append(p.pid)
	return procs

def enumWindowsProc(hwnd, lParam):
	if (lParam is None) or ((lParam is not None) and win32process.GetWindowThreadProcessId(hwnd)[1] == lParam):
		text = win32gui.GetWindowText(hwnd)
		if text:
			win32api.SendMessage(hwnd, win32con.WM_CLOSE)

for process in psutil.process_iter():
	if process.name() == f'{compatible.lower()}.exe':
		win32gui.EnumWindows(enumWindowsProc, process.pid)
s(5) # Give browser time to close

count=0
for brws in [f'{compatible.lower()}.exe','chromium.exe']:
	pids=proc_name(brws)
	if pids:
		print(f'Process {brws} still running, after trying to gracefully end. Forcing {brws} to shutdown now.')
		modify_process(kill=True, pids=pids)
	elif not pids and count == 0:
		print(f'{compatible} was already closed or just got ended gracefully!')
		count+=1

required = set()
def interceptor(request):
	global auth, ua, regex
	if 'apiv2' in request.url:
		regex=re.search(r"authorization: (.+)\nuser-agent: (.+)", str(request.headers))
		if regex:
			auth = regex[1]
			ua = regex[2]
			for x in [auth,ua]:required.add(x)
		else:regex=False

opts = uc.ChromeOptions()
opts.headless = True
opts.add_argument(r'--user-data-dir='+fp)
driver = uc.Chrome(options=opts)
driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ['*png','*jpeg','*woff','*woff2','*jpg','*gif','*jpeg','*css','*mp4','*mkv']})
driver.execute_cdp_cmd('Network.enable', {})
driver.request_interceptor = interceptor
driver.get('https://fansly.com/')
itr=0
while True:
	if required:
		driver.quit()
		break
	if itr > 10 and regex == False:
		print(f'\nERROR: Required data not found with your browser {compatible};\nmake sure you actually browsed fansly, while logged into your account, with this browser before.')
		driver.quit()
		os.remove('chromedriver.exe')
		s(60)
		exit()
	s(.3)
	itr+=.3
try:os.remove('chromedriver.exe')
except:pass
save_changes('Authorization_Token', auth)
save_changes('User_Agent', ua)
