import wx


def copyToClipboard(text):
    clipdata = wx.TextDataObject()
    clipdata.SetText(text)
    wx.TheClipboard.Open()
    wx.TheClipboard.SetData(clipdata)
    wx.TheClipboard.Close()
