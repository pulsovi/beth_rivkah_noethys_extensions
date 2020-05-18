# coding:utf8
from Dlg import DLG_Famille
from Utils import UTILS_Utilisateurs
import GestionDB
import wx


def Extension():
    res = Request(u'''
SELECT
    `Anomalie`,
    `anomalies`.`IDfamille`,
    `anomalies`.`IDindividu`,
    `individus`.`nom`,
    `individus`.`prenom`
FROM
    (
        SELECT
            'Adulte inscrit en (activité) Scolarité' AS `Anomalie`,
            `IDindividu`,
            NULL AS `IDfamille`
        FROM
            `individus`
            INNER JOIN `inscriptions` USING(`IDindividu`)
        WHERE `IDcivilite`!=4 AND `IDcivilite`!=5
    UNION
        SELECT
            "nombre d'enfants inscrits en Scolartité sur Noethys \
supérieur au nombre d'enfants inscrits à Beth Rivkah renseigné \
dans le questionnaire famille" AS `Anomalie`,
            NULL AS `IDindividu`,
            `IDfamille`
        FROM
            (
                SELECT
                    `familles`.`IDfamille`,
                    IFNULL(`t_nbEnfantsBR`.`reponse`, 0) AS `nbEnfantsBR`,
                    COUNT(`inscriptions`.`IDgroupe`) AS `nbInscriptions`
                FROM
                    `familles`
                    LEFT JOIN `inscriptions` USING(`IDfamille`)
                    LEFT JOIN `questionnaire_reponses` AS `t_nbEnfantsBR` ON (
                        `t_nbEnfantsBR`.`IDfamille`=`familles`.`IDfamille`
                        AND `t_nbEnfantsBR`.`IDquestion`=24
                    )
                GROUP BY `familles`.`IDfamille`
            ) AS `comparison`
        WHERE `nbEnfantsBR`<`nbInscriptions`
    UNION
        SELECT
            'Deux quotients familiaux concurents le même jour' AS `Anomalie`,
            NULL AS `IDindividu`,
            `IDfamille`
        FROM
            `quotients` AS `quotient1`
            LEFT JOIN `quotients` AS `quotient2` USING(`IDfamille`)
        WHERE
            `quotient1`.`date_fin`>=`quotient2`.`date_debut`
            AND
            `quotient1`.`date_debut`<=`quotient2`.`date_fin`
            AND
            `quotient1`.`IDquotient`!=`quotient2`.`IDquotient`
        GROUP BY `IDfamille`
    UNION
        SELECT
            'Régime incompatible avec la classe' AS `Anomalie`,
            `IDindividu`,
            NULL AS `IDfamille`
        FROM
            `scolarite`
            LEFT JOIN `questionnaire_reponses` USING(`IDindividu`)
        WHERE
        `questionnaire_reponses`.`IDquestion`=27
        AND
        `questionnaire_reponses`.`reponse`=17
        AND
        `scolarite`.`IDniveau`<6
    ) AS `anomalies`
    LEFT JOIN `rattachements` USING(`IDfamille`)
    LEFT JOIN `individus` ON (
        `anomalies`.`IDindividu`=`individus`.`IDindividu`
        OR
        `rattachements`.`IDindividu`=`individus`.`IDindividu`
    )
    WHERE
        `individus`.`IDindividu`=`anomalies`.`IDindividu`
        OR (
            `anomalies`.`IDindividu` IS NULL
            AND
            `individus`.`IDcivilite`!=4
            AND
            `individus`.`IDcivilite`!=5
        )
GROUP BY
    `Anomalie`,
    `IDfamille`,
    `individus`.`IDindividu`
    ''')
    dlg = wx.FileDialog(
        None,
        message=u"Veuillez sélectionner le répertoire de destination et le nom du fichier",
        wildcard=".csv",
        defaultFile="anomalies.csv",
    )
    if dlg.ShowModal() == wx.ID_CANCEL:
        return
    pathname = dlg.GetPath()
    output = stringifyErrorList(res)
    file = open(pathname, 'wb')
    file.write(output.encode('1252'))
    file.close()
    dlg = wx.MessageDialog(
        parent=None,
        message=u"La procédure s'est déroulée avec succès",
        caption=u"Fin de procédure",
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()


def OuvrirFicheFamille(IDfamille):
    droit = UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel(
        "familles_fiche", "consulter")
    if not droit:
        return
    dlg = DLG_Famille.Dialog(None, IDfamille=IDfamille)
    dlg.ShowModal()
    dlg.Destroy()


def Request(Req):
    DB = GestionDB.DB()
    DB.ExecuterReq(Req)
    res = DB.ResultatReq()
    DB.Close()
    return res


def stringifyErrorList(list):
    output = u'Erreur;Référence\n'
    lastErr = (None, None)
    for erreur, IDfamille, IDindividu, nom, prenom in list:
        message = u'"' + erreur + u'"'
        ref = nom + u' ' + prenom
        if IDindividu is None:
            if lastErr[1] == IDfamille and lastErr[0] == erreur:
                continue
            lastErr = (erreur, IDfamille)
            ref = u'"famille ' + ref + u'"'
        output += (
            message
            + u';'
            + ref
            + u';'
            + str(IDindividu if IDfamille is None else IDfamille)
            + u'\n'
        )
    return output
