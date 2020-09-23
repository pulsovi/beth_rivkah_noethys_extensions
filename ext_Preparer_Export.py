# coding: utf8
"""
Met a jour les réponses de questionnaire :
- individu / Résultats calculés / Montant de mensualité estimé (avant réduction)
- famille / Résultats calculés / Montant de mensualité estimé (avant réduction) / Montant fixé
"""

import wx
import unicodedata

from Utils import UTILS_Titulaires

from ext_Extensions_automatiques import getQuery, message, printErr
from ext_CTRL_Famille_outils import FAMILLE, INDIVIDU
from ext_DLG_Famille_evaluer_mensualite import Inscriptions, GetActivite

VERSION = "_v2.3.0"


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
        style=wx.PD_APP_MODAL | wx.PD_SMOOTH | wx.PD_CAN_SKIP | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE
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
            # mensualité estimée avant réductions
            inscriptions.AddValue(19, IDfamille, inscriptions.CalculateTaux(brut, mensualites))
            # coefficient de réduction "Intervenant BR"
            inscriptions.AddValue(43, IDfamille, coeffBr)
            # coefficient de réduction "Tarif dégressif"
            inscriptions.AddValue(44, IDfamille, coeffDeg)
            # coefficient de réduction global
            inscriptions.AddValue(45, IDfamille, coeff)
            # mensualité estimée après réductions
            inscriptions.AddValue(30, IDfamille,
                inscriptions.CalculateTaux(brut, mensualites, coeff))
            if quotient is not None:
                # mensualité fixée
                inscriptions.AddValue(20, IDfamille, round(brut * quotient[4], 2))
            fillCompteClient(IDfamille, inscriptions)
            # Enfants
            for id, prenom, taux in enfants:
                # mensualité estimée avant réductions
                inscriptions.AddValue(25, id,
                    inscriptions.CalculateTaux(taux, mensualites), INDIVIDU)
                # mensualité estimée après réductions
                inscriptions.AddValue(31, id,
                    inscriptions.CalculateTaux(taux, mensualites, coeff), INDIVIDU)
                if quotient is not None:
                    # mensualité fixée
                    inscriptions.AddValue(42, id, round(taux * quotient[4], 2), INDIVIDU)
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


def fillCompteClient(IDfamille, db):
    if db.GetResponse("""
        SELECT * FROM `questionnaire_reponses`
        WHERE `IDquestion`=46 AND `IDfamille`={IDfamille}
    """.format(IDfamille=IDfamille)):
        return
    titulaires = UTILS_Titulaires.GetTitulaires([IDfamille])[IDfamille]["listeTitulaires"]
    code = u"" + titulaires[0]["nom"]
    for titulaire in titulaires:
        code += titulaire["prenom"]
    code = remove_accents(code.upper()).replace(" ", "")
    indice = 0
    code10 = code[:10]
    while db.GetResponse("""
        SELECT * FROM `questionnaire_reponses`
        WHERE `IDquestion`=46 AND `reponse`="{code10}"
    """.format(code10=code10)):
        indice += 1
        code10 = code[:10 - len(str(indice))] + str(indice)
    db.AddValue(46, IDfamille, code10, FAMILLE)


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


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
