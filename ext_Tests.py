# coding: utf8
import wx

from Dlg import DLG_Famille


def Extension():
    dlg = Consigne(style=wx.STAY_ON_TOP)
    dlg.SetPosition(wx.Point(500))
    Dlg_Famille_(dlg)
    dlg.Destroy()


def Dlg_Famille_(dlg):
    famille = DLG_Famille.Dialog(None, 15)
    Dlg_Famille_Evaluer_Mensualite(dlg, famille)
    Dlg_Famille_Fixer_Tarif(dlg, famille)
    famille.Destroy()


def Dlg_Famille_Evaluer_Mensualite(dlg, famille):
    dlg.SetText(u"Selectionner 2019-2020\n\nLes chiffres doivent être 634.80, 312.80, 322")
    famille.MenuEvaluerMensualite(None)


def Dlg_Famille_Fixer_Tarif(dlg, famille):
    dlg.SetText(u"Verifier l'application du tarif")
    famille.MenuFixerTarif(None)
    famille.ShowModal()


class Consigne():
    def __init__(self, text="", title="Information", **kwargs):
        self.frame = wx.Frame(None, title=title, **kwargs)
        self.panel = wx.Panel(self.frame)
        self.label = wx.StaticText(self.panel)
        self.SetText(text)

    def SetText(self, text):
        self.label.SetLabel(text)
        self.panel.SetSize(self.panel.GetBestFittingSize())
        self.frame.SetSize(self.frame.GetBestFittingSize())
        self.frame.Show(True)

    def Destroy(self):
        self.frame.Destroy()

    def SetPosition(self, *args, **kwargs):
        self.frame.SetPosition(*args, **kwargs)
