/*************************\
|*| Erreurs utilisateur |*|
\*************************/

/*\
|*| parent inscrit en Scolarité
\*/
SELECT
    'Parent inscrit en Scolarité' AS `Anomalie`,
    `IDindividu`,
    NULL AS `IDfamille`
FROM
    `individus`
    INNER JOIN `inscriptions` USING(`IDindividu`)
WHERE `IDcivilite`!=4 AND `IDcivilite`!=5

/*\
|*| nombre d'enfants inscrits en Scolartité sur Noethys supérieur au
|*| nombre d'enfants inscrits à Beth Rivkah renseigné dans le questionnaire famille
\*/
UNION
SELECT
    'nombre d\'enfants inscrits en Scolartité sur Noethys supérieur au\nnombre d\'enfants inscrits à Beth Rivkah renseigné dans le questionnaire famille' AS `Anomalie`,
    NULL AS `IDindividu`,
    `IDfamille`
FROM
    (
        SELECT
            `familles`.`IDfamille`,
            IFNULL(`reponse`, 0) AS `nbEnfantsBR`,
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

/*\
|*| Deux quotients familiaux actifs le meme jour pour une famille
\*/
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

/*\
|*| Régime incompatible avec la classe :
|*|  EXTERNE et DEMI PENSIONNAIRE pour toutes les classes.
|*|  INTERNE du CE1 à la TERMINALE
\*/
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

/*********************\
|*| Erreur logiciel |*|
\*********************/


/*\
|*| Une question de questionnaire repondue deux fois
|*| Le meme ID de question et le meme ID d'attribution (famille ou individu)
\*/
SELECT
    'question de questionnaire repondue plusieurs fois' AS `Anomalie`,
    NULL AS `IDindividu`,
    `IDfamille`,
    `IDquestion`
FROM
    `questionnaire_reponses`
WHERE
    `IDfamille` IS NOT NULL
GROUP BY
    `IDquestion`,
    `IDfamille`
HAVING
    COUNT(*)>1

UNION
SELECT
    'question de questionnaire repondue plusieurs fois' AS `Anomalie`,
    `IDindividu`,
    NULL AS `IDindividu`,
    `IDquestion`
FROM
    `questionnaire_reponses`
WHERE
    `IDindividu` IS NOT NULL
GROUP BY
    `IDquestion`,
    `IDindividu`
HAVING
    COUNT(*)>1
