# coding: utf8
import datetime

import wx

from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_CheckListBox
from Ctrl import CTRL_Saisie_date
from Dlg import DLG_Liste_inscriptions
from Dlg import DLG_Selection_activite
from Ol import OL_Liste_inscriptions
from Utils import UTILS_Infos_individus, UTILS_Questionnaires, UTILS_Titulaires
from Utils.UTILS_Traduction import _
import GestionDB

from ext_Extensions_automatiques import addModule, message, hasModule

VERSION = "_v2.0.2"


def Extension():
    if not hasModule(__name__ + VERSION):
        message(u"L'extension est correctement installée, "
            u"merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.", __name__ + VERSION)


def Initialisation():
    AddDateRef()
    AddIDfamille()
    FixDecimalDisplay()
    addModule(__name__ + VERSION)


def AddDateRef():
    '''
    Ajoute le champs "Date de reference" dans les paramètres
    '''
    OL_Liste_inscriptions.ListView.InitModel = InitModel
    OL_Liste_inscriptions.ListView.MAJ = MAJ
    DLG_Liste_inscriptions.Parametres = Parametres


def AddIDfamille():
    '''
    Ajoute IDfamille dans la liste des colonnes disponibles
    '''
    OL_Liste_inscriptions.LISTE_CHAMPS.append({
        "label": _(u"ID de la famille"),
        "code": "IDfamille",
        "champ": "inscriptions.IDfamille",
        "typeDonnee": "entier",
        "align": "left",
        "largeur": 65,
        "stringConverter": None,
        "actif": True,
        "afficher": True
    })


def FixDecimalDisplay():
    '''
    Fixe le bug d'affichage des questions au format decimal
    '''
    UTILS_Questionnaires.Questionnaires.FormatageReponse = FormatageReponse


##############
# AddDateRef #
##############
def InitModel(self, date_reference=datetime.date.today()):
    # Initialisation des questionnaires
    categorie = "inscription"
    self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
    self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
    self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

    # Importation des données
    self.donnees = self.GetTracks()

    # Infos individus
    self.infosIndividus = UTILS_Infos_individus.Informations(date_reference=date_reference)
    for track in self.donnees:
        self.infosIndividus.SetAsAttributs(parent=track, mode="individu", ID=track.IDindividu)
    for track in self.donnees:
        self.infosIndividus.SetAsAttributs(parent=track, mode="famille", ID=track.IDfamille)


def MAJ(self, IDindividu=None, IDactivite=None, partis=True, listeGroupes=[],
    listeCategories=[], regroupement=None, listeColonnes=[], labelParametres="",
    date_reference=datetime.date.today()
        ):
    self.IDactivite = IDactivite
    self.partis = partis
    self.listeGroupes = listeGroupes
    self.listeCategories = listeCategories
    self.regroupement = regroupement
    self.labelParametres = labelParametres
    if IDindividu is not None:
        self.selectionID = IDindividu
        self.selectionTrack = None
    else:
        self.selectionID = None
        self.selectionTrack = None
    attente = wx.BusyInfo(_(u"Recherche des données..."), self)
    self.dict_titulaires = UTILS_Titulaires.GetTitulaires()
    self.InitModel(date_reference=date_reference)
    self.InitObjectListView()
    del attente
    # Sélection d'un item
    if self.selectionTrack is not None:
        self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
    self.selectionID = None
    self.selectionTrack = None


