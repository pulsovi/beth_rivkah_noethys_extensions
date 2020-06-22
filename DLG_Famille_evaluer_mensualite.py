# coding: utf8

from Ctrl import CTRL_Bouton_image
from Dlg import DLG_Famille
from Utils.UTILS_Traduction import _
import wx

from Extensions_automatiques import message, addModule, hasModule, getQuery
from CTRL_Famille_outils import Ajouter as AjouterOutil

VERSION = "_v2.0.0"


QID = {
    "enfantsInscritsBR": 24,
    "intervenantsBR": 1,
    "mensualites": 21,
}

CoeffIntervenantBR = {
    "Non intervenants": 1,
    "1 parent intervenant ": 0.90,  # 1 parent intervenant à mi-temps
    "2 parents intervenant": 0.85,  # 2 parents intervenants à mi-temps
    "1 parent ou plus inte": 0.75,  # 1 parent ou plus intervenants à plein temps
}

CoeffDegressif = [1, 1, 0.92, 0.88, 0.84, 0.80, 0.76]


def Extension():
    if not hasModule(__name__ + VERSION):
        message(u"L'extension est correctement installée, " +
            u"merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.", __name__ + VERSION)


def Initialisation():
    DLG_Famille.Dialog.MenuEvaluerMensualite = MenuEvaluerMensualite
    AjouterOutil("bethrivkah", (u"Évaluer mensualité standard",
        "Images/16x16/Euro.png", "self.MenuEvaluerMensualite"))
    addModule(__name__ + VERSION)


def MenuEvaluerMensualite(self, event):
    activite = GetActivite()
    if activite is None:
        return
    famille, enfants = EvaluerMensualite(self.IDfamille, activite[0])[:2]
    response = u"famille: {montant:10.2f}\n".format(montant=famille)
    for id, prenom, montant, taux in enfants:
        response += u"\n{prenom:25s}: {montant:4.2f}".format(prenom=prenom, montant=montant)
    message(response)


def EvaluerMensualite(IDfamille, IDactivite):
    nb, inscriptions, mensualites, coeff = GetInscriptions(IDfamille, IDactivite)
    filteredList = filter(filtrerListe, inscriptions)
    valid = validateList(nb, filteredList)
    if not valid:
        raise Exception(
            u"\n\nLes donnees d'inscriptions de cette famille semblent anormales.\n" +
            u"Executez l'utilitaire de detection des anomalies et resolvez-les.\n" +
            u"Si cette erreur persiste apres toutes les corrections, merci de contacter " +
            u"le developpeur de l'extension DLG_Famille_evaluer_mensualite\n" +
            str({
                "nb": nb,
                "inscriptions": inscriptions,
                "mensualites": mensualites,
                "filteredList": filteredList,
            })
        )
    famille = 0
    brut = 0
    enfants = []
    for individu, prenom, categorie, IDcategorie, groupe, IDgroupe, taux in filteredList:
        brut += taux
        montant = calculateTaux(taux, mensualites, coeff)
        enfants.append((individu, prenom, montant, taux))
        famille += montant
    return famille, enfants, brut, mensualites


def calculateTaux(taux, mensualites, coeff):
    return taux * 1000000 / int(mensualites) * coeff


def validateList(nb, list):
    if len(list) != nb:
        return False
    individus = set()
    for individu, prenom, categorie, IDcategorie, groupe, IDgroupe, taux in list:
        if individu in individus:
            return False
        individus.add(individu)
    return True


def filtrerListe(ligne):
    individu, prenom, categories, IDcategorie, groupes, IDgroupe, taux = ligne
    if str(IDcategorie) not in str(categories).split(";"):
        return False
    if str(IDgroupe) not in str(groupes).split(";"):
        return False
    return True


