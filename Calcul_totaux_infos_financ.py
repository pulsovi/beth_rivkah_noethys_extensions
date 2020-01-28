# coding: utf8
import GestionDB
import wx

def Extension():
    Request(u'''
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
`infos_familles` AS (
    SELECT
        `familles`.`IDfamille`,
        IFNULL(`t_nbEnfantsBR`.`reponse`, 0)    AS `nbEnfantsBR`,
        IFNULL(`t_intervenantsBR`.`reponse`, 1) AS `intervenantBR`,
        IFNULL(`t_mensualite_fix`.`reponse`, 0) AS `montantFix`,
        `r_nbMensualites`.`label`               AS `nbMensualites`
    FROM
        `familles`
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_mensualite_fix`
                ON (`t_mensualite_fix`.`IDfamille`=`familles`.`IDfamille`
                    AND `t_mensualite_fix`.`IDquestion`=20)
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_nbEnfantsBR`
            ON (`t_nbEnfantsBR`.`IDfamille`=`familles`.`IDfamille`
                AND `t_nbEnfantsBR`.`IDquestion`=24)
        LEFT OUTER JOIN `questionnaire_reponses` AS `t_intervenantsBR`
            ON (`t_intervenantsBR`.`IDfamille`=`familles`.`IDfamille`
                AND `t_intervenantsBR`.`IDquestion`=1)
        LEFT JOIN `questionnaire_reponses` AS `t_nbMensualites` ON (
            `t_nbMensualites`.`IDfamille`=`familles`.`IDfamille`
            AND `t_nbMensualites`.`IDquestion`=21
        )
        LEFT JOIN `questionnaire_questions` AS `d_nbMensualites`
            ON `d_nbMensualites`.`IDquestion`=21
        LEFT JOIN `questionnaire_choix` AS `r_nbMensualites` ON (
            `IDchoix`=IFNULL(`t_nbMensualites`.`reponse`,`d_nbMensualites`.`defaut`)
        )
),
`tarifs_scolarites` AS (
    SELECT
        `IDgroupe`,
        `nbEnfantsBR`,
        `intervenantBR`,
        `tarif` * `CoeffDegressif` * `CoeffIntervenant` AS `tarif`
    FROM
        (
            SELECT 1 /*Maternelle*/ AS `IDgroupe`, 3600 AS `tarif` UNION ALL
            SELECT 2 /*Primaire  */ AS `IDgroupe`, 3600 AS `tarif` UNION ALL
            SELECT 3 /*Collège   */ AS `IDgroupe`, 4080 AS `tarif` UNION ALL
            SELECT 4 /*Lycée     */ AS `IDgroupe`, 4200 AS `tarif` UNION ALL
            SELECT 5 /*Lycée Pro */ AS `IDgroupe`, 4200 AS `tarif`
        ) AS `tarif`

        LEFT JOIN (
            SELECT
                1 AS `nbEnfantsBR`,
                1 AS `CoeffDegressif` UNION ALL
            SELECT
                2 AS `nbEnfantsBR`,
                0.92 AS `CoeffDegressif` UNION ALL
            SELECT
                3 AS `nbEnfantsBR`,
                0.88 AS `CoeffDegressif` UNION ALL
            SELECT
                4 AS `nbEnfantsBR`,
                0.84 AS `CoeffDegressif` UNION ALL
            SELECT
                5 AS `nbEnfantsBR`,
                0.80 AS `CoeffDegressif` UNION ALL
            SELECT
                6 AS `nbEnfantsBR`,
                0.76 AS `CoeffDegressif`
        ) AS `nbEnfants`
            ON 1=1

        LEFT JOIN (
            SELECT
                /*non intervenant*/
                1 AS `intervenantBR`,
                1 AS `CoeffIntervenant` UNION ALL
            SELECT
                /*1 parent intervenant à mi-temps*/
                2 AS `intervenantBR`,
                0.90 AS `CoeffIntervenant` UNION ALL
            SELECT
                /*2 parents intervenants à mi-temps*/
                3 AS `intervenantBR`,
                0.85 AS `CoeffIntervenant` UNION ALL
            SELECT
                /*1 parent ou + intervenant à plein temps*/
                4 AS `intervenantBR`,
                0.75 AS `CoeffIntervenant`
        ) AS `intervenant`
            ON 1=1
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
        -- mensualité familiale calculée
        SELECT
            `t_mensualite_std`.                         `IDreponse`,
            19                                       AS `IDquestion`,
            NULL                                     AS `IDindividu`,
            `infos_familles`.                           `IDfamille`,
            SUM(`tarif`) / `nbMensualites`           AS `reponse`
        FROM
            `infos_familles`
            INNER JOIN `inscriptions` USING(`IDfamille`)
            LEFT JOIN `tarifs_scolarites` ON (
                `inscriptions`.`IDgroupe`=`tarifs_scolarites`.`IDgroupe`
                AND `tarifs_scolarites`.`nbEnfantsBR`=`infos_familles`.`nbEnfantsBR`
                AND `tarifs_scolarites`.`intervenantBR`=`infos_familles`.`intervenantBR`
            )
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_mensualite_std` ON (
                `t_mensualite_std`.`IDfamille`=`infos_familles`.`IDfamille`
                AND `t_mensualite_std`.`IDquestion`=19
            )
        GROUP BY `IDfamille`
    UNION
        -- mensualité personnelle calculée
        SELECT
            `t_IDreponse`.               `IDreponse`,
            25                        AS `IDquestion`,
            `inscriptions`.              `IDindividu`,
            NULL                      AS `IDfamille`,
            `tarif` / `nbMensualites` AS `reponse`
        FROM
            `inscriptions`
            LEFT OUTER JOIN `infos_familles` USING(`IDfamille`)
            LEFT JOIN `tarifs_scolarites` ON (
                `inscriptions`.`IDgroupe`=`tarifs_scolarites`.`IDgroupe`
                AND `tarifs_scolarites`.`nbEnfantsBR`=`infos_familles`.`nbEnfantsBR`
                AND `tarifs_scolarites`.`intervenantBR`=`infos_familles`.`intervenantBR`
            )
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_IDreponse` ON (
                `t_IDreponse`.`IDindividu`=`inscriptions`.`IDindividu`
                AND `t_IDreponse`.`IDquestion`=25
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
    UNION
        -- Reduction tarif scolarité
        SELECT
            `t_IDreponse`.        `IDreponse`,
            28                 AS `IDquestion`,
            `inscriptions`.       `IDindividu`,
            NULL               AS `IDfamille`,
            `coeff`            AS `reponse`
        FROM
            `inscriptions`
            LEFT JOIN (
                SELECT
                    `infos_familles`.`IDfamille`,
                    100 * (1 - (`montantFix` / (SUM(`tarif`) / `nbMensualites`))) AS `coeff`
                FROM
                    `infos_familles`
                    INNER JOIN `inscriptions` USING(`IDfamille`)
                    INNER JOIN `tarifs_scolarites` ON (
                        `inscriptions`.`IDgroupe`=`tarifs_scolarites`.`IDgroupe`
                        AND `tarifs_scolarites`.`nbEnfantsBR`=`infos_familles`.`nbEnfantsBR`
                        AND `tarifs_scolarites`.`intervenantBR`=`infos_familles`.`intervenantBR`
                    )
                    GROUP BY `IDfamille`
            ) AS `famille` USING(`IDfamille`)
            LEFT OUTER JOIN `questionnaire_reponses` AS `t_IDreponse` ON (
                `t_IDreponse`.`IDquestion`=28
                AND `t_IDreponse`.`IDindividu`=`inscriptions`.`IDindividu`
            )
)
SELECT `IDreponse`, `IDquestion`, `IDindividu`, `IDfamille`, `reponse`
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
    res = DB.ResultatReq()
    DB.Close()
    return res
