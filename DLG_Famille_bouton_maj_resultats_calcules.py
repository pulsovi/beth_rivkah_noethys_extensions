# coding: utf8
from Dlg import DLG_Famille
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import Chemins
import GestionDB
import inspect
import wx

ID_CATEGORIES = {
    'RevenusP1': 1,
    'RevenusP2': 4,
    'Charges': 6,
    'Resultats': 7,
    'Convenu': 9,
    'Divers': 2,
}

ID_QUESTIONS = {
    'SalaireP1': 2,
    'ChomageP1': 3,
    'CAFP1': 4,
    'AutreRevenusP1': 5,
    'SalaireP2': 6,
    'ChomageP2': 7,
    'CAFP2': 8,
    'AutreRevenusP2': 9,
    'Loyer': 10,
    'CreditImmo': 11,
    'Charges': 12,
    'Scolarite': 13,
    'TotalRevenusP1': 14,
    'TotalRevenusP2': 15,
    'TotalRevenusFamille': 16,
    'TotalCharges': 17,
    'ResteAVivre': 18,
    'MensualiteStdFamille': 19,
    'MensualiteStdIndividu': 25,
    'MensualiteNego': 20,
    'NbMensualites': 21,
    'NbEnfantsACharge': 23,
}

infos = [
    'SalaireP1',
    'ChomageP1',
    'CAFP1',
    'AutreRevenusP1',
    'SalaireP2',
    'ChomageP2',
    'CAFP2',
    'AutreRevenusP2',
    'Loyer',
    'CreditImmo',
    'Charges',
    'Scolarite',
    'NbEnfantsACharge',
]

resultats = [
    'TotalRevenusP1',
    'TotalRevenusP2',
    'TotalRevenusFamille',
    'TotalCharges',
    'ResteAVivre',
]


def Extension():
    if isInstalled():
        message("Le bouton est en place")
    else:
        message("Ajout du bouton ...")
        Initialisation()


def Initialisation():
    DLG_Famille.Dialog.OnBoutonOutils = OnBoutonOutils
    DLG_Famille.Dialog.MenuMettreAJourLesResultatsCalcules = MenuMettreAJourLesResultatsCalcules


