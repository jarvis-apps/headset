#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

# do imports
import sys, os, time
from jarvis.Jarvis import Jarvis
from jarvis.Headset import Headset
from jarvis.Logger import Logger


# define globals
DIR = os.path.dirname(os.path.realpath(__file__))
TOKEN_FILE = "{}/token".format(DIR)
LOG_FILE = "{}/logs/headset.log".format(DIR)
LOG_TAG = "app:headsetD"


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
