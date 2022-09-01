"""
this would've been way easier if leveldb / plyvel were scalable compatible
if you want to help this project; creating working windows builds of plyvel would be nice
github.com/wbolster/plyvel/issues/137

please do not use the code provided for malicious purposes
"""

import platform
from time import sleep as s

os_v=platform.system()
get_started='https://github.com/Avnsx/fansly/wiki/Get-Started'
if os_v == 'Windows':print('\nDetected Supported OS; Windows')
else:
	print(f'\nERROR: Detected unsupported OS; {os_v} - please enter data manually into config.ini\n\nPlease read the manual Tutorial called "Get Started"\n\nTrying to navigate the local browser to the fansly scraper wiki ...')
	s(5)
	try:
		import webbrowser
		webbrowser.open(get_started, new=0, autoraise=True)
	except:
		print(f'ERROR: Unfortunately that did not work -> please navigate manually to {get_started} ...')
	input()
	exit()

import os
os.system('title Automatic Configurator')

import psutil,re,sqlite3,traceback,json,win32con,win32api,win32gui,win32process,win32crypt,requests,keyboard,shutil,base64
import undetected_chromedriver.v2 as uc
from re import search
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
from configparser import RawConfigParser
from Crypto.Cipher import AES
sess = requests.Session()

if uc.__version__ < '3.1.5':
	input(f'WARNING: Possible module versioning missmatch found for "undetected_chromedriver"\nRequired is version 3.1.5 or above, but you have version {uc.__version__}\nPlease make sure to upgrade with "pip install --upgrade undetected_chromedriver"\n\nYou can skip this warning by pressing Enter; but the configurator will most likely not work as expected')

def exit():os._exit(0) # thanks pyinstaller

