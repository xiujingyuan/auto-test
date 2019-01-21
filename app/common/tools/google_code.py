# -*- coding: utf-8 -*-
# @Time    : 18-4-10 上午11:20
# @Author  : Fyi Zhang
# @Site    :
# @File    : Connection.py
# @Software: PyCharm

import base64
import hashlib
import hmac
import struct
import time
import win32clipboard as w
import win32con
import win32gui
import win32api
import sys


class googleCode:

    def calGoogleCode(self, secretKey):
        try:
            input = int(time.time()) // 30
            lens = len(secretKey)
            lenx = 4 - (lens % 4 if lens % 4 else 4)
            secretKey += lenx * '='
            print (secretKey, ' ----- ', lenx, lens, '|')
            key = base64.b32decode(secretKey)
            msg = struct.pack(">Q", input)
            googleCode = hmac.new(key, msg, hashlib.sha1).digest()

            o = googleCode[19] & 15
            googleCode = str((struct.unpack(">I", googleCode[o:o + 4])[0] & 0x7fffffff) % 1000000)
            if len(googleCode) == 5:
                googleCode = '0' + googleCode
            return googleCode
        except Exception as e:
            print(e)
            

    def set_verify_code(self, verify_code):
        w.OpenClipboard()
        w.EmptyClipboard()
        w.SetClipboardData(win32con.CF_TEXT, verify_code)
        w.CloseClipboard()

    def find_windows(self,verify_string_param,class_name):

        handle = win32gui.FindWindow(class_name, None);
        print(win32gui.GetClassName(handle))
        win32gui.ShowWindow(handle, win32con.SW_SHOWMAXIMIZED)
        win32gui.SetForegroundWindow(handle)
        self.input_verify_code(verify_string_param, handle)
        win32api.keybd_event(0x0D, handle, 0, 0)

    def input_verify_code(self, input_string, handle):
        print(input_string)
        for x in input_string:
            self.key_board(int(x), handle)
            time.sleep(0.1)

    def key_board(self, number, handle):
        if number == 0:
            win32api.keybd_event(0x30, handle, 0, 0)
        elif number == 1:
            win32api.keybd_event(0x31, handle, 0, 0)
        elif number == 2:
            win32api.keybd_event(0x32, handle, 0, 0)
        elif number == 3:
            win32api.keybd_event(0x33, handle, 0, 0)
        elif number == 4:
            win32api.keybd_event(0x34, handle, 0, 0)
        elif number == 5:
            win32api.keybd_event(0x35, handle, 0, 0)
        elif number == 6:
            win32api.keybd_event(0x36, handle, 0, 0)
        elif number == 7:
            win32api.keybd_event(0x37, handle, 0, 0)
        elif number == 8:
            win32api.keybd_event(0x38, handle, 0, 0)
        elif number == 9:
            win32api.keybd_event(0x39, handle, 0, 0)


if __name__ == "__main__":
    verify_string = sys.argv[1]
    class_name = sys.argv[2]
    print(verify_string)
    print(class_name)
    t = googleCode()
    verify_code = t.calGoogleCode(verify_string)
    print(verify_code)
	#t.set_verify_code(verify_code)
    t.find_windows(verify_code,class_name)