def OnBoutonOutils(self, event):
    # Création du menu contextuel
    menuPop = UTILS_Adaptations.Menu()

    # Item Régler une facture
    item = wx.MenuItem(menuPop, 40, _(u"Régler une facture"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Codebarre.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuReglerFacture, id=40)

    menuPop.AppendSeparator()

    # Item Editer un revelé de compte
    item = wx.MenuItem(menuPop, 90, _(u"Editer un relevé des prestations"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuImprimerReleve, id=90)

    menuPop.AppendSeparator()

    # Item Editer Attestation de présence
    item = wx.MenuItem(menuPop, 10, _(u"Générer une attestation de présence"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Generation.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuGenererAttestation, id=10)

    # Item Liste Attestation de présence
    item = wx.MenuItem(menuPop, 20, _(u"Liste des attestations de présences générées"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuListeAttestations, id=20)

    menuPop.AppendSeparator()

    # Item Editer Lettre de rappel
    item = wx.MenuItem(menuPop, 110, _(u"Générer une lettre de rappel"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Generation.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuGenererRappel, id=110)

    # Item Liste Lettres de rappel
    item = wx.MenuItem(menuPop, 120, _(u"Liste des lettres de rappel générées"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuListeRappels, id=120)

    menuPop.AppendSeparator()

    # Item Liste des reçus édités
    item = wx.MenuItem(menuPop, 300, _(u"Liste des reçus de règlements édités"))
    item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Note.png"), wx.BITMAP_TYPE_PNG))
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuListeRecus, id=300)

    item = wx.MenuItem(menuPop, 301, _(u"Répartition de la ventilation par règlement"))
    item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Repartition.png"), wx.BITMAP_TYPE_PNG))
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuRepartitionVentilation, id=301)

    menuPop.AppendSeparator()

    # Item Edition d'étiquettes et de badges
    item = wx.MenuItem(menuPop, 80, _(u"Edition d'étiquettes et de badges"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette2.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuEditionEtiquettes, id=80)

    menuPop.AppendSeparator()

    # Item Historique
    item = wx.MenuItem(menuPop, 30, _(u"Historique"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Historique.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuHistorique, id=30)

    item = wx.MenuItem(menuPop, 70, _(u"Chronologie"))
    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Timeline.png"), wx.BITMAP_TYPE_PNG)
    item.SetBitmap(bmp)
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuChronologie, id=70)

    menuPop.AppendSeparator()

    item = wx.MenuItem(menuPop, 85, _(u"Exporter les données de la famille au format XML"))
    item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_export.png"), wx.BITMAP_TYPE_PNG))
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuExporter, id=85)

    menuPop.AppendSeparator()

    item = wx.MenuItem(menuPop, 200, _(u"Envoyer un Email avec l'éditeur d'Emails de Noethys"))
    item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Editeur_email.png"), wx.BITMAP_TYPE_PNG))
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuEnvoyerMail, id=200)

    item = wx.MenuItem(menuPop, 210, _(u"Envoyer un Email avec le client de messagerie par défaut"))
    item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Editeur_email.png"), wx.BITMAP_TYPE_PNG))
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuEnvoyerMail, id=210)

    menuPop.AppendSeparator()

    ID_MAJ_CALC = wx.Window.NewControlId()
    item = wx.MenuItem(menuPop, ID_MAJ_CALC, _(u"Mettre à jour les résultats calculés"))
    item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
    menuPop.AppendItem(item)
    self.Bind(wx.EVT_MENU, self.MenuMettreAJourLesResultatsCalcules, id=ID_MAJ_CALC)

    self.PopupMenu(menuPop)
    menuPop.Destroy()


def MenuMettreAJourLesResultatsCalcules(self, event):
    notebook = self.notebook
    page = notebook.dictPages["questionnaire"]["ctrl"]
    # page.majEffectuee = False
    page.Sauvegarde()
    # page.MAJ()

    query = ""
    # recuperation des informations de base
    prepare = """
        SELECT IFNULL(`reponse`, 0) INTO @{varName}
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`={idQuestion} AND
            `questionnaire_reponses`.`IDfamille`={idFamille};
        """
    for question in infos:
        query += prepare.format(
            varName=question,
            idQuestion=ID_QUESTIONS[question],
            idFamille=self.IDfamille
        )

    # recuperation des ID de reponse
    prepare = """
        SELECT IFNULL(`IDreponse`, NULL) INTO @{varName}
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`={idQuestion} AND
            `questionnaire_reponses`.`IDfamille`={idFamille};
        """
    for question in resultats:
        query += prepare.format(
            varName=question,
            idQuestion=ID_QUESTIONS[question],
            idFamille=self.IDfamille
        )

    # recuperation des informations supplementaires
    query += """
        SELECT IFNULL(SUM(`IDcivilite`!=4 AND `IDcivilite`!=5), 0) INTO @nbParents
        FROM
            `familles`
            LEFT OUTER JOIN `rattachements` USING(`IDfamille`)
            LEFT OUTER JOIN `individus` USING(`IDindividu`)
        WHERE `IDfamille`={idFamille};
        """.format(idFamille=self.IDfamille)

    # envoi des reponses
    query += """
        INSERT INTO `questionnaire_reponses`
            (`IDreponse`, `IDquestion`, `IDfamille`, `reponse`)
        VALUES
        """
    prepare = """
            (@{IDreponse}, {IDquestion}, {IDfamille}, {reponse}){comma}
        """
    query += prepare.format(
        IDreponse='TotalRevenusP1',
        IDquestion=ID_QUESTIONS['TotalRevenusP1'],
        IDfamille=self.IDfamille,
        reponse='@`SalaireP1` + @`ChomageP1` + @`CAFP1` + @`AutreRevenusP1`',
        comma=','
    )
    query += prepare.format(
        IDreponse='TotalRevenusP2',
        IDquestion=ID_QUESTIONS['TotalRevenusP2'],
        IDfamille=self.IDfamille,
        reponse='@`SalaireP2` + @`ChomageP2` + @`CAFP2` + @`AutreRevenusP2`',
        comma=','
    )
    query += prepare.format(
        IDreponse='TotalRevenusFamille',
        IDquestion=ID_QUESTIONS['TotalRevenusFamille'],
        IDfamille=self.IDfamille,
        reponse='@`SalaireP1` + @`ChomageP1` + @`CAFP1` + @`AutreRevenusP1` + \
            @`SalaireP2` + @`ChomageP2` + @`CAFP2` + @`AutreRevenusP2`',
        comma=','
    )
    query += prepare.format(
        IDreponse='TotalCharges',
        IDquestion=ID_QUESTIONS['TotalCharges'],
        IDfamille=self.IDfamille,
        reponse='@`Loyer` + @`CreditImmo` + @`Charges` + @`Scolarite`',
        comma=','
    )
    query += prepare.format(
        IDreponse='ResteAVivre',
        IDquestion=ID_QUESTIONS['ResteAVivre'],
        IDfamille=self.IDfamille,
        reponse='( \
                @`SalaireP1` + @`ChomageP1` + @`CAFP1` + @`AutreRevenusP1` + \
                @`SalaireP2` + @`ChomageP2` + @`CAFP2` + @`AutreRevenusP2` \
                - @`Loyer` - @`CreditImmo` - @`Charges` - @`Scolarite` \
            ) / ((@`nbParents` + @`NbEnfantsACharge`) * 30)',
        comma=''
    )
    query += 'ON DUPLICATE KEY UPDATE reponse=VALUES(reponse);\n'
    DB = GestionDB.DB()
    DB.ExecuterReq(query)
    res = DB.ResultatReq()
    DB.Close()
    page.majEffectuee = False
    wx.CallLater(1, page.MAJ)


def message(text, title=u"Information"):
    dlg = wx.MessageDialog(
        parent=None,
        message=text,
        caption=title,
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()


def isInstalled():
    buttonInstalled = \
        inspect.getsource(DLG_Famille.Dialog.OnBoutonOutils) == \
        inspect.getsource(OnBoutonOutils)
    eventHandlerInstalled = \
        inspect.getsource(DLG_Famille.Dialog.MenuMettreAJourLesResultatsCalcules) == \
        inspect.getsource(MenuMettreAJourLesResultatsCalcules)
    return buttonInstalled and eventHandlerInstalled
