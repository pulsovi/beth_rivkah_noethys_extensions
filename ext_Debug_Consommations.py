# coding: utf8
import atexit
import sys
import traceback
import os
import wx
# from Extensions_automatiques import printErr


def Extension():
    wx.GetApp().OnExit = wxexit
    wx.GetApp().Bind(wx.EVT_CLOSE, wxclose)


def exit_handler(text):
    fd = open('D:\\MesDonnees\\Dev\\noethys_extensions\\Debug_Consommations.log', 'a')
    fd.write(text)
    fd.flush()
    fd.close()
    sys.stderr.write(text)
    printErr("", False)


def Initialisation():
    atexit.register(exit_handler, "AtExit\n")("\n\nDebut\n")
    os.nativeExit = os._exit
    os._exit = osexit


def printErr(err=None, callback=None):
    traceback.print_exc(file=sys.stderr)
    fd = open('D:\\MesDonnees\\Dev\\noethys_extensions\\Debug_Consommations.log', 'a')
    traceback.print_stack(file=fd)
    fd.flush()
    fd.close()
    sys.stderr.write("\n")
    sys.stderr.flush()
    if callable(callback):
        callback(str(err))


def osexit():
    exit_handler("osExit\n")
    os.nativeExit()


def wxexit(self=None, *args, **kwargs):
    exit_handler("WxExit\n")


def wxclose(self=None, *args, **kwargs):
    exit_handler("WxClose\n")
