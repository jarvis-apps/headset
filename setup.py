#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import sys, os, hashlib, apt
from getpass import getpass

INSTALL_DIRECTORY = "/jarvisheadsetd"
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def install():
	global INSTALL_DIRECTORY
	if get_python_version() != 3:
		print("You need to run this script with python3")
		exit(1)
	if not is_root():
		print("You need to be root!")
		exit(1)

	if not is_installed("ofono"):
		do_action("installing package ofono", "sudo apt install -y ofono", False)
	do_action("starting ofono service", "sudo service ofono start")
	do_action("enabling ofono service", "sudo service ofono enable")

	if not is_installed("pulseaudio-module-bluetooth"):
		do_action("installing packages pulseaudio, pulseaudio-module-bluetooth", "sudo apt -y install pulseaudio pulseaudio-module-bluetooth", False)
	
	do_action("installing python3 utils", "sudo apt install -y python3-pip bluetooth bluez libbluetooth-dev")
	do_action("installing package pybluez", "sudo pip3 install pybluez")

	do_action("creating directory", "sudo mkdir " + INSTALL_DIRECTORY)
	do_action("moving downloaded folder", "sudo mv {} {}".format(CURRENT_DIRECTORY, INSTALL_DIRECTORY))

	do_action("installing service file", "sudo cp -v {}/jarvisheadsetd.service /etc/systemd/system/jarvisheadsetd.service".format(INSTALL_DIRECTORY))

	do_action("reloading systemd", "sudo systemctl daemon-reload")
	do_action("starting jarvisheadsetd service", "sudo service jarvisheadsetd start")
	do_action("enabling jarvisheadsetd service", "sudo service jarvisheadsetd enable")

	print("Successfully set up jarvisheadsetd!")

	print("\nPlease follow these steps to enable the headset and connect your device:")
	print("Open '/etc/pulse/default.pa'.")
	print(" -> sudo nano /etc/pulse/default.pa")
	print("Add 'headset=ofono' on the line of 'module-bluetooth-discover'.")
	print(" -> load-module module-bluetooth-discover headset=ofono")

	print("")
	print("Please reboot!")
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

def is_root():
	return os.geteuid() == 0

def get_python_version():
	# (2, 5, 2, 'final', 0)
	return sys.version_info[0]

cache = apt.Cache()
def is_installed(package):
	global cache
	return cache[package].is_installed:
