# coding: utf8
import GestionDB
import wx

ID_QUESTION = {
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
    'E_RP1': 14,
    'E_RP2': 15,
    'E_RF': 16,
    'E_Charges': 17
}


def Extension():
    Request('''
INSERT INTO `questionnaire_reponses`
    (`IDreponse`, `IDquestion`, `IDfamille`, `reponse`)
    WITH
    `infos_familles` AS (
        SELECT
            `familles`.`IDfamille`,
            IFNULL(`t_SalaireP1`.`reponse`, 0)      AS `SalaireP1`,
            IFNULL(`t_ChomageP1`.`reponse`, 0)      AS `ChomageP1`,
            IFNULL(`t_CAFP1`.`reponse`, 0)          AS `CAFP1`,
            IFNULL(`t_AutreRevenusP1`.`reponse`, 0) AS `AutreRevenusP1`,
            `t_E_RP1`.`IDreponse`                   AS `ID_E_RP1`,
            IFNULL(`t_SalaireP2`.`reponse`, 0)      AS `SalaireP2`,
            IFNULL(`t_ChomageP2`.`reponse`, 0)      AS `ChomageP2`,
            IFNULL(`t_CAFP2`.`reponse`, 0)          AS `CAFP2`,
            `t_E_RP2`.`IDreponse`                   AS `ID_E_RP2`,
            `t_E_RF`.`IDreponse`                    AS `ID_E_RF`,
            IFNULL(`t_AutreRevenusP2`.`reponse`, 0) AS `AutreRevenusP2`,
            IFNULL(`t_Loyer`.`reponse`, 0)          AS `Loyer`,
            IFNULL(`t_CreditImmo`.`reponse`, 0)     AS `CreditImmo`,
            IFNULL(`t_Charges`.`reponse`, 0)        AS `Charges`,
            IFNULL(`t_Scolarite`.`reponse`, 0)      AS `Scolarite`,
            `t_E_Charges`.`IDreponse`               AS `ID_E_Charges`,
            `t_RAV`.`IDreponse`                     AS `ID_RAV`,
            IFNULL(`t_nbEnfants`.`reponse`, 0)      AS `nbEnfants`,
            IFNULL(`t_nbParents`.`nbParents`, 0)    AS `nbParents`,
            IFNULL(`t_nbEnfants`.`reponse`, 0)
            + IFNULL(`t_nbParents`.`nbParents`, 0)  AS `AuFoyer`
        FROM
            `familles`
            LEFT OUTER JOIN (SELECT
                        `IDfamille`,
                        SUM(`IDcivilite` != 4 AND `IDcivilite` != 5) AS `nbParents`
                    FROM
                        `familles`
                        LEFT OUTER JOIN `rattachements` USING(`IDfamille`)
                        LEFT OUTER JOIN `individus` USING(`IDindividu`)
                    GROUP BY `IDfamille`) AS `t_nbParents`
                USING(`IDfamille`)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_SalaireP1`
                ON (`t_SalaireP1`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_SalaireP1`.`IDquestion` = 2)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_ChomageP1`
                ON (`t_ChomageP1`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_ChomageP1`.`IDquestion` = 3)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_CAFP1`
                ON (`t_CAFP1`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_CAFP1`.`IDquestion` = 4)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_AutreRevenusP1`
                ON (`t_AutreRevenusP1`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_AutreRevenusP1`.`IDquestion` = 5)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_SalaireP2`
                ON (`t_SalaireP2`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_SalaireP2`.`IDquestion` = 6)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_ChomageP2`
                ON (`t_ChomageP2`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_ChomageP2`.`IDquestion` = 7)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_CAFP2`
                ON (`t_CAFP2`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_CAFP2`.`IDquestion` = 8)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_AutreRevenusP2`
                ON (`t_AutreRevenusP2`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_AutreRevenusP2`.`IDquestion` = 9)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_Loyer`
                ON (`t_Loyer`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_Loyer`.`IDquestion` = 10)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_CreditImmo`
                ON (`t_CreditImmo`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_CreditImmo`.`IDquestion` = 11)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_Charges`
                ON (`t_Charges`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_Charges`.`IDquestion` = 12)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_Scolarite`
                ON (`t_Scolarite`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_Scolarite`.`IDquestion` = 13)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_RP1`
                ON (`t_E_RP1`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_E_RP1`.`IDquestion` = 14)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_RP2`
                ON (`t_E_RP2`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_E_RP2`.`IDquestion` = 15)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_RF`
                ON (`t_E_RF`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_E_RF`.`IDquestion` = 16)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_E_Charges`
                ON (`t_E_Charges`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_E_Charges`.`IDquestion` = 17)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_RAV`
                ON (`t_RAV`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_RAV`.`IDquestion` = 18)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_nbEnfants`
                ON (`t_nbEnfants`.`IDfamille` = `familles`.`IDfamille`
                    AND `t_nbEnfants`.`IDquestion` = 23)
    ),
    `tarifs_scolarites` AS (
        SELECT
            `nbEnfantsBR`,
            `section`,
            IF(`nbEnfantsBR` = 1, `tarif`, `tarif` * (100 - (4 * `nbEnfantsBR`)) / 100) AS `tarif`
        FROM
            (
                SELECT 1 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 2 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 3 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 4 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 5 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 6 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 7 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 8 AS `section`, 3600 AS `tarif` UNION ALL
                SELECT 9 AS `section`, 3600 AS `tarif` UNION ALL

                SELECT 10 AS `section`, 4080 AS `tarif` UNION ALL
                SELECT 11 AS `section`, 4080 AS `tarif` UNION ALL
                SELECT 12 AS `section`, 4080 AS `tarif` UNION ALL
                SELECT 13 AS `section`, 4080 AS `tarif` UNION ALL

                SELECT 14 AS `section`, 4200 AS `tarif` UNION ALL
                SELECT 15 AS `section`, 4200 AS `tarif` UNION ALL
                SELECT 16 AS `section`, 4200 AS `tarif`
            ) AS `tarif`

            LEFT JOIN (
                SELECT 1 AS `nbEnfantsBR` UNION ALL
                SELECT 2 AS `nbEnfantsBR` UNION ALL
                SELECT 3 AS `nbEnfantsBR` UNION ALL
                SELECT 4 AS `nbEnfantsBR` UNION ALL
                SELECT 5 AS `nbEnfantsBR` UNION ALL
                SELECT 6 AS `nbEnfantsBR`
            ) AS `nbEnfants`
                ON 1=1
    ),
    `reponses_to_insert` AS (
        --
            -- Somme revenus parent 1
            SELECT
                `ID_E_RP1` AS `IDreponse`,
                14 AS `IDquestion`,
                `IDfamille`,
                `SalaireP1` + `ChomageP1` + `CAFP1` + `AutreRevenusP1` AS `reponse`
            FROM `infos_familles`
        UNION
            -- Somme revenus parent 2
            SELECT
                `ID_E_RP2` AS `IDreponse`,
                15 AS `IDquestion`,
                `IDfamille`,
                `SalaireP2` + `ChomageP2` + `CAFP2` + `AutreRevenusP2` AS `reponse`
            FROM `infos_familles`
        UNION
            -- Somme revenus foyer
            SELECT
                `ID_E_RF` AS `IDreponse`,
                16 AS `IDquestion`,
                `IDfamille`,
                `SalaireP1` + `ChomageP1` + `CAFP1` + `AutreRevenusP1` +
                `SalaireP2` + `ChomageP2` + `CAFP2` + `AutreRevenusP2` AS `reponse`
            FROM `infos_familles`
        UNION
            -- Somme charges foyer
            SELECT
                `ID_E_Charges` AS `IDreponse`,
                17 AS `IDquestion`,
                `IDfamille`,
                `Loyer` + `CreditImmo` + `Charges` + `Scolarite` AS `reponse`
            FROM `infos_familles`
        UNION
            -- R.A.V
            SELECT
                `ID_RAV` AS `IDreponse`,
                18 AS `IDquestion`,
                `IDfamille`,
                -- moyens
                (
                    -- revenus
                    (`SalaireP1` + `ChomageP1` + `CAFP1` + `AutreRevenusP1` +
                    `SalaireP2` + `ChomageP2` + `CAFP2` + `AutreRevenusP2`)
                    -- charges
                    - (`Loyer` + `CreditImmo` + `Charges` + `Scolarite`)
                )
                / (
                    -- personnes au foyer
                    (`nbParents` + `nbEnfants`)
                    -- un mois/J
                    * 30
                )
                AS `reponse`
            FROM `infos_familles`
    )
    SELECT `IDreponse`, `IDquestion`, `IDfamille`, `reponse`
        FROM `reponses_to_insert`
        WHERE `reponse` != 0
ON DUPLICATE KEY UPDATE `reponse`=VALUES(`reponse`);
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
    return DB.ResultatReq()
