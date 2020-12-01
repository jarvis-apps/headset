#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import dbus
from classes.Logger import Logger

class Headset:
	def __init__(self):
		self.logging = False
		self.bus = dbus.SystemBus()
		self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')

	def set_logger(self, logger_instance):
		self.logger = logger
		self.logging = True

	def dial(self, number, hide_caller_id=None):
		modems = self.manager.GetModems()
		modem = modems[0][0]
		hide_callerid = "default"
		
		if hide_caller_id is not None:
			if hide_caller_id:
				hide_callerid = "enabled"
			else:
				hide_callerid = "disabled"

		vcm = dbus.Interface(self.bus.get_object('org.ofono', modem),
						'org.ofono.VoiceCallManager')
		return vcm.Dial(number, hide_callerid)

	def hangup_all(self):
		modems = self.manager.GetModems()
		modem = modems[0][0]
		return dbus.Interface(bus.get_object('org.ofono', modem),
						'org.ofono.VoiceCallManager').HangupAll()
	def hangup_active(self):
		modems = self.manager.GetModems()
		modem = modems[0][0]
		vcm = dbus.Interface(bus.get_object('org.ofono', modem),
						'org.ofono.VoiceCallManager')
		calls = vcm.GetCalls()
		for path, properties in calls:
				state = properties["State"]
				if state != "active":
					continue
				call = dbus.Interface(bus.get_object('org.ofono', path),
								'org.ofono.VoiceCall')
				call.Hangup()
	def hangup_call(self):
		modems = self.manager.GetModems()
		modem = modems[0][0]
		## TODO: Check if below "modem" is really a modem object...
		call = dbus.Interface(bus.get_object('org.ofono', modem),
						'org.ofono.VoiceCall')
		return call.Hangup()

	def answer_calls(self):
		modems = self.manager.GetModems()

		for path, properties in modems:
			if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
				continue
			mgr = dbus.Interface(bus.get_object('org.ofono', path),
							'org.ofono.VoiceCallManager')
			calls = mgr.GetCalls()
			for path, properties in calls:
				state = properties["State"]
				if state != "incoming":
					continue
				call = dbus.Interface(bus.get_object('org.ofono', path),
								'org.ofono.VoiceCall')
				call.Answer()
