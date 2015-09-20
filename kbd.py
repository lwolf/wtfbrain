#!/usr/bin/python3

# ----------------------------------------------------------------------------
# Constantin S. Pan <kvapen@gmail.com> wrote this file. As long as you retain
# this notice you can do whatever you want with this stuff. If we meet some
# day, and you think this stuff is worth it, you can buy me a can of Coke in
# return.
# 	Constantin S. Pan
# ----------------------------------------------------------------------------

import pyudev
from datetime import datetime
from dateutil.tz import tzlocal
from os.path import expanduser
import shlex
import subprocess
import time
import json

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='input')

def uniq_keyboard(device):
	return device.get('ID_INPUT_KEYBOARD') == '1' and device.get('UNIQ') == '""'

def isotime():
	return datetime.now(tzlocal()).strftime("%F %T %Z")

def get_config():
	filename = expanduser("~/.wtfbrain.json")
	with open(filename) as f:
		config = json.load(f)
	return config

def notify(summary, body, timeout):
	args = [
		'notify-send', summary, body,
		'-t', str(timeout * 1000),
	]
	subprocess.check_call(args)

def set_xkbmap(xkbmap):
	try:
		args = ['setxkbmap']
		for k, v in xkbmap.items():
			args.append("-" + k)
			args.append(v)
		cmd = ' '.join(shlex.quote(x) for x in args)
		print(cmd)
		subprocess.check_call(args)
		print('xkbmap set')
		return True
	except subprocess.CalledProcessError:
		print('command failed: ' + cmd)
		return False

def set_rate(rate):
	try:
		first_delay, delay = rate
		args = [
			'xset', 'r', 'rate',
			str(first_delay),
			str(delay),
		]
		cmd = ' '.join(shlex.quote(x) for x in args)
		print(cmd)
		subprocess.check_call(args)
		print('rate set')
		return True
	except subprocess.CalledProcessError:
		print('command failed: ' + cmd)
		return False

def main():
	config = get_config()

	set_rate(config['rate'])
	set_xkbmap(config['xkbmap'])

	while True:
		try:
			for action, device in monitor:
				if action == 'add' and uniq_keyboard(device):
					notify(
						'A keyboard attached',
						'{0}:{1}'.format(
							device.get('ID_VENDOR', 'no-vendor'),
							device.get('ID_MODEL', 'no-model'),
						) + '\nReconfiguring xkbmap and rate',
						2,
					)
					print("[{0}] {1}:{2} {3}'".format(
						isotime(),
						device.get('ID_VENDOR', 'no-vendor'),
						device.get('ID_MODEL', 'no-model'),
						device.sys_path,
					))
					time.sleep(2)
					set_rate(config['rate'])
					set_xkbmap(config['xkbmap'])
		except KeyboardInterrupt:
			print("dying")
			return
		except:
			print("recovering from interruption")

if __name__ == '__main__':
	main()