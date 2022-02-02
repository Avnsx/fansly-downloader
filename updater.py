import requests,re,time,os,traceback,subprocess,platform,sys
from shutil import unpack_archive
import dateutil.parser as dp
from time import sleep as s
from configparser import RawConfigParser
from tkinter import Tk
from tkinter.messagebox import askyesno, showinfo, showerror

def exit():sys.exit(0) # pyinstaller

plat = platform.system()
config = RawConfigParser()

existed_before = False
if len(config.read('config.ini')) == 1:
	existed_before = True

if config.has_option('Other', 'version') == False:
	config.add_section('Other')
	config.set('Other', 'version', '0.2')
	cur_ver='0.2'

cur_ver = config['Other']['version']
title ='Avnsx/fansly - Updater'
resp = requests.get('https://api.github.com/repos/avnsx/fansly/releases/latest', headers={'user-agent': title, 'referer':title, 'accept-language': 'en-US,en;q=0.9',})
js = resp.json()

error = False
while True:
	try:
		d=dp.isoparse(js['created_at']).replace(tzinfo=None)
		parsed = f"{d.strftime('%d')} {d.strftime('%B')[:3]} {d.strftime('%Y')}"
		d_version=js['tag_name'].lstrip('v')
		config.set('Other', 'version', d_version)
		d_name=js['name']
		try:
			change_log = f'\n\nChangelog v{d_version}\n'+re.search(r"```(.*)```", js['body'], re.DOTALL)[1].replace('\n','')
		except TypeError:
			change_log = ''
			pass
		try:
			d_url=js['assets'][0]['browser_download_url']
			d_count=js['assets'][0]['download_count']
		except IndexError:
			msg=f'ERROR: Currently no download is linked for version {d_version}'
			error = True
		break
	except KeyError:
		if re.search('rate limit', str(js)):
			seconds_left=int(resp.headers['X-RateLimit-Reset'])-round(time.time())
			minutes_left=round(seconds_left/60)
			msg=f'ERROR: Got rate limited; please wait {minutes_left} minutes & try again, manually update or switch your IP'
			error = True
		else:
			msg=f'ERROR: GitHub API responded unexpectedly\n\n{resp.text}'
			error = True
		break
	except:
		msg=traceback.format_exc()
		error = True
		break

root = Tk()
root.withdraw()
root.attributes('-topmost', True)

if os.path.isfile('old_updater.exe'):
	s(3)
	os.remove('old_updater.exe')
	root.lift()
	showinfo(title, f'Successfully updated to version {d_version}{change_log}', parent=root)
	exit()

if error == False:
	if cur_ver < d_version:msg = f'  Your version: {cur_ver}\n\n  Latest Build:\n{5*" "}Name: {d_name}\n{5*" "}Version: {d_version}\n{5*" "}Published: {parsed}\n{5*" "}Download count: {d_count}\n\n►  Would you like to update your current version?'
	else:msg = f'  Your version: {cur_ver}\n\n  Latest Build:\n{5*" "}Name: {d_name}\n{5*" "}Version: {d_version}\n{5*" "}Published: {parsed}\n{5*" "}Download count: {d_count}\n\n►  You are already on the newest version!\n►  Do you still want to update?'
	root.lift()
	choice = askyesno(title, msg, parent=root)
	if choice == True:
		with open('update.zip', 'wb') as f:f.write(requests.get(d_url, allow_redirects=True, headers={'user-agent': title, 'referer':title, 'accept-language': 'en-US,en;q=0.9',}).content)
		try:os.rename('updater.exe', 'old_updater.exe')
		except FileNotFoundError:pass
		unpack_archive('update.zip')
		os.remove('update.zip')

		if existed_before == True:
			new_config=RawConfigParser()
			new_config.read('config.ini')

			for each_section in new_config.sections():
				for (each_key, each_val) in new_config.items(each_section):
					try:
						config[each_section][each_key]
					except KeyError:
						config.set(each_section,each_key,each_val)
						pass
			with open('config.ini', 'w', encoding='utf-8') as f:config.write(f)

		try:
			if plat == 'Windows':os.startfile('updater.exe')
			elif plat == 'Linux':subprocess.Popen(['xdg-open', 'updater.exe'])
			elif plat == 'Darwin':subprocess.Popen(['open', 'updater.exe'])
		except FileNotFoundError:pass

	root.destroy()
else:
	root.lift()
	choice = showerror(title, msg, parent=root)
	root.destroy()

