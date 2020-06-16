# coding: utf8
import GestionDB
import wx

VERSION = "_v2.0.0"


def Extension():
    query = u'''
INSERT INTO `questionnaire_reponses`
    (`IDreponse`, `IDquestion`, `IDindividu`, `IDfamille`, `reponse`)
WITH
`p1` AS (
    SELECT
        `familles`.`IDfamille`,
        IFNULL(`t_SalaireP1`.`reponse`, 0)      AS `SalaireP1`,
        IFNULL(`t_ChomageP1`.`reponse`, 0)      AS `ChomageP1`,
        IFNULL(`t_CAFP1`.`reponse`, 0)          AS `CAFP1`,
        IFNULL(`t_AutreRevenusP1`.`reponse`, 0) AS `AutreRevenusP1`
    FROM
        `familles`
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_SalaireP1` ON (
            `t_SalaireP1`.`IDfamille`=`familles`.`IDfamille`
            AND `t_SalaireP1`.`IDquestion`=2
        )
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_ChomageP1` ON (
            `t_ChomageP1`.`IDfamille`=`familles`.`IDfamille`
            AND `t_ChomageP1`.`IDquestion`=3
        )
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_CAFP1` ON (
            `t_CAFP1`.`IDfamille`=`familles`.`IDfamille`
            AND `t_CAFP1`.`IDquestion`=4
        )
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_AutreRevenusP1` ON (
            `t_AutreRevenusP1`.`IDfamille`=`familles`.`IDfamille`
            AND `t_AutreRevenusP1`.`IDquestion`=5
        )
),
`p2` AS (
    SELECT
        `familles`.`IDfamille`,
        IFNULL(`t_SalaireP2`.`reponse`, 0)      AS `SalaireP2`,
        IFNULL(`t_ChomageP2`.`reponse`, 0)      AS `ChomageP2`,
        IFNULL(`t_CAFP2`.`reponse`, 0)          AS `CAFP2`,
        IFNULL(`t_AutreRevenusP2`.`reponse`, 0) AS `AutreRevenusP2`
    FROM
        `familles`
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_SalaireP2`
            ON (`t_SalaireP2`.`IDfamille`=`familles`.`IDfamille`
                AND `t_SalaireP2`.`IDquestion`=6)
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_ChomageP2`
            ON (`t_ChomageP2`.`IDfamille`=`familles`.`IDfamille`
                AND `t_ChomageP2`.`IDquestion`=7)
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_CAFP2`
            ON (`t_CAFP2`.`IDfamille`=`familles`.`IDfamille`
                AND `t_CAFP2`.`IDquestion`=8)
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_AutreRevenusP2`
            ON (`t_AutreRevenusP2`.`IDfamille`=`familles`.`IDfamille`
                AND `t_AutreRevenusP2`.`IDquestion`=9)
),
`charges` AS (
    SELECT
        `familles`.`IDfamille`,
        IFNULL(`t_Loyer`.`reponse`, 0)          AS `Loyer`,
        IFNULL(`t_CreditImmo`.`reponse`, 0)     AS `CreditImmo`,
        IFNULL(`t_Charges`.`reponse`, 0)        AS `Charges`,
        IFNULL(`t_Scolarite`.`reponse`, 0)      AS `Scolarite`
    FROM
        `familles`
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_Loyer` ON (
            `t_Loyer`.`IDfamille`=`familles`.`IDfamille`
            AND `t_Loyer`.`IDquestion`=10
        )
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_CreditImmo` ON (
            `t_CreditImmo`.`IDfamille`=`familles`.`IDfamille`
            AND `t_CreditImmo`.`IDquestion`=11
        )
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_Charges` ON (
            `t_Charges`.`IDfamille`=`familles`.`IDfamille`
            AND `t_Charges`.`IDquestion`=12
        )
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_Scolarite` ON (
            `t_Scolarite`.`IDfamille`=`familles`.`IDfamille`
            AND `t_Scolarite`.`IDquestion`=13
        )
),
`reponses_to_insert` AS (
    --
        -- Somme revenus parent 1
        SELECT
            `t_E_RP1`.                                                `IDreponse`,
            14                                                     AS `IDquestion`,
            NULL                                                   AS `IDindividu`,
            `p1`.                                                     `IDfamille`,
            `SalaireP1` + `ChomageP1` + `CAFP1` + `AutreRevenusP1` AS `reponse`
        FROM
            `p1`
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_RP1` ON (
                `t_E_RP1`.`IDfamille`=`p1`.`IDfamille`
                AND `t_E_RP1`.`IDquestion`=14
            )
    UNION
        -- Somme revenus parent 2
        SELECT
            `t_E_RP2`.                                                `IDreponse`,
            15                                                     AS `IDquestion`,
            NULL                                                   AS `IDindividu`,
            `p2`.                                                     `IDfamille`,
            `SalaireP2` + `ChomageP2` + `CAFP2` + `AutreRevenusP2` AS `reponse`
        FROM
            `p2`
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_RP2` ON (
                `t_E_RP2`.`IDfamille`=`p2`.`IDfamille`
                AND `t_E_RP2`.`IDquestion`=15
            )
    UNION
        -- Somme revenus foyer
        SELECT
            `t_E_RF`.    `IDreponse`,
            16        AS `IDquestion`,
            NULL      AS `IDindividu`,
            `p1`.        `IDfamille`,
            `SalaireP1` + `ChomageP1` + `CAFP1` + `AutreRevenusP1` +
                `SalaireP2` + `ChomageP2` + `CAFP2` + `AutreRevenusP2`
                      AS `reponse`
        FROM
            `p1` LEFT JOIN `p2` USING(`IDfamille`)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_RF` ON (
                `t_E_RF`.`IDfamille`=`p1`.`IDfamille`
                AND `t_E_RF`.`IDquestion`=16
            )
    UNION
        -- Somme charges foyer
        SELECT
            `t_E_Charges`.                                      `IDreponse`,
            17 AS                                               `IDquestion`,
            NULL AS                                             `IDindividu`,
            `charges`.                                          `IDfamille`,
            `Loyer` + `CreditImmo` + `Charges` + `Scolarite` AS `reponse`
        FROM
            `charges`
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_Charges` ON (
                `t_E_Charges`.`IDfamille`=`charges`.`IDfamille`
                AND `t_E_Charges`.`IDquestion`=17
            )
    UNION
        -- Reste A Vivre
        SELECT
            `t_RAV`.    `IDreponse`,
            18       AS `IDquestion`,
            NULL     AS `IDindividu`,
            `p1`.       `IDfamille`,
            (`SalaireP1` + `ChomageP1` + `CAFP1` + `AutreRevenusP1` +
                `SalaireP2` + `ChomageP2` + `CAFP2` + `AutreRevenusP2`
                - `Loyer` - `CreditImmo` - `Charges` - `Scolarite`
            ) / (
                -- personnes au foyer
                (`nbParents` + IFNULL(`t_nbEnfants`.`reponse`, 0))
                -- un mois/J
                * 30
            )
            AS          `reponse`
        FROM
            `p1`
            LEFT JOIN `p2` USING(`IDfamille`)
            LEFT JOIN `charges` USING(`IDfamille`)
            LEFT OUTER JOIN (
                SELECT
                    `IDfamille`,
                    IFNULL(SUM(`IDcivilite`!=4 AND `IDcivilite`!=5), 0) AS `nbParents`
                FROM
                    `familles`
                    LEFT OUTER JOIN `rattachements` USING(`IDfamille`)
                    LEFT OUTER JOIN `individus` USING(`IDindividu`)
                GROUP BY `IDfamille`
            ) AS `t_nbParents` USING(`IDfamille`)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_RAV` ON (
                `t_RAV`.`IDfamille`=`p1`.`IDfamille`
                AND `t_RAV`.`IDquestion`=18
            )
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_nbEnfants` ON (
                `t_nbEnfants`.`IDfamille`=`p1`.`IDfamille`
                AND `t_nbEnfants`.`IDquestion`=23
            )
    UNION
        -- Département
        SELECT
            `t_IDreponse`.                `IDreponse`,
            26                         AS `IDquestion`,
            `individus`.                  `IDindividu`,
            NULL                       AS `IDfamille`,
            LEFT(`t_cp`.`cp_resid`, 2) AS `reponse`
        FROM
            `individus`
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_IDreponse` ON (
                `t_IDreponse`.`IDindividu`=`individus`.`IDindividu`
                AND `t_IDreponse`.`IDquestion`=26
            )
            LEFT OUTER JOIN `individus` AS `t_cp` ON (
                `t_cp`.`IDindividu`=IFNULL(`individus`.`adresse_auto`, `individus`.`IDindividu`)
            )
        WHERE `t_cp`.`cp_resid` IS NOT NULL
)
SELECT `IDreponse`, `IDquestion`, `IDindividu`, `IDfamille`, `reponse`
    FROM `reponses_to_insert`
    WHERE `reponse` != 0
ON DUPLICATE KEY UPDATE `reponse`=VALUES(`reponse`);
    '''
    wait = wx.BusyInfo(u"Calcul en cours, merci de patienter…")
    success = Request(query)
    del wait

    if success:
        message(u"La procédure s'est déroulée avec succès.")
    else:
        message(u"Une erreur a interrompu la procédure.")


def message(text):
    dlg = wx.MessageDialog(
        parent=None,
        message=text,
        caption=u"Fin de procédure",
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()


def Request(Req):
    DB = GestionDB.DB()
    success = DB.ExecuterReq(Req)
    DB.ResultatReq()
    DB.Close()
    return success
