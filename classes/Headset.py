#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import dbus
import time
import threading
from jarvis import Logger, Exiter


class Headset:
    def __init__(self):
        self.logging = False
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object(
            'org.ofono', '/'), 'org.ofono.Manager')

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
        return dbus.Interface(self.bus.get_object('org.ofono', modem),
                              'org.ofono.VoiceCallManager').HangupAll()

    def hangup_active(self):
        modems = self.manager.GetModems()
        modem = modems[0][0]
        vcm = dbus.Interface(self.bus.get_object('org.ofono', modem),
                             'org.ofono.VoiceCallManager')
        calls = vcm.GetCalls()
        for path, properties in calls:
            state = properties["State"]
            if state != "active":
                continue
            call = dbus.Interface(self.bus.get_object('org.ofono', path),
                                  'org.ofono.VoiceCall')
            call.Hangup()

    def hangup_call(self):
        modems = self.manager.GetModems()
        modem = modems[0][0]
        # TODO: Check if below "modem" is really a modem object...
        call = dbus.Interface(self.bus.get_object('org.ofono', modem),
                              'org.ofono.VoiceCall')
        return call.Hangup()

    def answer_calls(self):
        modems = self.manager.GetModems()

        for path, properties in modems:
            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                continue
            mgr = dbus.Interface(self.bus.get_object('org.ofono', path),
                                 'org.ofono.VoiceCallManager')
            calls = mgr.GetCalls()
            for path, properties in calls:
                state = properties["State"]
                if state != "incoming":
                    continue
                call = dbus.Interface(self.bus.get_object('org.ofono', path),
                                      'org.ofono.VoiceCall')
                call.Answer()

    def hold_and_answer(self, timeout=100):
        modems = self.manager.GetModems()
        modem = modems[0][0]

        manager = dbus.Interface(self.bus.get_object('org.ofono', modem),
                                 'org.ofono.VoiceCallManager')

        manager.HoldAndAnswer(timeout=timeout)

    def release_and_answer(self):
        path = None
        modems = self.manager.GetModems()
        for path_i, properties in modems:
            if "org.ofono.VoiceCallManager" in properties["Interfaces"]:
                path = path_i
                break
        if (path is None):
            return (False, "Modem not found")
        modemapi = dbus.Interface(self.bus.get_object(
            'org.ofono', path), 'org.ofono.Modem')
        properties = modemapi.GetProperties()

        if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
            return (False, "org.ofono.VoiceCallManager not found")

        print("[ %s ]" % (path))

        mgr = dbus.Interface(self.bus.get_object('org.ofono', path),
                             'org.ofono.VoiceCallManager')

        mgr.ReleaseAndAnswer()

    def release_and_swap(self):
        modem = None
        modems = self.manager.GetModems()
        for path, properties in modems:
            if "org.ofono.VoiceCallManager" in properties["Interfaces"]:
                modem = path
                break
        if (modem is None):
            return (False, "Modem not found")
        modemapi = dbus.Interface(self.bus.get_object(
            'org.ofono', modem), 'org.ofono.Modem')
        properties = modemapi.GetProperties()

        if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
            print("org.ofono.VoiceCallManager not found")
            exit(2)

        print("[ %s ]" % (modem))

        mgr = dbus.Interface(self.bus.get_object('org.ofono', modem),
                             'org.ofono.VoiceCallManager')

        mgr.ReleaseAndSwap()

    def is_call_incoming(self):
        modems = self.manager.GetModems()

        for path, properties in modems:
            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                continue

            mgr = dbus.Interface(self.bus.get_object('org.ofono', path),
                                 'org.ofono.VoiceCallManager')
            calls = mgr.GetCalls()

            if len(calls) == 0:
                return False
            return mgr.GetCalls()

    def on_ingoing_call(self, fn):
        looper_thread = threading.Thread(
            target=Headset.on_ingoing_call_looper, name="Ingoing Call Looper", args=[self, fn])
        looper_thread.start()

    @staticmethod
    def on_ingoing_call_looper(obj, fn):
        while Exiter.running:
            call = obj.is_call_incoming()
            if call:
                fn(call)
            time.sleep(0.5)

    # BELOW FUNCTIONS ARE NOT READY YET!!!

    # these functions do work but produce no output

    def _list_calls(self):
        modems = self.manager.GetModems()

        for path, properties in modems:
            print("[ %s ]" % (path))

            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                continue

            mgr = dbus.Interface(self.bus.get_object('org.ofono', path),
                                 'org.ofono.VoiceCallManager')

            calls = mgr.GetCalls()

            for path, properties in calls:
                print("    [ %s ]" % (path))

                for key in properties.keys():
                    if key == 'Icon':
                        print("        %s = %d" % (key, properties[key]))
                    else:
                        val = str(properties[key])
                        print("        %s = %s" % (key, val))

    def _list_messages(self):
        modems = self.manager.GetModems()

        for path, properties in modems:
            print("[ %s ]" % (path))

            if "org.ofono.MessageManager" not in properties["Interfaces"]:
                continue

            connman = dbus.Interface(self.bus.get_object('org.ofono', path),
                                     'org.ofono.MessageManager')

            contexts = connman.GetMessages()

            for path, properties in contexts:
                print("    [ %s ]" % (path))

                for key in properties.keys():
                    val = str(properties[key])
                    print("        %s = %s" % (key, val))

                print('')

    # these functions do not work yet

    def _send_sms(self, to, message, use_delivery_reports=False):
        modems = self.manager.GetModems()
        path = modems[0][0]
        mm = dbus.Interface(self.bus.get_object('org.ofono', path),
                            'org.ofono.MessageManager')

        # mm.SetProperty("UseDeliveryReports", dbus.Boolean(use_delivery_reports))
        mm.SendMessage(to, message)
    # TODO: need mainloop

    def _on_sms(self, callback_fn=False):
        def incoming_message(message, details, path, interface):
            print("%s" % (message.encode('utf-8')))

            for key in details:
                val = details[key]
                print("    %s = %s" % (key, val))

        self.bus.add_signal_receiver(incoming_message,
                                     bus_name="org.ofono",
                                     signal_name="ImmediateMessage",
                                     path_keyword="path",
                                     interface_keyword="interface")

        self.bus.add_signal_receiver(incoming_message,
                                     bus_name="org.ofono",
                                     signal_name="IncomingMessage",
                                     path_keyword="path",
                                     interface_keyword="interface")

    def _set_speaker_volume(self, volume):
        modems = self.manager.GetModems()
        path = modems[0][0]

        cv = dbus.Interface(self.bus.get_object('org.ofono', path),
                            'org.ofono.CallVolume')

        cv.SetProperty("SpeakerVolume", dbus.Byte(int(volume)))

    def _get_phone_book(self, timeout=100):
        modems = self.manager.GetModems()
        path = modems[0][0]

        phonebook = dbus.Interface(self.bus.get_object('org.ofono', path),
                                   'org.ofono.Phonebook')

        print(phonebook.Import(timeout=timeout))
