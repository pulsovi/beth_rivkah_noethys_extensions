# coding: utf8
import GestionDB
import wx


def Extension():
    Request(u'''
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
    WITH
    `infos_familles` AS (
        SELECT
            `familles`.`IDfamille` AS `IDfamille`,
            IFNULL(`t_mensualite_fix`.`reponse`, 0) AS `montantFix`,
            MIN(`IDquotient`)      AS `active_quotient_id`
        FROM
            `familles`
            LEFT OUTER JOIN `quotients` ON (
                `familles`.`IDfamille`=`quotients`.`IDfamille`
                AND `quotients`.`date_debut`<=CURDATE( )
                AND (
                    `quotients`.`date_fin` IS NULL
                    OR `quotients`.`date_fin`>=CURDATE( )
                )
            )
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_mensualite_fix`
                ON (`t_mensualite_fix`.`IDfamille`=`familles`.`IDfamille`
                    AND `t_mensualite_fix`.`IDquestion`=20)
        GROUP BY `familles`.`IDfamille`
    ),
    `tarifs_scolarites` AS (
        SELECT 1 /*Maternelle*/ AS `IDgroupe`, 3600 AS `tarif` UNION
        SELECT 2 /*Primaire  */ AS `IDgroupe`, 3600 AS `tarif` UNION
        SELECT 3 /*College   */ AS `IDgroupe`, 4080 AS `tarif` UNION
        SELECT 4 /*Lycee     */ AS `IDgroupe`, 4200 AS `tarif` UNION
        SELECT 5 /*Lycee Pro */ AS `IDgroupe`, 4200 AS `tarif`
    ),
    `source_quotients` AS (
        SELECT
            `infos_familles`.`IDfamille`                                     AS `IDfamille`,
            `infos_familles`.`active_quotient_id`                            AS `IDquotient`,
            CONVERT(1000000*`infos_familles`.`montantFix`/SUM(`tarif`), INT) AS `quotient`,
            `infos_familles`.`montantFix`                                    AS `revenu`,
            IFNULL(`quotients`.`quotient`, 0)                                AS `actual_quotient`,
            IFNULL(`quotients`.`revenu`, 0)                                  AS `actual_revenu`
        FROM
            `infos_familles`
            INNER JOIN `inscriptions` USING(`IDfamille`)
            INNER JOIN `tarifs_scolarites` USING(`IDgroupe`)
            LEFT OUTER JOIN `quotients` ON (
                `infos_familles`.`IDfamille`=`quotients`.`IDfamille`
                AND `quotients`.`IDquotient`=`infos_familles`.`active_quotient_id`)
        GROUP BY `infos_familles`.`IDfamille`
    )
    -- fermer les quotients ouverts
        SELECT
            `IDquotient`,
            NULL,
            NULL,
            CURDATE( ) - INTERVAL 1 DAY,
            NULL,
            NULL,
            NULL,
            NULL
        FROM
            `source_quotients`
        WHERE
            (`quotient`!=`actual_quotient` OR `revenu`!=`actual_revenu`)
            AND `IDquotient` IS NOT NULL
    UNION
        SELECT
            NULL,
            `IDfamille`,
            CURDATE( ),
            '2050-01-01',
            `quotient`,
            '',
            `revenu`,
            1
        FROM
            `source_quotients`
        WHERE
            `quotient`!=`actual_quotient` OR `revenu`!=`actual_revenu`
ON DUPLICATE KEY UPDATE `date_fin`=VALUES(`date_fin`);
    ''')
    dlg = wx.MessageDialog(
        parent=None,
        message=u"La procédure s'est déroulée avec succès",
        caption=u"Fin de procédure",
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()


def Request(Req):
    DB = GestionDB.DB()
    DB.ExecuterReq(Req)
    res = DB.ResultatReq()
    DB.Close()
    return res
