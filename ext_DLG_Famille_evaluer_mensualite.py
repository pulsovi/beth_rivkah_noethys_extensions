# coding: utf8

# exposes
#    classes: Inscriptions
#    functions: GetActivite
#        deprecated: EvaluerMensualite
import wx

from Ctrl import CTRL_Bouton_image
from Dlg import DLG_Famille
from Utils.UTILS_Traduction import _

from ext_Extensions_automatiques import message, addModule, hasModule, deprecate
from ext_CTRL_Famille_outils import Ajouter as AjouterOutil, UpdateQuestionnaire, CTRL_ANNEE

VERSION = "_v3.0.1"


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
    inscriptions = Inscriptions()
    activite = GetActivite(inscriptions)
    if activite is None:
        inscriptions.Close()
        return
    brut, mensualites, coeffBR, coeffDeg, enfants = inscriptions.EvaluerMensualite(
        self.IDfamille, activite[0])
    inscriptions.Close()

    coeff = coeffBR * coeffDeg
    msgBrut = u"MONTANT BRUT:\n- famille: {montant:25.2f}\n".format(
        montant=inscriptions.CalculateTaux(brut, mensualites))
    msgRed = u"MONTANT REDUIT:\n- famille: {montant:25.2f}\n".format(
        montant=inscriptions.CalculateTaux(brut, mensualites, coeff))

    for id, prenom, taux in enfants:
        msgBrut += u"\n- {prenom:25s}: {montant:15.2f}".format(prenom=prenom,
            montant=inscriptions.CalculateTaux(taux, mensualites))
        msgRed += u"\n- {prenom:25s}: {montant:15.2f}".format(prenom=prenom,
            montant=inscriptions.CalculateTaux(taux, mensualites, coeff))

    reponse = (u"{msgBrut}\n\nREDUCTIONS:\n- intervenants BR: {coeffBR:25.0%}\n"
        u"- tarif dégressif: {coeffDeg:25.0%}\n- soit: {coeff:25.2%}\n\n\n{msgRed}").format(
        msgBrut=msgBrut, msgRed=msgRed,
        coeffBR=1 - coeffBR, coeffDeg=1 - coeffDeg, coeff=1 - coeff)
    message(reponse)


def EvaluerMensualite(IDfamille, IDactivite):
    deprecate("Deprecated function EvaluerMensualite use class Inscriptions instead.")
    inscriptions = Inscriptions()
    brut, mensualites, coeffBR, coeffDeg, enfantsG = inscriptions.EvaluerMensualite(
        IDfamille, IDactivite)
    famille = inscriptions.CalculateTaux(brut, mensualites, coeffDeg * coeffBR)
    enfants = []
    for individu, prenom, taux in enfantsG:
        montant = inscriptions.CalculateTaux(taux, mensualites, coeffBR * coeffDeg)
        enfants.append((individu, prenom, montant, taux))
    inscriptions.Close()
    return famille, enfants, brut, mensualites


class Inscriptions(UpdateQuestionnaire):
    def EvaluerMensualite(self, IDfamille, IDactivite):
        """Returns tuple: (brut, mensualites, coeffBR, coeffDeg, enfants)
        enfants is array of tuples like: (IDindividu, prenom, taux)
        """
        nb, inscriptions, mensualites, coeffBR, coeffDeg = self.GetInscriptions(
            IDfamille, IDactivite)
        filteredList = filter(self.FiltrerListe, inscriptions)
        valid = self.ValidateList(nb, filteredList)
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
        brut = 0
        enfants = []
        for individu, prenom, categorie, IDcategorie, groupe, IDgroupe, taux in filteredList:
            brut += taux
            enfants.append((individu, prenom, taux))
        return brut, mensualites, coeffBR, coeffDeg, enfants

    def GetInscriptions(self, IDfamille, IDactivite):
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
        inscriptions = self.GetResponse(inscriptionsQuery)

        numberQuery = """
        SELECT COUNT(*) FROM `inscriptions`
        WHERE `IDfamille`={IDfamille} AND `IDactivite`={IDactivite}
        """.format(IDfamille=IDfamille, IDactivite=IDactivite)
        number = self.GetResponse(numberQuery)[0][0]

        reponsesQuestionnaire = self.GetQuestionnaireValeurs(IDfamille)

        mensualites = int(reponsesQuestionnaire[QID["mensualites"]])

        intervenantsBR = reponsesQuestionnaire[QID["intervenantsBR"]][0:21]
        enfantsInscritsBR = int(reponsesQuestionnaire[QID["enfantsInscritsBR"]])
        if enfantsInscritsBR > 6:
            enfantsInscritsBR = 6
        coeffBR = CoeffIntervenantBR[intervenantsBR]
        coeffDeg = CoeffDegressif[enfantsInscritsBR]

        return number, inscriptions, mensualites, coeffBR, coeffDeg

    def GetQuestionnaireValeurs(self, IDfamille):
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
        response = self.GetResponse(query)

        reponses = {}
        for question, reponse in response:
            reponses[question] = reponse

        return reponses

    def GetQuotient(self, IDfamille, IDactivite):
        query = """
        SELECT *
        FROM
            `quotients`
            JOIN `activites` ON (
                `activites`.`date_fin`>=`quotients`.`date_debut`
                AND `activites`.`date_debut`<=`quotients`.`date_fin`
            )
        WHERE
            `activites`.`IDactivite`={IDactivite}
            AND `quotients`.`IDfamille`={IDfamille}
        """.format(IDfamille=IDfamille, IDactivite=IDactivite)
        response = self.GetResponse(query)
        # if response:
        #     if len(response) > 1:
        #         print(u"la famille %d a plusieurs quotients pour cette annee" % IDfamille)
        return response[-1] if response else None

    def ValidateList(self, nb, list):
        if len(list) != nb:
            return False
        individus = set()
        for individu, prenom, categorie, IDcategorie, groupe, IDgroupe, taux in list:
            if individu in individus:
                return False
            individus.add(individu)
        return True

    def CalculateTaux(self, taux, mensualites, coeff=1):
        return taux * 1000000 / int(mensualites) * coeff

    def FiltrerListe(self, ligne):
        individu, prenom, categories, IDcategorie, groupes, IDgroupe, taux = ligne
        if str(IDcategorie) not in str(categories).split(";"):
            return False
        if str(IDgroupe) not in str(groupes).split(";"):
            return False
        return True


class Dialog(wx.Dialog):
    def __init__(self, db, parent=None, id=-1, title=_(u"Choix année scolaire")):
        super(Dialog, self).__init__(parent, id, title, name="DLG_annee")
        self.parent = parent
        self.staticbox = wx.StaticBox(self, -1, "")
        self.label = wx.StaticText(self, -1, _(u"Veuillez sélectioner une année scolaire :"))
        self.ctrl_annee = CTRL_ANNEE(self, db)
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


def GetActivite(db=None):
    if db is None:
        connection = UpdateQuestionnaire()
    else:
        connection = db
    dlg = Dialog(connection)
    dlg.ShowModal()
    activite = dlg.GetAnnee()
    dlg.Destroy()
    if db is None:
        connection.Close()
    return activite
