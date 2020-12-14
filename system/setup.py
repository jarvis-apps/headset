#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import sys, os, hashlib, apt, re
from getpass import getpass

def install(token_file):
	global INSTALL_DIRECTORY
	if get_python_version() != 3:
		print("You need to run this script with python3")
		exit(1)
	if not is_root():
		print("You need to be root!")
		exit(1)

	do_action("updating system", "sudo apt update ; sudo apt upgrade -y")
	do_action("installing utilities", "sudo apt install -y alsa-utils bluez bluez-tools pulseaudio-module-bluetooth python-gobject python-gobject-2 ofono python3-dbus libbluetooth-dev")
	do_action("adding pi to 'lp' group", "sudo usermod -a -G lp pi")
	do_action("installing bluetooth packages", "sudo apt install -y python-dbus python-pip ; pip install tcpbridge bluetool")

	# setup bluetooth sound
	with open("/etc/bluetooth/audio.conf", "w") as f:
		f.write("[General]\nClass = 0x20041C\nEnable = Source,Sink,Media,Socket\n")

	regex_replace_in_file("/etc/bluetooth/main.conf", "[#]?Name =.+", "Name = Jarvis")
	regex_replace_in_file("/etc/bluetooth/main.conf", "[#]?Class =.+", "Class = 0x20041C")
	do_action("modify bluetooth configuration", "true")

	print("Jarvis headset successfully set up!")
	print("Connect your device either with bluetoothctl or in the web dashboard (if it's installed)")
	exit(0)
	



def do_action(print_str, shell_command, show_output=True, on_fail="failed!", on_success="done!", exit_on_fail=True):
	print(print_str + "... ", end="")

	if not show_output:
		shell_command += " &> /dev/null"

	if not os.system(shell_command) == 0:
		print(on_fail)
		if exit_on_fail:
			exit(1)
	else:
		print(on_success)

def regex_replace_in_file(file_path, from_regex, to_string):
	contents = None
	with open(file_path, "r") as f:
		contents = f.read()
	
	if contents is None:
		return False
	
	new_contents = re.sub(from_regex, to_string, contents, flags = re.M)
	
	with open(file_path, "w") as f:
		f.write(new_contents)
	
	return True



def is_root():
	return os.geteuid() == 0

def get_python_version():
	# (2, 5, 2, 'final', 0)
	return sys.version_info[0]


install()