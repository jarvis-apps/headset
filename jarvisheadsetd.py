#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

# do imports
import sys, os, time
from classes.Jarvis import Jarvis
from classes.Headset import Headset
from classes.Logger import Logger


# check right usage
if "--install" in sys.argv:
	import setup
	setup.install()
if "--token" not in sys.argv and "--use-stored" not in sys.argv:
	print("Usage: python3 jarvisheadsetd.py --token <token>|--use-stored")
	exit(1)


# get token or stored token
token = None
TOKEN_FILE = "token"
if "--token" in sys.argv:
	try:
		token = sys.argv[sys.argv.index("--token") + 1]
		with open(TOKEN_FILE, "w") as f:
			f.write(token)
	except Exception as e:
		print("Usage: python3 jarvisheadsetd.py --token <token>")
		exit(1)
if "--use-stored" in sys.argv:
	try:
		with open(TOKEN_FILE, "r") as f:
			token = f.read()
	except Exception as e:
		print("Token file doesn't exist!")
		print("Usage: python3 jarvisheadsetd.py --token <token>")
		exit(1)


# program logic
tag = "headsetD"
jarvis = Jarvis("localhost", token)
logger = Logger("logs/headset.log")
logger.print_on()

# connect to jarvis backend
# while not jarvis.connect(True):
# 	logger.e(tag, "Failed to connect to Jarvis... 5 seconds to retry")
# 	time.sleep(5)
# logger.s(tag, "Successfully connected to Jarvis at localhost")
