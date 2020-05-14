# coding: utf8
from Dlg import DLG_Famille
from Dlg import DLG_Famille_questionnaire
from Extensions_automatiques import message, hasModule, addModule, getQuery
from CTRL_Famille_outils import Ajouter as AjouterOutil
import wx

VERSION = "1.0"
NoethysSauvegardeQuestionnaire = None


def Extension():
    if not hasModule(__name__ + VERSION):
        message(u"L'extension est correctement installée, merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.")


def Initialisation():
    global NoethysSauvegardeQuestionnaire
    NoethysSauvegardeQuestionnaire = DLG_Famille_questionnaire.Panel.Sauvegarde
    DLG_Famille_questionnaire.Panel.Sauvegarde = customQuestionnaireSauvegarde
    DLG_Famille.Dialog.MenuMettreAJourLesResultatsCalcules = MenuMettreAJourLesResultatsCalcules
    AjouterOutil("bethrivkah", (u"Mettre à jour les résultats calculés",
        "Images/16x16/Actualiser2.png", "self.MenuMettreAJourLesResultatsCalcules"))
    addModule(__name__ + VERSION)


def MenuMettreAJourLesResultatsCalcules(self, event):
    notebook = self.notebook
    page = notebook.dictPages["questionnaire"]["ctrl"]
    page.Sauvegarde()


def customQuestionnaireSauvegarde(self):
    message("sauvegarde")
    # mise à jour de la BDD avec les valeurs saisies
    NoethysSauvegardeQuestionnaire(self)
    # mise à jour de la BDD pour les valeurs calculées
    majResultatsCalcules(self.IDfamille)
    # mise à jour de l'affichage
    self.majEffectuee = False
    wx.CallLater(1, self.MAJ)


def majResultatsCalcules(IDfamille):
    getQuery(getQueryString(IDfamille))


def getQueryString(IDfamille):
    return """
        SELECT IFNULL(`reponse`, 0) INTO @SalaireP1
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=2 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @ChomageP1
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=3 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @CAFP1
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=4 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @AutreRevenusP1
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=5 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @SalaireP2
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=6 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @ChomageP2
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=7 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @CAFP2
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=8 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @AutreRevenusP2
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=9 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @Loyer
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=10 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @CreditImmo
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=11 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @Charges
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=12 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @Scolarite
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=13 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`reponse`, 0) INTO @NbEnfantsACharge
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=23 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`IDreponse`, NULL) INTO @TotalRevenusP1
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=14 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`IDreponse`, NULL) INTO @TotalRevenusP2
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=15 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`IDreponse`, NULL) INTO @TotalRevenusFamille
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=16 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`IDreponse`, NULL) INTO @TotalCharges
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=17 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(`IDreponse`, NULL) INTO @ResteAVivre
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=18 AND
            `questionnaire_reponses`.`IDfamille`={IDfamille};

        SELECT IFNULL(SUM(`IDcivilite`!=4 AND `IDcivilite`!=5), 0) INTO @nbParents
        FROM
            `familles`
            LEFT OUTER JOIN `rattachements` USING(`IDfamille`)
            LEFT OUTER JOIN `individus` USING(`IDindividu`)
        WHERE `IDfamille`={IDfamille};

        INSERT INTO `questionnaire_reponses`
            (`IDreponse`, `IDquestion`, `IDfamille`, `reponse`)
        VALUES
            (@TotalRevenusP1, 14, {IDfamille}, @`SalaireP1` + @`ChomageP1` + @`CAFP1` + @`AutreRevenusP1`),
            (@TotalRevenusP2, 15, {IDfamille}, @`SalaireP2` + @`ChomageP2` + @`CAFP2` + @`AutreRevenusP2`),
            (@TotalRevenusFamille, 16, {IDfamille}, @`SalaireP1` + @`ChomageP1` + @`CAFP1` + \
@`AutreRevenusP1` + @`SalaireP2` + @`ChomageP2` + @`CAFP2` + @`AutreRevenusP2`),
            (@TotalCharges, 17, {IDfamille}, @`Loyer` + @`CreditImmo` + @`Charges` + @`Scolarite`),
            (@ResteAVivre, 18, {IDfamille}, (@`SalaireP1` + @`ChomageP1` + @`CAFP1` + \
@`AutreRevenusP1` + @`SalaireP2` + @`ChomageP2` + @`CAFP2` + @`AutreRevenusP2` - @`Loyer` - \
@`CreditImmo` - @`Charges` - @`Scolarite`) / ((@`nbParents` + @`NbEnfantsACharge`) * 30))
        ON DUPLICATE KEY UPDATE reponse=VALUES(reponse);
    """.format(IDfamille=IDfamille)