class Parametres(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listview = listview

        # Date reference
        self.box_date_ref = wx.StaticBox(self, -1, _(u"Date référence"))
        self.ctrl_date_ref = CTRL_Saisie_date.Date2(self)
        self.SetDateRef()

        # Activité
        self.box_activite_staticbox = wx.StaticBox(self, -1, _(u"Activité"))
        self.ctrl_activite = DLG_Selection_activite.Panel_Activite(
            self, callback=self.OnSelectionActivite)

        self.check_partis = wx.CheckBox(self, -1, _(u"Afficher les individus partis"))
        self.check_partis.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Groupes
        self.box_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_CheckListBox.Panel(self)

        # Catégories
        self.box_categories_staticbox = wx.StaticBox(self, -1, _(u"Catégories"))
        self.ctrl_categories = CTRL_CheckListBox.Panel(self)

        # Regroupement
        self.box_regroupement_staticbox = wx.StaticBox(self, -1, _(u"Regroupement"))
        self.ctrl_regroupement = DLG_Liste_inscriptions.CTRL_Regroupement(self, listview=listview)

        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(
            self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_actualiser.SetMinSize((250, 40))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixRegroupement, self.ctrl_regroupement)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)

    def __set_properties(self):
        self.ctrl_date_ref.SetToolTip(wx.ToolTip(
            _(u"Choisissez une date de référence pour l'affichage des classes")))
        self.check_partis.SetToolTip(wx.ToolTip(
            _(u"Cochez cette case pour inclure dans la liste des individus partis")))
        self.ctrl_groupes.SetToolTip(wx.ToolTip(_(u"Cochez les groupes à afficher")))
        self.ctrl_categories.SetToolTip(wx.ToolTip(_(u"Cochez les catégories à afficher")))
        self.ctrl_regroupement.SetToolTip(wx.ToolTip(_(u"Sélectionnez un regroupement")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)

        # Date ref
        box_date_ref = wx.StaticBoxSizer(self.box_date_ref, wx.VERTICAL)
        box_date_ref.Add(self.ctrl_date_ref, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(box_date_ref, 1, wx.EXPAND, 0)

        # Activité
        box_activite = wx.StaticBoxSizer(self.box_activite_staticbox, wx.VERTICAL)
        box_activite.Add(self.ctrl_activite, 1, wx.ALL | wx.EXPAND, 5)
        box_activite.Add(self.check_partis, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        grid_sizer_base.Add(box_activite, 1, wx.EXPAND, 0)

        # Groupes
        box_groupes = wx.StaticBoxSizer(self.box_groupes_staticbox, wx.VERTICAL)
        box_groupes.Add(self.ctrl_groupes, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(box_groupes, 1, wx.EXPAND, 0)

        # Catégories
        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        box_categories.Add(self.ctrl_categories, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(box_categories, 1, wx.EXPAND, 0)

        # Regroupement
        box_regroupement = wx.StaticBoxSizer(self.box_regroupement_staticbox, wx.VERTICAL)
        box_regroupement.Add(self.ctrl_regroupement, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(box_regroupement, 1, wx.EXPAND, 0)

        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)

    def OnSelectionActivite(self):
        self.MAJ_Groupes()
        self.MAJ_Categories()

    def MAJ_Groupes(self):
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, IDactivite, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.ctrl_activite.GetID()
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        DB.Close()

        # Formatage des données
        listeDonnees = []
        for IDgroupe, IDactivite, nom in listeGroupes:
            dictTemp = {"ID": IDgroupe, "label": nom, "IDactivite": IDactivite}
            listeDonnees.append(dictTemp)

        # Envoi des données à la liste
        self.ctrl_groupes.SetDonnees(listeDonnees, cocher=True)

    def MAJ_Categories(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, IDactivite, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.ctrl_activite.GetID()
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()

        # Formatage des données
        listeDonnees = []
        for IDcategorie_tarif, IDactivite, nom in listeCategories:
            dictTemp = {"ID": IDcategorie_tarif, "label": nom, "IDactivite": IDactivite}
            listeDonnees.append(dictTemp)

        # Envoi des données à la liste
        self.ctrl_categories.SetDonnees(listeDonnees, cocher=True)

    def OnChoixRegroupement(self, event):
        pass

    def OnBoutonActualiser(self, event):
        # Récupération des paramètres
        date_ref = self.GetDateRef()
        IDactivite = self.ctrl_activite.GetID()
        partis = self.check_partis.GetValue()
        listeGroupes = self.ctrl_groupes.GetIDcoches()
        listeCategories = self.ctrl_categories.GetIDcoches()
        regroupement = self.ctrl_regroupement.GetRegroupement()

        # Vérifications
        if not self.ctrl_date_ref.FonctionValiderDate() or date_ref is None:
            dlg = wx.MessageDialog(self, _(u"La date de référence n'est pas valide !"),
                _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_ref.SetFocus()
            return False

        if IDactivite is None:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"),
                _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeGroupes) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un groupe !"),
                _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeCategories) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une catégorie !"),
                _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        labelParametres = self.GetLabelParametres()

        # MAJ du listview
        self.parent.ctrl_listview.MAJ(IDactivite=IDactivite, partis=partis,
            listeGroupes=listeGroupes, listeCategories=listeCategories,
            regroupement=regroupement, labelParametres=labelParametres,
            date_reference=self.GetDateRef())

    def GetDateRef(self):
        return self.ctrl_date_ref.GetDate()

    def SetDateRef(self, date_reference=datetime.date.today()):
        self.ctrl_date_ref.SetDate(date_reference)

    def GetLabelParametres(self):
        listeParametres = []

        activite = self.ctrl_activite.GetNomActivite()
        listeParametres.append(_(u"Activité : %s") % activite)

        groupes = self.ctrl_groupes.GetLabelsCoches()
        listeParametres.append(_(u"Groupes : %s") % groupes)

        categories = self.ctrl_categories.GetLabelsCoches()
        listeParametres.append(_(u"Catégories : %s") % categories)

        labelParametres = " | ".join(listeParametres)
        return labelParametres


#####################
# FixDecimalDisplay #
#####################
def FormatageReponse(self, reponse="", controle=""):
    filtre = self.GetFiltre(controle)
    texteReponse = u""
    if filtre == "texte":
        texteReponse = reponse
    if filtre == "entier":
        texteReponse = int(reponse)
    if filtre == "montant":
        texteReponse = float(reponse)  # decimal.Decimal(reponse)
    if filtre == "choix":
        if reponse is None:
            if type(reponse) == int:
                listeTemp = [reponse, ]
            else:
                listeTemp = reponse.split(";")
            listeTemp2 = []
            for IDchoix in listeTemp:
                try:
                    IDchoix = int(IDchoix)
                    if IDchoix in self.dictChoix:
                        listeTemp2.append(self.dictChoix[IDchoix])
                except:
                    pass
            texteReponse = ", ".join(listeTemp2)
    if filtre == "coche":
        if reponse in (1, "1"):
            texteReponse = _(u"Oui")
        else:
            texteReponse = _(u"Non")
    if filtre == "date":
        texteReponse = UTILS_Questionnaires.DateEngEnDateDD(reponse)
    if filtre == "decimal":
        texteReponse = float(reponse)
    return texteReponse
