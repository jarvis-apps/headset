#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

# do imports
import sys, os, time
from jarvis import Jarvis, Logger, MQTT
from classes.Headset import Headset

# define globals
DIR = os.path.dirname(os.path.realpath(__file__))
TOKEN_FILE = "{}/token".format(DIR)
LOG_FILE = "{}/logs/headset.log".format(DIR)
LOG_TAG = "app:headsetd"

headset = Headset()


if "--test" in sys.argv:
	print("You're running this script in test mode. You have the following options:")
	print(" 0 - Call a number")
	print(" 1 - Accept a call")
	print(" 2 - Hangup a call")

	while True:
		next_action = input("Please enter an action [0-2]: ")
		if next_action == "0":
			number = input(" -> Enter the number to call: ")
			headset.dial(number)
		if next_action == "1":
			headset.answer_calls()
		if next_action == "2":
			headset.hangup_call()

# check right usage
# if "--token" not in sys.argv and "--use-stored" not in sys.argv:
# 	print("Usage: python3 headsetd.py --token <token>|--use-stored")
# 	exit(1)


# get token or stored token
# token = None
# if "--token" in sys.argv:
# 	try:
# 		token = sys.argv[sys.argv.index("--token") + 1]
# 		with open(TOKEN_FILE, "w") as f:
# 			f.write(token)
# 	except Exception as e:
# 		print("Usage: python3 headsetd.py --token <token>")
# 		exit(1)
# if "--use-stored" in sys.argv:
# 	try:
# 		with open(TOKEN_FILE, "r") as f:
# 			token = f.read()
# 	except Exception as e:
# 		print("Token file doesn't exist!")
# 		print("Usage: python3 headsetd.py --token <token>")
# 		exit(1)


# # program logic
# jarvis = Jarvis("localhost", token)
# logger = Logger(LOG_FILE)
# logger.print_on()


# # connect to jarvis backend
# while not jarvis.connect(True):
# 	logger.e(LOG_TAG, "Failed to connect to Jarvis... 5 seconds to retry")
# 	time.sleep(5)
# logger.s(LOG_TAG, "Successfully connected to Jarvis at localhost")
