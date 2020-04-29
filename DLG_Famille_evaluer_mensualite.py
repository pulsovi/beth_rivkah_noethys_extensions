# coding: utf8


from Ctrl import CTRL_Bouton_image
from Dlg import DLG_Famille
from Extensions_automatiques import message
from Utils.UTILS_Traduction import _
import CTRL_Famille_outils
import GestionDB
import wx
from divers import copyToClipboard


def Extension():
    message(u"Extension installée")


def Initialisation():
    DLG_Famille.Dialog.MenuEvaluerMensualite = MenuEvaluerMensualite
    CTRL_Famille_outils.Ajouter("bethrivkah", (u"Évaluer mensualité standard",
        "Images/16x16/Euro.png", "self.MenuEvaluerMensualite"))


def MenuEvaluerMensualite(self, event):
    dlg = Dialog(None)
    dlg.ShowModal()
    annee = dlg.GetAnnee()
    dlg.Destroy()
    message(str(annee))

    req = GetInscriptionsQuery(self.IDfamille, annee[0])
    copyToClipboard(req)
    message(req)

    db = GestionDB.DB()
    db.ExecuterReq(req)
    listeDonnees = db.ResultatReq()
    db.Close()
    message(str(listeDonnees))
    return


class Dialog(wx.Dialog):
    def __init__(self, parent, id=-1, title=_(u"Choix année scolaire")):
        wx.Dialog.__init__(self, parent, id, title, name="DLG_annee")
        self.parent = parent
        self.staticbox = wx.StaticBox(self, -1, "")
        self.label = wx.StaticText(self, -1, _(u"Veuillez sélectioner une année scolaire :"))
        self.ctrl_annee = CTRL(self)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(
            self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(
            self, id=wx.ID_OK, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.__set_properties()
        self.__do_layout()
        self.ctrl_annee.SetFocus()

    def __set_properties(self):
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour confirmer")))
        self.ctrl_annee.SetMinSize((300, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        # Intro
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)

        # Staticbox
        staticbox = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_contenu.Add(self.ctrl_annee, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(0)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def GetAnnee(self):
        index = self.ctrl_annee.GetSelection()
        if index == -1:
            return None
        return self.ctrl_annee.dictDonnees[index]


class CTRL(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, choices=[])
        self.parent = parent
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'année scolaire à évaluer.")))
        self.MAJ()

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0:
            self.Enable(False)
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDactivite, nom FROM activites ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.dictDonnees = {}
        listeNoms = []
        index = 0
        for IDactivite, nom in listeDonnees:
            listeNoms.append(nom)
            self.dictDonnees[index] = (IDactivite, nom)
            index += 1
        return listeNoms

    def SetID(self, ID=0):
        if ID is None:
            return
        for index, values in self.dictDonnees.items():
            if values[0] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1:
            return None
        if index == 0:
            return None
        return self.dictDonnees[index][0]


def GetInscriptionsQuery(IDfamille, IDactivite):
    return """
    SELECT
        `inscriptions`.`IDindividu`,
        `tarifs`.`categories_tarifs`,
        `inscriptions`.`IDcategorie_tarif`,
        `tarifs`.`groupes`,
        `inscriptions`.`IDgroupe`,
        `tarifs_lignes`.`taux`
    FROM
        `inscriptions`
        LEFT JOIN `rattachements` USING(`IDindividu`, `IDfamille`)
        LEFT JOIN `tarifs` USING(`IDactivite`)
        LEFT JOIN `tarifs_lignes` USING(`IDtarif`, `IDactivite`)
    WHERE
        `rattachements`.`IDfamille`={IDfamille} AND
        `inscriptions`.`IDactivite`={IDactivite}
    """.format(IDfamille=IDfamille, IDactivite=IDactivite)


def GetTarifsQuery(IDactivite):
    return """
    SELECT
        *
    FROM
        `tarifs`
    WHERE
        `IDactivite`={IDactivite}
    """.format(IDactivite=IDactivite)