try:
	print('Reading config.ini file ...')
	config = RawConfigParser()
	if len(config.read('config.ini')) != 1:
		print('config.ini file not found or can not be read. Please download it & make sure it is in the same directory as Fansly Scraper & Automatic Configurator')
		input()
		exit()

	def ApplicationRunning(processName):
		for proc in psutil.process_iter():
			try:
				if processName.lower() in proc.name().lower():
					print('Running compiled')
					return True
			except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):pass
		print('Running in py env')
		return False

	ti=0
	def save_changes(arg1, arg2):
		global ti, cur, db, driver
		arg2=arg2.replace('Headless','')
		if arg1 == 'authorization_token':
			c,s='',7
			for x in range(s):
			    for y in range(x,len(arg2),s):c+=arg2[y]
			arg2=c+'fNs'
		config.set('MyAccount', arg1, arg2)
		if ti == 1:
			with open('config.ini', 'w', encoding='utf-8') as configfile:config.write(configfile)
			print('Finished!\n\nNow just write your Fansly content creators name into the config.ini file, afterwards you can start Fansly Scraper!')
			try:cur.close()
			except:pass
			try:db.close()
			except:pass
			try:os.remove('chromedriver.exe')
			except:pass
			try:os.remove('log_d.db')
			except:pass
			try:driver.close()
			except:pass
			try:driver.quit()
			except:pass
			input()
			exit()
		if ti == 0:
			print(f'\nINFO: Successfully found required strings with {compatible}!\n\nOverwriting config.ini ...')
			ti+=1

	print('Reading default browser from registry ...')
	with OpenKey(HKEY_CURRENT_USER, r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice') as key:used_browser=QueryValueEx(key, 'ProgId')[0] # win only

	compatible = None
	for x in ['Firefox','Brave','Opera GX','Opera','Chrome','MSEdge']:
		if search(x, used_browser):
			compatible=x
			break
	if search('App', used_browser):compatible='MSEdge'

	if compatible:print(f'Good News! Your default browser is {compatible} -> a compatible browser for automatic configuration!')
	elif not compatible:
		print(f'Your browser ({used_browser}) is not supported, please enter data manually into config.ini')
		input()
		exit()

	if compatible == 'Chrome':
		fp=os.getenv('localappdata')+r'\Google\Chrome\User Data'
	elif compatible == 'MSEdge':
		fp=os.getenv('localappdata')+r'\Microsoft\Edge\User Data'
	elif compatible == 'Brave':
		fp=os.getenv('localappdata')+r'\BraveSoftware\Brave-Browser\User Data'
	elif compatible == 'Opera':
		fp=os.getenv('appdata')+r'\Opera Software\Opera Stable'
	elif compatible == 'Opera GX':
		fp=os.getenv('appdata')+r'\Opera Software\Opera GX Stable'
	elif compatible == 'Firefox':
		bp = os.getenv('appdata')+r'\Mozilla\Firefox\Profiles'
		myprofiles=[]
		for file in os.listdir(bp):myprofiles.append(os.path.join(file))
		if len(myprofiles) == 0:
			print('\nERROR: Required files were not found at all, enter data manually into config.ini')
			input()
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
				save_changes('user_agent', ua)
				save_changes('authorization_token', auth)
			except IndexError:
				print(f'\nERROR: Required token was not found in file; please browse fansly - while logged in with {compatible} - & execute again or enter data manually into config.ini')
				try:cur.close()
				except:pass
				input()
				exit()
			except sqlite3.OperationalError:
				if prf_c == len(myprofiles):
					print(f'\nERROR: Required token was not found in profile directories, enter data manually into config.ini')
					try:cur.close()
					except:pass
					input()
					exit()
				elif prf_c < len(myprofiles):
					prf_c+=1
					pass

	# method 1: get info through a direct api request request
	try:
		local_s=fp+r'\Local State'
		if compatible == 'Opera' or compatible == 'Opera GX':login_d=fp+r'\Login Data'
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
			ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
			fns_headers = {
				'authority': 'apiv3.fansly.com',
    			'accept': 'application/json, text/plain, */*',
    			'accept-language': 'en-US;q=0.8,en;q=0.7',
    			'cache-control': 'max-age=0',
    			'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="104", "Chromium";v="104"',
    			'sec-ch-ua-mobile': '?0',
    			'sec-ch-ua-platform': '"Windows"',
    			'sec-fetch-dest': 'empty',
    			'sec-fetch-mode': 'cors',
    			'sec-fetch-site': 'same-site',
    			'sec-fetch-user': '?1',
    			'upgrade-insecure-requests': '1',
    			'user-agent': ua,
    			'origin': 'https://fansly.com/',
    			'referer': 'https://fansly.com/',
			}
			device_id=sess.get('https://apiv3.fansly.com/api/v1/device/id', headers=fns_headers).json()['response'] # get random ua string
			# send login request to get token
			auth_req = sess.post('https://apiv3.fansly.com/api/v1/login', headers=fns_headers, json={"username":usr, "password": pw, "deviceId": device_id}).json()
			if auth_req['success']:
				auth = None
				try:
					# if account has two factor disabled
					auth = auth_req['response']['session']['token']
				except KeyError:
					"""
					if the fansly account has two factor enabled -> the immediately responded token is just a temporary one 
					a request to "/login/twofa" with the temp auth token including the twofa string as a payload called "code" would be required to generate
					the correct token; so instead we just 'error out' and have our second method get the job done
					auth = auth_req['response']['twofa']['token']
					"""
					print(f'ERROR: Two factor authentication is enabled for the fansly account; method 1 failed')
				if auth:
					save_changes('user_agent', ua)
					save_changes('authorization_token', auth)
			else:
				print('\nERROR: Something went wrong in auth_req\n')
				print(auth_req)
		except IndexError:
			print(f'\nERROR: Your fansly account was not found in your browsers login storage.\nDid you not allow your browser to save your fansly login data?\n\nTrying a different method now ...')
			print('\n'+traceback.format_exc())
		except sqlite3.OperationalError:
			if prf_c == len(myprofiles):
				print(f'\nERROR: Your entire browser login storage was not found\nTrying a different method now ...')
				cur.close()
			elif prf_c < len(myprofiles):
				prf_c+=1
		cur.close()
		db.close()
	except Exception as e:
		print(f'ERROR: Issue in first fetching method: {e}')
		print('\n'+traceback.format_exc())
	try:os.remove('log_d.db')
	except:pass

	# github.com/ultrafunkamsterdam/undetected-chromedriver/issues/803
	if compatible == 'Opera' or compatible == 'Opera GX':
		print('Unfortunately, you will have to enter your data manually, please read the "Get-Started" tutorial')
		input()
		exit()

	print('\n\n\t >>> Well that did not work as intended; but do not worry, we will try something else! <<<\n')

	###############################################################
	# method 2: imitate browser & get auth token through intercepting the request

	def modify_process(kill, pids=None):
		try:
			if pids is None:pids = []
			for p in pids:
				if kill == True:psutil.Process(p).terminate()
		except Exception:
			print('\nERROR: Unexpected error in modify_process')
			print('\n'+traceback.format_exc())
			input()
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

	options = uc.ChromeOptions()
	options.headless = True
	options.add_argument(fr'--disable-extensions')
	options.add_argument(f'--user-data-dir={fp}')

	try:
		with open(f'{fp}/Last Version', 'r', encoding='utf-8') as f:ver_main = f.read().split('.')[0]
		driver = uc.Chrome(options=options, enable_cdp_events=True, use_subprocess=True, version_main=ver_main)
	except:
		driver = uc.Chrome(options=options, enable_cdp_events=True, use_subprocess=True)

	auth, ua = None, None
	def interceptor(events):
	    global auth, ua
	    try:ua = events['params']['request']['headers']['User-Agent']
	    except:pass
	    try:auth = events['params']['request']['headers']['authorization']
	    except:pass
	
	driver.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*png','*woff2','*woff','*jpg','*jpeg','*mp4','*mov','*webm','*wmv','*flv','*mkv']}) # disable media so it loads quicker
	driver.add_cdp_listener('Network.requestWillBeSent', interceptor) # https://chromedevtools.github.io/devtools-protocol/tot/Network/#type-Headers
	driver.execute_cdp_cmd('Network.enable', {})
	
	driver.get('https://fansly.com/home')
	
	# wait for them to load up
	wait_t = 60
	for i in range(wait_t):
		if i % 20 == 0:
			print(f'Please wait, attemping method 2 ... [Timeout in: {wait_t-i} seconds]')
		if all([ua, auth]):
			driver.execute_cdp_cmd('Network.disable', {})
			save_changes('user_agent', ua)
			save_changes('authorization_token', auth)
			exit()
		s(1)
	# if that fails we just exit here
	print(f'\nERROR: Required data inside your browser {compatible}; cannot be accessed with automatic configurator!\n\nPlease read the manual Tutorial called "Get Started"\n\nTrying to navigate the local browser to the fansly scraper wiki ...')
	s(5)
	try:
		import webbrowser
		webbrowser.open(get_started, new=0, autoraise=True)
		print(f'INFO: Successfully navigated to the manual set up tutorial, please read it to understand how to be able to use fansly scraper')
		s(15)
		exit()
	except:
		print(f'ERROR: Unfortunately that did not work -> please navigate manually to {get_started} ...')
	input()
	exit()
except:
	print('\nERROR: General Exception')
	print('\n'+traceback.format_exc())
	input()
