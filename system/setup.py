#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import sys, os, hashlib, apt, re, copy, subprocess, json, pwd
from getpass import getpass
from xml.etree import ElementTree as ET
from jarvis import Colors, SetupTools

DIR = os.path.dirname(os.path.realpath(__file__))

def install():
	global INSTALL_DIRECTORY

	SetupTools.check_python_version(3)
	SetupTools.check_root()
	USR = SetupTools.get_default_user(os.getlogin())

	# update system and install bluetooth utilities
	SetupTools.do_action("updating system", 										 "sudo apt update ; sudo apt upgrade -y", exit_on_fail=False)
	SetupTools.do_action("installing utilities", 									 "sudo apt install -y alsa-utils bluez bluez-tools pulseaudio-module-bluetooth python-gobject python-gobject-2 ofono python3-dbus libbluetooth-dev")
	SetupTools.do_action("adding pi to 'lp' group", 								f"sudo usermod -a -G lp {USR}")
	SetupTools.do_action("installing bluetooth packages", 							 "sudo apt install -y python-dbus python-pip ; pip install tcpbridge bluetool")
	SetupTools.do_action("installing jarvis bluetooth utility (jarvis-bluetooth)", 	f"sudo mv {DIR}/jarvis-bluetooth /usr/bin/jarvis-bluetooth")
	SetupTools.do_action("making jarvis-bluetooth executable", 						f"sudo chmod 777 /usr/bin/jarvis-bluetooth")


	# setup bluetooth sound
	with open("/etc/bluetooth/audio.conf", "w") as f:
		f.write("[General]\nClass = 0x20041C\nEnable = Source,Sink,Media,Socket\n")

	SetupTools.regex_replace_in_file("/etc/bluetooth/main.conf", "[#]?Name =.+", "Name = Jarvis")
	SetupTools.regex_replace_in_file("/etc/bluetooth/main.conf", "[#]?Class =.+", "Class = 0x20041C")
	SetupTools.do_action("modify bluetooth configuration", "true")


	# modify ofono dbus config file (for a2dp)
	cnf = ET.parse("/etc/dbus-1/system.d/ofono.conf")
	root = cnf.getroot()
	with open("/etc/dbus-1/system.d/ofono.conf", "r") as f:
		text_contents = f.read()
		pre = ""
		try:
			pre = re.search(f"[\w\W]*?<{root.tag}", text_contents).group(0).replace(f"<{root.tag}", "")
		except Exception as e:
			pass

	insert_element = copy.deepcopy(root.find("policy[@user='root']"))
	allowed_users = [child.get("user") for child in cnf.findall("policy[@user]")]
	if USR not in allowed_users:
		insert_element.set("user", USR)
		root.insert(1, insert_element)
	
	del insert_element
	insert_element = copy.deepcopy(root.find("policy[@user='root']"))
	if "pulse" not in allowed_users:
		insert_element.set("user", "pulse")
		root.insert(1, insert_element)

	final_string = f"{pre}\n{ET.tostring(root, 'unicode')}"
	with open("/etc/dbus-1/system.d/ofono.conf", "w") as f:
		f.write(final_string)


	if not os.path.exists(f"/home/{USR}/.config/systemd/user/default.target.wants"):
		os.makedirs(f"/home/{USR}/.config/systemd/user/default.target.wants")
	try:
		os.symlink("/usr/lib/systemd/user/pulseaudio.service", "/home/pi/.config/systemd/user/default.target.wants/pulseaudio.service")
	except FileExistsError as e:
		pass
	if not os.path.exists(f"/home/{USR}/.config/systemd/user/sockets.target.wants"):
		os.makedirs(f"/home/{USR}/.config/systemd/user/sockets.target.wants")
	try:
		os.symlink("/usr/lib/systemd/user/pulseaudio.socket", "/home/pi/.config/systemd/user/sockets.target.wants/pulseaudio.socket",)
	except FileExistsError as e:
		pass
	SetupTools.do_action("changing permissions", f"sudo chown -R {USR}: /home/{USR}/.config")


	print(f"{Colors.GREEN}Successfully set up Jarvis headset{Colors.END}\nA reboot is necessary for all features to work (especially headset functionality)")
	exit(0)
	

install()