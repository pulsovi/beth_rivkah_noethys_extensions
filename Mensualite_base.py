# coding: utf8

import wx

from Extensions_automatiques import getQuery, message
from DLG_Famille_evaluer_mensualite import EvaluerMensualite, GetActivite


VERSION = "_v1.0.0"


def Extension():
    MajMensualiteBase()


def MajMensualiteBase():
    """
    Met a jour les réponses de questionnaire :
    - TODO individu / Résultats calculés / Montant de mensualité estimé (avant réduction)
    - famille / Résultats calculés / Montant de mensualité estimé (avant réduction)
    """
    activite = GetActivite()
    if activite is None:
        return
    IDactivite = activite[0]

    familles = getQuery("SELECT `IDfamille` FROM `familles`")

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

        reponses = getQuery("""
        SELECT `IDreponse`
        FROM `questionnaire_reponses`
        WHERE
            `IDquestion`=19
            AND
            `IDfamille`={IDfamille}
        """.format(IDfamille=IDfamille))
        IDreponse = None if not reponses else reponses[0][0]

        try:
            base = EvaluerMensualite(IDfamille, IDactivite)[0]
        except Exception:
            progress.Destroy()
            message(u"Erreur avec la famille" + str(getQuery("""
            SELECT `nom`, `prenom`
            FROM `rattachements`
            LEFT JOIN `individus` USING(`IDindividu`)
            WHERE `IDfamille`={IDfamille}
            """.format(IDfamille=IDfamille))))
            return

        if IDreponse:
            getQuery("""
            UPDATE `questionnaire_reponses`
            SET `reponse`={base}
            WHERE `IDreponse`={IDreponse}
            """.format(base=base, IDreponse=IDreponse))
        else:
            getQuery("""
            INSERT INTO `questionnaire_reponses`
                (`IDquestion`, `IDfamille`, `reponse`)
            VALUES (19, {IDfamille}, {base})
            """.format(IDfamille=IDfamille, base=base))

    progress.Destroy()
    message(u"La procédure s'est terminée avec succés.", u"Fin")
