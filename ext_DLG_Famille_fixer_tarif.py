# coding: utf8
"""
Le coefficient et les tarifs obeissent à ces équations
- Tarif activité = tarif annuel BR ÷ 1 000 000
- Brut = tarif activite
- Quotient = tarif annuel fixé ÷ tarif activite ÷ mensualites
- Quotient = tarif mensuel fixé ÷ tarif activite
- Tarif payé mensuellement = Quotient × tarif activite
- Pour une famille au tarif standard, le quotient vaut 1 000 000 ÷ mensualites
"""


# exposes:
#     Extension and Initialisation only

from Ctrl import CTRL_Bouton_image, CTRL_Saisie_euros
from datetime import date
from Dlg import DLG_Famille, DLG_Saisie_quotient
from Utils.UTILS_Traduction import _
import wx

from ext_Extensions_automatiques import message, addModule, hasModule
from ext_CTRL_Famille_outils import Ajouter as AjouterOutil, CTRL_ANNEE
from ext_DLG_Famille_evaluer_mensualite import Inscriptions

VERSION = "_v2.0.1"


def Extension():
    if not hasModule(__name__ + VERSION):
        message(u"L'extension est correctement installée, "
            u"merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.", __name__ + VERSION)


def Initialisation():
    # Agrandir le cadre Observations dans la saisie de quotient
    DLG_Saisie_quotient.Dialog.NoethysDoLayout = DLG_Saisie_quotient.Dialog._Dialog__do_layout
    DLG_Saisie_quotient.Dialog._Dialog__do_layout = DoLayout
    # Ajouter le bouton Fixer tarif
    DLG_Famille.Dialog.MenuFixerTarif = MenuFixerTarif
    AjouterOutil("bethrivkah", (u"Fixer le tarif de mensualité",
        "Images/16x16/Euro.png", "self.MenuFixerTarif"))
    # Enregistrer le module
    addModule(__name__ + VERSION)


def DoLayout(self):
    """Agrandit le cadre Observations dans la saisie de quotient"""
    self.ctrl_observations.SetMinSize((-1, 100))
    self.NoethysDoLayout()


def MenuFixerTarif(self, event):
    inscriptions = Inscriptions()

    # recuperer la saisie utilisateur pour l'année et le montant
    dlg = Dialog(None, db=inscriptions)
    dlg.ShowModal()
    activite = dlg.GetAnnee()
    montant = dlg.GetMontant()
    dlg.Destroy()

    if not activite or not montant:
        return

    # calculer le nouveau quotient et récupérer le quotient actif
    IDactivite, nom, date_debut, date_fin = activite

    brut, mensualites, coeffBR, coeffDeg, enfants = inscriptions.EvaluerMensualite(
        self.IDfamille, IDactivite)

    if not brut:
        message(
            u"Aucun enfant de cette famille n'est inscrit à cette activité",
            u"Opération impossible",
            wx.OK | wx.ICON_ERROR
        )
        return

    quotient = int(round(montant / brut))
    quotientActif = GetQuotientActif(inscriptions, self.IDfamille, date_debut, date_fin)

    # pas de redondances
    if quotientActif and quotient == int(quotientActif[4]):
        message(u"Ce montant est déjà fixé.")
        return

    # stopper le quotient actif en BDD
    values = u""
    if quotientActif:
        date_debut = date.today().isoformat()
        values += u"""
        ({IDquotient}, NULL, NULL, '{date_fin}', NULL, NULL, NULL, NULL),
        """.format(
            IDquotient=quotientActif[0],
            date_fin=date.fromordinal(date.today().toordinal() - 1).isoformat()
        )

    # nouveau quotient en BDD
    observations = u"""Pour une mensualite totale de {montant}€ :""".format(montant=montant)
    for id, prenom, taux in enfants:
        observations += u"\\n - {prenom}: {montant}".format(
            prenom=prenom, montant=round(montant * taux / brut, 2))
    values += u"""
    (NULL, {IDfamille}, '{date_debut}', '{date_fin}', {quotient}, "{observations}", NULL, 1)
    """.format(
        IDfamille=self.IDfamille,
        date_debut=date_debut,
        date_fin=date_fin,
        quotient=quotient,
        observations=observations,
    )

    # execution
    query = u"""
    INSERT INTO `quotients` (
        `IDquotient`,
        `IDfamille`,
        `date_debut`,
        `date_fin`,
        `quotient`,
        `observations`,
        `revenu`,
        `IDtype_quotient`
    )
    VALUES
        {values}
    ON DUPLICATE KEY UPDATE
        `date_fin`=VALUES(`date_fin`)
    """.format(values=values)
    inscriptions.ExecuterReq(query)
    inscriptions.Close()
    message(u"""Le montant a été fixé.
Merci de consulter le volet QF/Revenus pour vérifier la période d'application.""")
    OuvrirQF(self)


def OuvrirQF(self):
    notebook = self.notebook
    notebook.AffichePage("quotients")
    notebook.MAJpage("quotients")


def GetQuotientActif(DB, IDfamille, debut, fin):
    query = """
    SELECT
        *
    FROM
        `quotients`
    WHERE
        `IDfamille`={IDfamille}
        AND `date_debut`<='{debut}'
        AND (
            `date_fin` IS NULL
            OR `date_fin`>='{fin}'
        )
    LIMIT 1
    """.format(IDfamille=IDfamille, debut=date.today(), fin=fin)
    resultats = DB.GetResponse(query)
    if resultats:
        return resultats[0]
    return None


class Dialog(wx.Dialog):
    def __init__(self, parent, id=-1, title=_(u"Choix année scolaire"), db=None):
        wx.Dialog.__init__(self, parent, id, title, name="DLG_annee_montant")
        self.parent = parent
        self.staticbox = wx.StaticBox(self, -1, "")
        self.label = wx.StaticText(self, -1, _(u"Veuillez choisir l'année et saisir le montant."))
        self.label_annee = wx.StaticText(self, -1, _(u"Année scolaire :"))
        self.ctrl_annee = CTRL_ANNEE(self, db=db)
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
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
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=2, hgap=2)
        grid_sizer_contenu.Add(self.label_annee, 1, wx.ALL, 0)
        grid_sizer_contenu.Add(self.ctrl_annee, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_montant, 1, wx.ALL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 1, wx.EXPAND, 0)
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
        return self.ctrl_annee.GetAnnee()

    def GetMontant(self):
        return self.ctrl_montant.GetMontant()
