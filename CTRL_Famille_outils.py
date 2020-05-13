# coding: utf8


from Dlg import DLG_Famille
from Extensions_automatiques import message, addModule, hasModule
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
from collections import OrderedDict
import Chemins
import wx


list_outils = OrderedDict([
    (u"facture", [
        (u"Régler une facture", "Images/16x16/Codebarre.png", "self.MenuReglerFacture")
    ]),
    (u"relevé prestations", [
        (u"Editer un relevé des prestations", "Images/16x16/Euro.png", "self.MenuImprimerReleve")
    ]),
    (u"attestation de présence", [
        (u"Générer une attestation de présence",
            "Images/16x16/Generation.png", "self.MenuGenererAttestation"),
        (u"Liste des attestations de présences générées",
            "Images/16x16/Facture.png", "self.MenuListeAttestations")
    ]),
    (u"lettres de rappel", [
        (u"Générer une lettre de rappel",
            "Images/16x16/Generation.png", "self.MenuGenererRappel"),
        (u"Liste des lettres de rappel générées",
            "Images/16x16/Facture.png", "self.MenuListeRappels"),
    ]),
    (u"règlements", [
        (u"Liste des reçus de règlements édités",
            "Images/16x16/Note.png", "self.MenuListeRecus"),
        (u"Répartition de la ventilation par règlement",
            "Images/16x16/Repartition.png", "self.MenuRepartitionVentilation"),
    ]),
    (u"étiquettes", [
        (u"Edition d'étiquettes et de badges",
            "Images/16x16/Etiquette2.png", "self.MenuEditionEtiquettes"),
    ]),
    (u"log", [
        (u"Historique", "Images/16x16/Historique.png", "self.MenuHistorique"),
        (u"Chronologie", "Images/16x16/Timeline.png", "self.MenuChronologie"),
    ]),
    (u"export", [
        (u"Exporter les données de la famille au format XML",
            "Images/16x16/Document_export.png", "self.MenuExporter"),
    ]),
    (u"mail", [
        (u"Envoyer un Email avec l'éditeur d'Emails de Noethys",
            "Images/16x16/Editeur_email.png", "self.MenuEnvoyerMail"),
        (u"Envoyer un Email avec le client de messagerie par défaut",
            "Images/16x16/Editeur_email.png", "self.MenuEnvoyerMail"),
    ])
])


def Extension():
    if not hasModule("CTRL_Famille_outils"):
        message(u"L'extension est correctement installée, merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.")


def Initialisation():
    DLG_Famille.Dialog.OnBoutonOutils = OnBoutonOutils
    addModule("CTRL_Famille_outils")


def OnBoutonOutils(self, event):
    # Création du menu contextuel
    menuPop = UTILS_Adaptations.Menu()

    first = True
    for groupName, group in list_outils.iteritems():
        if first:
            first = False
        else:
            menuPop.AppendSeparator()

        for text, image, handler in group:
            ID = wx.Window.NewControlId()
            item = wx.MenuItem(menuPop, ID, _(text))
            bmp = wx.Bitmap(Chemins.GetStaticPath(image), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, eval(handler), id=ID)

    self.PopupMenu(menuPop)
    menuPop.Destroy()


def Ajouter(group, params):
    global list_outils
    if group not in list_outils:
        list_outils[group] = []
    list_outils[group].append(params)
