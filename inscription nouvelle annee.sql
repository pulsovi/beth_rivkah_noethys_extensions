-- Ce script inscrit dans l'activite 2 (2020-2021) tous les eleves qui
-- sont inscrits dans l'activite 1 (2019-2020)
-- ont le statut d'inscription "ok" (confirme) dans l'activite 1
-- sont inscrits dans une classe de l'annee 2020-2021
--
-- ils sont inscrits
-- dans le groupe correspondant a la classe ou ils sont inscrits
-- avec la categorie (10 mois / 12 mois) qu'ils avaient en activite 1



    INSERT INTO inscriptions
    (SELECT
-- individus.nom,
-- prenom,
i2.IDinscription,
i1.IDindividu,
i1.IDfamille,
2 AS IDactivite,
groupes.IDgroupe,
ct2.IDcategorie_tarif,
i1.IDcompte_payeur,
'2020-05-18' AS date_inscription,
NULL AS parti,
NULL date_desinscription,
i1.statut

    FROM
`inscriptions` AS i1
LEFT JOIN individus USING(IDindividu)
LEFT JOIN inscriptions AS i2 ON (i1.IDindividu=i2.IDindividu and i2.IDactivite=2)
LEFT JOIN scolarite ON (individus.IDindividu = scolarite.IDindividu)
LEFT JOIN classes ON (scolarite.IDclasse = classes.IDclasse)
LEFT JOIN categories_tarifs AS ct1 ON (ct1.IDcategorie_tarif = i1.IDcategorie_tarif)
LEFT JOIN categories_tarifs AS ct2 ON (ct1.nom = ct2.nom and ct2.IDactivite =2)
LEFT JOIN groupes ON (groupes.IDactivite=2 and groupes.nom = classes.nom)
    Where
i1.IDactivite=1
AND classes.date_debut = '2020-08-31'
AND i1.statut = 'ok')
    ON DUPLICATE KEY UPDATE IDactivite=2
