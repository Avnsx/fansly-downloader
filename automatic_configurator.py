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
	print(f'\nDetected Unsupported OS; {os_v} - please enter data manually into config.ini\n\nPlease read Get Started {get_started}\n\nTrying to open browser on Get Started')
	try:
		import webbrowser
		webbrowser.open(get_started, new=0, autoraise=True)
	except:
		print('Unfortunately that did not work, please navigate manually ...')
	s(180)
	exit()

import os
os.system('title Automatic Configurator')

import psutil,re,sqlite3,traceback,json,win32con,win32api,win32gui,win32process,win32crypt,requests,keyboard,shutil,base64
from seleniumwire.undetected_chromedriver import uc
from re import search
from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
from configparser import RawConfigParser
from Crypto.Cipher import AES
sess = requests.Session()

def exit():os._exit(0) # pyinstaller

try:
	uc_ver = uc.__version__
	if uc_ver > '3.0.6':
		print(f'\nERROR: Version missmatch! Your version({uc_ver}) of the python library "undetected chromedriver" is too high!\n\n!!! Please install undetected chromedriver version 3.0.6 to run this code, if you have pip installed: "pip install undetected_chromedriver==3.0.6" !!!\n\nYou could also just use the executable(.exe) version of "automatic_configurator.py", or manually configure "config.ini"')
		s(20)
		exit()

	print('Reading config.ini file ...')
	config = RawConfigParser()
	if len(config.read('config.ini')) != 1:
		print('config.ini file not found or can not be read. Please download it & make sure it is in the same directory as Fansly Scraper & auto_config')
		s(180)
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
		global ti, cur, db
		arg2=arg2.replace('Headless','')
		config.set('MyAccount', arg1, arg2)
		if ti == 1:
			with open('config.ini', 'w', encoding='utf-8') as configfile:config.write(configfile)
			print('Done! Now all you have to do is; write your Fansly content creators name into the config.ini file and you can start Fansly Scraper!')
			try:cur.close()
			except:pass
			try:db.close()
			except:pass
			try:os.remove('chromedriver.exe')
			except:pass
			try:os.remove('log_d.db')
			except:pass
			try:shutil.rmtree(selenium_wire_storage)
			except:pass
			s(180)
			exit()
		if ti == 0:
			print(f'\nFound required strings with {compatible}!\nAuthorization_Token = {auth}\nUser_Agent = {arg2}\n\nOverwriting config.ini ...')
			ti+=1

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
		s(180)
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
			print('\nERROR: Required files were not found at all, enter data manually into config.ini')
			s(180)
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
				s(180)
				exit()
			except sqlite3.OperationalError:
				if prf_c == len(myprofiles):
					print(f'\nERROR: Required token was not found in profile directories, enter data manually into config.ini')
					try:cur.close()
					except:pass
					s(180)
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
			ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
			headers = {
				'authority': 'apiv2.fansly.com',
				'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="97", "Google Chrome";v="97"',
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
				print('\nERROR: Issue in device id request ...')
				print('\n'+traceback.format_exc())
				pass
			# send login request to get token
			headers = {
				'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="97", "Google Chrome";v="97"',
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
						save_changes('user_agent', ua)
						save_changes('authorization_token', auth)
				else:
					print('\nERROR: Something went wrong in auth_req\n')
					print(auth_req)
			except:
				print('\nERROR: Issue in token request ...')
				print('\n'+traceback.format_exc())
				pass
		except IndexError:
			print(f'\nERROR: Your fansly account was not found in your browsers login storage.\nDid you not allow your browser to save your fansly login data?\n\nTrying a different method now ...')
			print('\n'+traceback.format_exc())
			pass
		except sqlite3.OperationalError:
			if prf_c == len(myprofiles):
				print(f'\nERROR: Your entire browser login storage was not found\nTrying a different method now ...')
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
		s(180)
		exit()
	else:print('\n\n\t >>> Well that did not work as intended; but do not worry, we will try something else! <<<\n')

	def modify_process(kill, pids=None):
		try:
			if pids is None:pids = []
			for p in pids:
				if kill == True:psutil.Process(p).terminate()
		except Exception:
			print('\nERROR: Unexpected error in modify_process')
			print('\n'+traceback.format_exc())
			s(180)
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
	opts.add_experimental_option('excludeSwitches', ['enable-logging'])
	opts.add_argument(r'--user-data-dir='+fp)

	app=ApplicationRunning('Automatic Configurator.exe')
	if app:
		selenium_wire_storage = os.path.join(os.getcwd(), 'temporal_data')
		selenium_wire_options = {'request_storage_base_dir': selenium_wire_storage}
		
		certs_dict = {'seleniumwire-ca.pem':'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZGekNDQXYrZ0F3SUJBZ0lVSVVjNmRubnFoWVgzWllYUXpwWnlKMWd0VXdjd0RRWUpLb1pJaHZjTkFRRUwKQlFBd0d6RVpNQmNHQTFVRUF3d1FVMlZzWlc1cGRXMGdWMmx5WlNCRFFUQWVGdzB4T0RBM01qQXhNRFF4TUROYQpGdzB5T0RBM01UY3hNRFF4TUROYU1Cc3hHVEFYQmdOVkJBTU1FRk5sYkdWdWFYVnRJRmRwY21VZ1EwRXdnZ0lpCk1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQ0R3QXdnZ0lLQW9JQ0FRREtLcG0xNEFIaUpiNG9uR0VTNEVjaHMycUIKWHNmZU1BYnNBN3g0YmxKa01HeUhHeDlCOE9wWHFsUnRjTm5XRDJKR25qYzAvazkydXVaYVYycHJEblp3SDVKbApuSlNadUdFelVVQW5yd2hUSFRxTWhNOXBmVDhScGx0RTBseXBsUW5pOHJqSDVvc2hCcnp6QUhJTG0vaUFtMVdJCkhDRlVDbFFhSjdzVlZ6QWlrYVBmZzRXVVhMSFA3L0FqeEllanAvU1ZJOFljbjFCUElsRHdwMXBJcTRXYXdKb1oKVFo3NUd3dnNUMW9oSDRZU1JNK0J4d0J1QlVxanVzYVlKaVd3cG5SODAxWFYyOTBpMy9iQk9rUzJmRWE0K2NpUwpMRUdFaTRTYWFDNk5oYXAzc2Q4MG5wSlVRZmY0bHRWR2F4WDBqQ0cvenN3ZjJYR0VEdHN3MkZGODQ4S2VQajRYCklsZ200eGN1aGhCdmNzZ29iL2J3RXZEVHJYUGszOFlRRUpFS0g4dUdmMzdBT3YyVFFtcWo0NVdadDdqU1oyWUgKWkduNFJ1bkpBTy9KN3RvcUo3dXBqeDY2UHE4V2tYUTZmYVNlVE5FTm1YY2xZUFJRRnVqVmJGa0VDUmNPdFM2VwpmVWtITSt0Z1hIS3FTTWNmVlZwNDZvLzRIZkh6b1R5dnJVRHJ5SEpCM2gvSXJxV0sxNDMzcllwM2JKemtwak05CkpUNzF2aDZzRG8vWXMrNEhLNXJ3cndrZVA3Yis2ZFV4MW5IT2dQWDg4bmpWSTZjdXhuamV4NkFmU2xkNWQ0QkgKWVpkdmlYUnFDeHBpdWRtbk4rY01LQWRKZ1JaRm1WTkgvZGpRcXRxM3kvZ21qd0tueVc5NXkzdUp1NFh6NStSNAo5amhBWkdKRmlISy92RStYd3dJREFRQUJvMU13VVRBZEJnTlZIUTRFRmdRVVB2clR5ZFNsWWhNUUp5OGx2QnZoCm5MZVFzdlF3SHdZRFZSMGpCQmd3Rm9BVVB2clR5ZFNsWWhNUUp5OGx2QnZobkxlUXN2UXdEd1lEVlIwVEFRSC8KQkFVd0F3RUIvekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBbUl2YWROdEZjYTl2dU11U2V3U1hIbE9kOXA3ZAo5eFlrcDhZajVSdkZVR0wzMnpZVWF0SDlZc1JoNUs5V3o1amlmandCTE1SRFpJbTQ4eGh4WWpxVnZUWm9RcEw2ClF5emJ1MkVzUkNibVErODYxVTRTZmNQMnVldEp1Rk02VWcwL0NLdml5TnBVYVgvOFlXdXBGWHNFaUNSSk05cGsKc2gyYitkcWxqeTlrdnJPb3NmZWh6OENSYnhVZmdQc0wySVZaYTBtSHN1T1pEYS9YSEFBVzluczVUZEJsRkh3bwpXLzJLRHZ2UEdMLzN0N1phaDJqd3U4RDh3Mzk3bG9vTVh4cXlUL0RBakg2K2JkNUtnLzdtRUxhcWJnL3BNM0VKCm1FTmQ1QnV0QmtocFZieUFLTG43VHZwWllTRUYvVk1OUGNaSE9Lb0tyeDF1dFp3TEZ1VkliMDdXRE1Sb3YwR08KaGcvcnJJQld2QTF5U2kvNHlyblJEYzdHQkhTVWgwS3J4NkxMWi9adEUzajcvNHJ3ajUxTXdxcU5oUXJDeEdoegprc3FuOFY2WFk3VVVLbmxUbEFXUnl1QkxpQSt5dmY5R2RnTkp4VWJsWllNTnBQYmVMd2UyQmUvdXRST3VNcXdyCkc0UkExc2ZQdUVkeWZkWEIvN2M4VmlPUHhLWUZIMFBPWHV3QitaMUpsWER0UjhyYmp5VlBVd3FRYXJBdU5JYncKTkM4UCtHV1N6dmlHNTQ0QlF5VzF4S3FMZ1FjRU1TVTczaWNET09iOUNPY2wxaDdVUlNPOVdCNkNaWHlrcFFTawpoY2VEaXdvakNEc3lNODR1WHl5WEtYQ1JQdHNlQ0lSc0Exelp3clhVN05EREJYcklDN21vVmJ4a0R1Mkc0VjFnCmI1SkZZZTRGTkkweXcvbz0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQoKLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUpRd0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQ1Mwd2dna3BBZ0VBQW9JQ0FRREtLcG0xNEFIaUpiNG8KbkdFUzRFY2hzMnFCWHNmZU1BYnNBN3g0YmxKa01HeUhHeDlCOE9wWHFsUnRjTm5XRDJKR25qYzAvazkydXVaYQpWMnByRG5ad0g1SmxuSlNadUdFelVVQW5yd2hUSFRxTWhNOXBmVDhScGx0RTBseXBsUW5pOHJqSDVvc2hCcnp6CkFISUxtL2lBbTFXSUhDRlVDbFFhSjdzVlZ6QWlrYVBmZzRXVVhMSFA3L0FqeEllanAvU1ZJOFljbjFCUElsRHcKcDFwSXE0V2F3Sm9aVFo3NUd3dnNUMW9oSDRZU1JNK0J4d0J1QlVxanVzYVlKaVd3cG5SODAxWFYyOTBpMy9iQgpPa1MyZkVhNCtjaVNMRUdFaTRTYWFDNk5oYXAzc2Q4MG5wSlVRZmY0bHRWR2F4WDBqQ0cvenN3ZjJYR0VEdHN3CjJGRjg0OEtlUGo0WElsZ200eGN1aGhCdmNzZ29iL2J3RXZEVHJYUGszOFlRRUpFS0g4dUdmMzdBT3YyVFFtcWoKNDVXWnQ3alNaMllIWkduNFJ1bkpBTy9KN3RvcUo3dXBqeDY2UHE4V2tYUTZmYVNlVE5FTm1YY2xZUFJRRnVqVgpiRmtFQ1JjT3RTNldmVWtITSt0Z1hIS3FTTWNmVlZwNDZvLzRIZkh6b1R5dnJVRHJ5SEpCM2gvSXJxV0sxNDMzCnJZcDNiSnprcGpNOUpUNzF2aDZzRG8vWXMrNEhLNXJ3cndrZVA3Yis2ZFV4MW5IT2dQWDg4bmpWSTZjdXhuamUKeDZBZlNsZDVkNEJIWVpkdmlYUnFDeHBpdWRtbk4rY01LQWRKZ1JaRm1WTkgvZGpRcXRxM3kvZ21qd0tueVc5NQp5M3VKdTRYejUrUjQ5amhBWkdKRmlISy92RStYd3dJREFRQUJBb0lDQVFDdmZ0bWVTNDMyL2VLY0tGd1FZY2I5CjExemVYeVBMbWc5NE5Db1l0VlFxaXVxN1FlMFpkZ1JJQTZGMHU2RXVOSDZRWk9ueHc4M0JlSzljdjBPdkdZZncKLzBjN2svaGZsUEl6OVJWbkhZZHhkdzhMU29NdXhMM0tHWXBqTE9XcGhLcG5hMkxDalR3N2VEandEWFB5NWZ1TAowTXduOHB0djgrTmNMUjgzZ0U5Vnd1M3BxcWQ3eWhmRk5UbFdJMVhIMkpYMkhXN3VDOUpRVDY3SnFjMHpCa3BkCnMxSlNJdEtjMWtDOGE0b0c5UEdTekU4Q0Rua3VDTVBwYThyWDYwMk9rb0RPbHpxTkFtWnR6dFBLbTBWbzBHc28KU2hVMTV0c2RMMnYyQ2ZoWGZEQWw1YStvWXZzTno1SnVKcW1Qam9ncG1MZjNaSkpJRjU5MkR0dHlCR2FBcnNxUwp2Z0VEREFGRGhNWEY4cTNEN0RPRWpYOU5tYzByQjdUaFd6ck9rOVFIOEVURWo4Ly9EemNaWGMrdUdYdkxmbnNrCmxWM3Qvd2l5Q2dxQ0lhbmxJbHVPQnkyWGtIZ25sUHlzWFB2Nzc3MFg2b1lPb09Cb1pYNzBZTHdSQXBQMnNFRUUKbVpBWDZJVFBLYkl2K2QwQ0czSEdIajR2U2l2S1ZBT3htUTRGakV0czFLV2xhV3JORkltczNzQVpTRkovb1dvYQpQMURzOHJXYUJPRThzOUhWQTVsTjN2WG4zNk13MWNHNlFYZnhJWFdmSC9IelNIamJrTjE1V2FnNzIyZ2d5OEV2Cm5xTnJsbmtWQVQ5VDFFQ3hxSmxpZlpnZ0NHcDZXMng0bnlLL05aVU4rU3VjTFFxamU0bU9HcmlDeGRZaXJNaHoKWk10Zjd2TGVsWFhqK0F2eU5VWTdtUUtDQVFFQTgxWjV2ZFJEeWJEdVNjV1ptK3FjV3VMQW5pN3hzK0wzUGJlUwpxWVpXWjdHNEo2U3BUYnVPZHRScUMxR1VaYXord3UxZ0ozNmZldE9VUzRvQmNZSGRwZ1padjBmTkVvYUw2eEpjCnpvWS9aMmFiRU9XbnFZUDRZaDA2bVRFdk1CVFJIMUliZ1BrNlYzT1FnN3lwRFJ2aGNCSXhKRSt1ZVJkZ3EyWnAKeDh0eFNLaVRndFhsVGlpeXBWWkNEcHJHdGdEU0NaSllzMUljWXVUMFRvcnA1emlXZmVIWUJLTzBWcVZEWXVRWgpRR3piZWRxR3RTanNWcVYyR0xuWEtVcytiMVhpUlVBSy9qVVNvdWRmWm9tVWZwb0JSWlpyRGkyVnZ4bXkzWEsrClR2VkJVTFZFYk1mcy9HUGNOUHgveWlZQzhpQ2U5YTJOZSs0azZsS0Vsc1FDNHFrM25RS0NBUUVBMUsrdFduejMKOEJKVzI5QU0xMGNGRjM3ejFUUU1lZkpmTWVBQjUvN0t3Y2JhTk9VSzhETTNWbmxWT3VPVzV3QlZlQ2VXVDB4TApvY05xek9DcVh3RUNaVWV1K1Z4Y0dndWVuZ0xUU1VQSXFweXphcmRkYlJyQm4reFFzaml2eGNoRDc4RjcyZThzCkdRK3FMSGRuUE4zTW82YWlqVzFIZlVxS2FFR0hRVVlMa3M1MGcvVUlXSlA4UGc2TGVsOGpTdjlTa2hFTXJOZngKclAveEdhWW5VTXVnY0VyVlM5R0FpQVRTakNFVE4wV2ZiN0pSVisyVENRVlVUT0o2SlRXcGZweDVJam9SOGo4VgpBVm0zVkkrT0Z1bUxKQ0U5SGVPU1F1NGJJNXd2RGhjM0xtL1JYdE1oUndBY09GdDJkY1NHcmRmQXRpZ0RXMXFnCjJiSEJOdDlVaXdiZTN3S0NBUUJqeWtiS3JrM09YSnliN0VqK1E4d3pDV0pzZkZ2cXBWMDNGaDB6SUVBMjdnN1QKVXhlTEpTdGJWK2pWRTNPRDd0bmJIbldjUExVeUxhcFhBQlZ2Y3c1dWs1UWllVk9FRVdFMzJhUHRuZWhLZ3kxOApWSEhaZHFGWnV4cll6KzdHRFFObGtNcHVyY1piTHExSkdRbEtzdkJVZ1dGZHZyK1NNU0FYcWp3ZkR6TTUxTWdKCms2WWgwMWJQcnZ3UCtURWNXbUhJUXhmVkVndEtFeEtOVXpKdy9DZmJIODd5dUIrd21MMTF4STBHZXAzVzd1TG4KVUF6N3k0Y094TWVUeTZPakRObHFCTVY5VWs1K045eEx0SWdORXlNS1lwRXNrMDBodld3NG5HR25CN1R0WUNqYgpZM0d3WDFOaTkxbUFrTzRNVll4YXUvMlZvU2ZLWUdTM1gxSy9tUjJSQW9JQkFRQ3RXMHduVjNrWU96cUZESDJLCjh4NVpXbWNRdnMzMGovTzd5V1NFWG8rUmhxM1JNMmZKQlZYenJBNG1ZOTlhQmxHa0VGQlo3a3d2WEFNdlgyZysKNjZteU44Mk0veFVyUFpGYUpkOWw5bFFYaklaSlU1QlpIOWYyckQzU0pwWk8xYjlhS3hEeVFCcG5pdmNnSzJzQQpsNkQzT3hsL3dUVG1FTjNqd0pXb1JKbW1YWlZuQVZCK01wRUZYQUdnQ3UvUGIzRTBFYVdOTks2T1hrZDhxb3VkCk5YeGVTd0MwUGQxUUFPNUV2YWpXQW0vRU1VcFFLeHNQM1VJck1PWnljZHpua0U3RDhTVXptT3RjSUc1b0JHTEMKbGpXTmkzSXZiSkNJOFY4NWxWSmRYOXJnaE0vWlJLbjVIMFBoUTl1NGZpbHdoVTFVckNTZ1Q2eVFCRzBDZHVLSQpOMTl0QW9JQkFHOU5tbUtDbjVvWGMyK29jdXBrUElXdmlPKythNU1jczNGNlkzdzdYenlEMkVST3RLWXg1WkJWCi9ZNGtZd2hab1BPenlVR0t6TXorTWdFenZlcFFVK2l2VTN6UU9kSGRjSXA0Q0tJOXZiM2QvK3Z4Nk5JWGRzb0EKbjV0UGV1U2RjeVlZSXpPZmo4UXcxUlhrT2RnS0xXT2l6WWpJV0xtZnBKZ1c5VTZTcGx1NEZMQ2grSFpuQ3EzagpBUE5CZE5iTVFoNWhuUW1LdjFqVzZPSG9MbHczcG1UQjhHcVMvcGN4ZlJpSERDb3p4b21kOC9VTnFnckFEWE9jClpYaDhqWVNib1FLNU94MElsTmI2eVR6cWIxWXdyaWpDejgvNVhyQmtGd3R6L1N2VHpjd282T0xiZzdFaUtYaFAKTTRBU1lnamwzYjRlYjRlakVwOXlsYk1KL0k3RzBtVT0KLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLQo='}
		destination_dir = os.path.join(selenium_wire_storage,'.seleniumwire')
		os.makedirs(name=destination_dir, exist_ok=True)
		for file_name, cert_string in certs_dict.items():
			destination_path = os.path.join(destination_dir, file_name)
			with open(destination_path, 'w', encoding='utf-8') as destination_cert_file:destination_cert_file.write(str(base64.b64decode(cert_string).decode('utf-8')))
			print('Cert copied')

		driver = uc.Chrome(options=opts, seleniumwire_options=selenium_wire_options)
	else:
		driver = uc.Chrome(options=opts)

	driver.request_interceptor = interceptor
	driver.get('https://fansly.com/')
	itr=0
	while True:
		if required:
			try:driver.quit()
			except:pass
			break
		if itr > 10 and regex == False:
			print(f'\nERROR: Required data not found with your browser {compatible};\nmake sure you actually browsed fansly, while logged into your account, with this browser before.')
			try:driver.close()
			except:pass
			try:driver.quit()
			except:pass
			try:os.remove('chromedriver.exe')
			except:pass
			s(180)
			exit()
		s(.3)
		itr+=.3
	save_changes('user_agent', ua)
	save_changes('authorization_token', auth)
except:
	print('\nERROR: General Exception')
	print('\n'+traceback.format_exc())
	s(180)
	exit()
