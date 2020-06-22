# coding: utf8
from Dlg import DLG_Famille
from Dlg import DLG_Famille_questionnaire
from Extensions_automatiques import message, hasModule, addModule, getQuery
from CTRL_Famille_outils import Ajouter as AjouterOutil, GetQuestionnaireValeurs
import wx

VERSION = "_v1.0.4"


def Extension():
    if not hasModule(__name__ + VERSION):
        message(u"L'extension est correctement installée, "
            u"merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.", __name__ + VERSION)


def Initialisation():
    # MAJ automatique à la sauvegarde
    DLG_Famille_questionnaire.Panel.NoethysSauvegarde = DLG_Famille_questionnaire.Panel.Sauvegarde
    DLG_Famille_questionnaire.Panel.Sauvegarde = customQuestionnaireSauvegarde
    # MAJ sur demande par menu Outils
    DLG_Famille.Dialog.MenuMettreAJourLesResultatsCalcules = MenuMettreAJourLesResultatsCalcules
    AjouterOutil("bethrivkah", (u"Mettre à jour les résultats calculés",
        "Images/16x16/Actualiser2.png", "self.MenuMettreAJourLesResultatsCalcules"))
    addModule(__name__ + VERSION)


def MenuMettreAJourLesResultatsCalcules(self, event):
    notebook = self.notebook
    page = notebook.dictPages["questionnaire"]["ctrl"]
    page.Sauvegarde()


def customQuestionnaireSauvegarde(self):
    # mise à jour de la BDD avec les valeurs saisies
    self.NoethysSauvegarde()
    # mise à jour de la BDD pour les valeurs calculées
    majResultatsCalcules(self.IDfamille)
    # mise à jour de l'affichage
    self.majEffectuee = False
    wx.CallLater(1, self.MAJ)


def majResultatsCalcules(IDfamille):
    noms = {
        2: "SalaireP1", 3: "ChomageP1", 4: "CAFP1", 5: "AutreRevenusP1",
        6: "SalaireP2", 7: "ChomageP2", 8: "CAFP2", 9: "AutreRevenusP2",
        10: "Loyer", 11: "CreditImmo", 12: "Charges", 13: "Scolarite",
        14: "TotalRevenusP1", 15: "TotalRevenusP2", 16: "TotalRevenusFamille", 17: "TotalCharges",
        23: "NbEnfantsACharge", 18: "ResteAVivre",
    }
    reponsesQuestionnaire = {}
    for IDquestion, valeur in GetQuestionnaireValeurs(IDfamille).iteritems():
        if IDquestion not in noms:
            continue
        valeur["reponse"] = float(valeur["reponse"])
        reponsesQuestionnaire[noms[IDquestion]] = valeur

    nbParents = int(getQuery("""
    SELECT IFNULL(SUM(`IDcivilite`!=4 AND `IDcivilite`!=5), 0)
    FROM
        `familles`
        LEFT OUTER JOIN `rattachements` USING(`IDfamille`)
        LEFT OUTER JOIN `individus` USING(`IDindividu`)
    WHERE `IDfamille`={IDfamille};
    """.format(IDfamille=IDfamille))[0][0])

    formatDict = {
        "IDfamille": IDfamille,
        "TotalRevenusP1id": reponsesQuestionnaire["TotalRevenusP1"]["IDreponse"],
        "TotalRevenusP2id": reponsesQuestionnaire["TotalRevenusP2"]["IDreponse"],
        "TotalChargesID": reponsesQuestionnaire["TotalCharges"]["IDreponse"],
        "TotalRevenusFamilleID": reponsesQuestionnaire["TotalRevenusFamille"]["IDreponse"],
        "ResteAVivreID": reponsesQuestionnaire["ResteAVivre"]["IDreponse"],
        "TotalRevenusP1val": (
            reponsesQuestionnaire["SalaireP1"]["reponse"]
            + reponsesQuestionnaire["ChomageP1"]["reponse"]
            + reponsesQuestionnaire["CAFP1"]["reponse"]
            + reponsesQuestionnaire["AutreRevenusP1"]["reponse"]
        ),
        "TotalRevenusP2val": (
            reponsesQuestionnaire["SalaireP2"]["reponse"]
            + reponsesQuestionnaire["ChomageP2"]["reponse"]
            + reponsesQuestionnaire["CAFP2"]["reponse"]
            + reponsesQuestionnaire["AutreRevenusP2"]["reponse"]
        ),
        "TotalChargesVal": (
            reponsesQuestionnaire["Loyer"]["reponse"]
            + reponsesQuestionnaire["CreditImmo"]["reponse"]
            + reponsesQuestionnaire["Charges"]["reponse"]
            + reponsesQuestionnaire["Scolarite"]["reponse"]
        ),
    }
    formatDict["TotalRevenusFamilleVal"] = formatDict["TotalRevenusP1val"] + \
        formatDict["TotalRevenusP2val"]
    formatDict["ResteAVivreVal"] = (
        (formatDict["TotalRevenusFamilleVal"] - formatDict["TotalChargesVal"])
        / (30 * (nbParents + reponsesQuestionnaire["NbEnfantsACharge"]["reponse"]))
    )

    query = """
    INSERT INTO `questionnaire_reponses`
        (`IDreponse`, `IDquestion`, `IDfamille`, `reponse`)
    VALUES
        ({TotalRevenusP1id}, 14, {IDfamille}, {TotalRevenusP1val}),
        ({TotalRevenusP2id}, 15, {IDfamille}, {TotalRevenusP2val}),
        ({TotalRevenusFamilleID}, 16, {IDfamille}, {TotalRevenusFamilleVal}),
        ({TotalChargesID}, 17, {IDfamille}, {TotalChargesVal}),
        ({ResteAVivreID}, 18, {IDfamille}, {ResteAVivreVal})
    ON DUPLICATE KEY UPDATE reponse=VALUES(reponse);
    """.format(**formatDict)
    getQuery(query)