class Dialog(wx.Dialog):
    def __init__(self, parent=None, id=-1, title=_(u"Choix année scolaire")):
        wx.Dialog.__init__(self, parent, id, title, name="DLG_annee")
        self.parent = parent
        self.staticbox = wx.StaticBox(self, -1, "")
        self.label = wx.StaticText(self, -1, _(u"Veuillez sélectioner une année scolaire :"))
        self.ctrl_annee = CTRL(self)
        self.bouton_ok = CTRL_Bouton_image.CTRL(
            self, id=wx.ID_OK, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(
            self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.__set_properties()
        self.__do_layout()
        self.ctrl_annee.SetFocus()

    def __set_properties(self):
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour confirmer")))
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
        req = """SELECT IDactivite, nom FROM activites ORDER BY nom;"""
        listeDonnees = getQuery(req)
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


def GetInscriptions(IDfamille, IDactivite):
    inscriptionsQuery = """
    SELECT
        `inscriptions`.`IDindividu`,
        `individus`.`prenom`,
        `tarifs`.`categories_tarifs`,
        `inscriptions`.`IDcategorie_tarif`,
        `tarifs`.`groupes`,
        `inscriptions`.`IDgroupe`,
        `tarifs_lignes`.`taux`
    FROM
        `inscriptions`
        LEFT JOIN `rattachements` USING(`IDindividu`, `IDfamille`)
        LEFT JOIN `individus` USING(`IDindividu`)
        LEFT JOIN `tarifs` USING(`IDactivite`)
        LEFT JOIN `tarifs_lignes` USING(`IDtarif`, `IDactivite`)
    WHERE
        `rattachements`.`IDfamille`={IDfamille} AND
        `inscriptions`.`IDactivite`={IDactivite}
    """.format(IDfamille=IDfamille, IDactivite=IDactivite)

    numberQuery = """
    SELECT COUNT(*) FROM `inscriptions` WHERE `IDfamille`={IDfamille} AND `IDactivite`={IDactivite}
    """.format(IDfamille=IDfamille, IDactivite=IDactivite)
    numberResponse = getQuery(numberQuery)[0][0]

    reponsesQuestionnaire = getQuestionnaireValeurs(IDfamille)

    mensualites = int(reponsesQuestionnaire[QID["mensualites"]])

    intervenantsBR = reponsesQuestionnaire[QID["intervenantsBR"]][0:21]
    enfantsInscritsBR = int(reponsesQuestionnaire[QID["enfantsInscritsBR"]])
    if enfantsInscritsBR > 6:
        enfantsInscritsBR = 6
    coeff = 1 * CoeffIntervenantBR[intervenantsBR] * CoeffDegressif[enfantsInscritsBR]

    return numberResponse, getQuery(inscriptionsQuery), mensualites, coeff


def getQuestionnaireValeurs(IDfamille):
    query = """
    SELECT
        `questionnaire_questions`.`IDquestion` AS `question`,
        IFNULL(
            `questionnaire_choix`.`label`, IFNULL(
                `questionnaire_reponses`.`reponse`, `questionnaire_questions`.`defaut`
        )) AS `reponse`
    FROM
        `questionnaire_questions`
        LEFT OUTER JOIN `questionnaire_reponses` ON(
            `questionnaire_questions`.`IDquestion`=`questionnaire_reponses`.`IDquestion` AND
            `questionnaire_reponses`.`IDfamille`={IDfamille}
        )
        LEFT JOIN `questionnaire_choix` ON (
            `questionnaire_questions`.`IDquestion`=`questionnaire_choix`.`IDquestion` AND
            (
                `questionnaire_reponses`.`reponse`=`questionnaire_choix`.`IDchoix` OR
                (
                    `questionnaire_reponses`.`reponse` IS NULL AND
                    `questionnaire_questions`.`defaut`=`questionnaire_choix`.`IDchoix`
                )
            )
        )
    WHERE
        (
            `questionnaire_reponses`.`IDfamille`={IDfamille} OR
            (
                `questionnaire_reponses`.`IDfamille` IS NULL AND
                `questionnaire_reponses`.`IDindividu` IS NULL
            )
        )
    ORDER BY `questionnaire_questions`.`IDquestion`
    """.format(IDfamille=IDfamille)
    response = getQuery(query)

    reponses = {}
    for question, reponse in response:
        reponses[question] = reponse

    return reponses


def GetActivite():
    dlg = Dialog(None)
    dlg.ShowModal()
    activite = dlg.GetAnnee()
    dlg.Destroy()
    return activite
