# coding: utf8
"""
Met a jour les réponses de questionnaire :
- individu / Résultats calculés / Montant de mensualité estimé (avant réduction)
- famille / Résultats calculés / Montant de mensualité estimé (avant réduction) / Montant fixé
"""

import wx

from Extensions_automatiques import getQuery, message, printErr
from CTRL_Famille_outils import FAMILLE, INDIVIDU
from DLG_Famille_evaluer_mensualite import Inscriptions, GetActivite

VERSION = "_v1.0.1"


def Extension():
    MajMensualiteBase()


def MajMensualiteBase():
    inscriptions = Inscriptions()

    activite = GetActivite(db=inscriptions)
    if activite is None:
        return
    IDactivite = activite[0]

    familles = inscriptions.GetResponse("SELECT `IDfamille` FROM `familles`")

    total = len(familles)
    current = 0
    progress = wx.ProgressDialog(
        title=u"Mise à jour des tarifs de base …",
        message=u"{current}/{total}".format(current=current, total=total),
        maximum=total,
        style=wx.PD_APP_MODAL | wx.PD_SMOOTH | wx.PD_CAN_SKIP |
        wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE
    )

    for IDfamille, in familles:
        current += 1
        ok, skip = progress.Update(
            value=current,
            newmsg=u"{current}/{total}".format(current=current, total=total),
        )
        if skip:
            progress.Destroy()
            return

        try:
            brut, mensualites, coeffBr, coeffDeg, enfants = inscriptions.EvaluerMensualite(
                IDfamille, IDactivite)
            quotient = inscriptions.GetQuotient(IDfamille, IDactivite)
            coeff = coeffBr * coeffDeg
            inscriptions.AddValue(19, IDfamille, inscriptions.CalculateTaux(brut, mensualites))
            inscriptions.AddValue(30, IDfamille,
                inscriptions.CalculateTaux(brut, mensualites, coeff))
            if quotient is not None:
                inscriptions.AddValue(20, IDfamille, round(brut * quotient[4], 2))
            for id, prenom, taux in enfants:
                inscriptions.AddValue(25, id,
                    inscriptions.CalculateTaux(taux, mensualites), INDIVIDU)
                inscriptions.AddValue(31, id,
                    inscriptions.CalculateTaux(taux, mensualites, coeff), INDIVIDU)
            inscriptions.Execute()
        except Exception:
            progress.Destroy()
            printErr(u"Erreur avec la famille" + str(getQuery("""
            SELECT `nom`, `prenom`
            FROM `rattachements`
            LEFT JOIN `individus` USING(`IDindividu`)
            WHERE `IDfamille`={IDfamille}
            """.format(IDfamille=IDfamille))))
            return

    progress.Destroy()
    message(u"La procédure s'est terminée avec succés.", u"Fin")


def updateFamille(IDfamille, reponse):
    updateReponse(IDfamille, reponse, FAMILLE)


def updateIndividu(IDfamille, reponse):
    updateReponse(IDfamille, reponse, INDIVIDU)


def updateReponse(ID, reponse, type=FAMILLE):
    idstring = "IDfamille" if type == FAMILLE else "IDindividu"
    IDquestion = 19 if type == FAMILLE else 25
    reponses = getQuery("""
    SELECT `IDreponse`
    FROM `questionnaire_reponses`
    WHERE
        `IDquestion`={IDquestion}
        AND
        `{idstring}`={ID}
    """.format(ID=ID, IDquestion=IDquestion, idstring=idstring))
    IDreponse = None if not reponses else reponses[0][0]

    if IDreponse:
        getQuery("""
        UPDATE `questionnaire_reponses`
        SET `reponse`={reponse}
        WHERE `IDreponse`={IDreponse}
        """.format(reponse=reponse, IDreponse=IDreponse))
    else:
        getQuery("""
        INSERT INTO `questionnaire_reponses`
            (`IDquestion`, `{idstring}`, `reponse`)
        VALUES ({IDquestion}, {ID}, {reponse})
        """.format(
            ID=ID,
            reponse=reponse,
            IDquestion=IDquestion,
            idstring=idstring
        ))
