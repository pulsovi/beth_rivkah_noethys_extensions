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
    infos_financieres = GetAllInfos()

    insert = '''INSERT INTO `questionnaire_reponses`
    (`IDreponse`, `IDquestion`, `IDfamille`, `reponse`)
VALUES\n\t'''

    values = ''
    for inff in infos_financieres:
        valeurs = UpdateInfos(inff)
        if valeurs:
            if values:
                values += ',\n\t'
            values += valeurs

    duplicate = '''\nON DUPLICATE KEY UPDATE\n\t`reponse`=VALUES(`reponse`);'''
    Request(insert + values + duplicate)
    dlg = wx.MessageDialog(None, u"La procédure s'est terminée avec succès.",
                           u"Procédure terminée", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def GetAllInfos():
    global liste_colonnes

    Champs = "SELECT\n\t`familles`.`IDfamille`"
    Tables = "\nFROM\n\t`familles`"
    compteur_table = 0
    liste_colonnes = ['IDfamille']

    for nom_colonne in ID_QUESTION:
        compteur_table += 1
        nom_table = 'table' + str(compteur_table)
        id_question = ID_QUESTION[nom_colonne]

        # Champs
        if not nom_colonne.startswith('E_'):
            Champs += (",\n\tIFNULL(`{table}`.`reponse`, 0.0)" +
                       " AS `{colonne}`").format(
                table=nom_table, colonne=nom_colonne)
        else:
            Champs += ",\n\t`{table}`.`reponse` AS `{colonne}`".format(
                table=nom_table, colonne=nom_colonne)
        liste_colonnes.append(nom_colonne)

        Champs += ",\n\t`{table}`.`IDreponse` AS `{colonne}`".format(
            table=nom_table, colonne="ID_" + nom_colonne)
        liste_colonnes.append("ID_" + nom_colonne)

        # Tables
        Tables += "\n\tLEFT OUTER JOIN `questionnaire_reponses` AS `{table}`\
\n\t\tON (`{table}`.`IDfamille` = `familles`.`IDfamille` \
AND `{table}`.`IDquestion` = {ID})".format(
            table=nom_table, ID=id_question)

    # Requete
    Req = Champs + Tables + "\nORDER BY\n\t`IDfamille` ASC\n;"

    # Envoi
    return Request(Req)


def UpdateInfos(infosFamille):
    sommes = (
        ('E_RP1', ("SalaireP1", "ChomageP1", "CAFP1", "AutreRevenusP1")),
        ('E_RP2', ("SalaireP2", "ChomageP2", "CAFP2", "AutreRevenusP2")),
        ("E_RF", ("SalaireP1", "ChomageP1", "CAFP1", "AutreRevenusP1",
                  "SalaireP2", "ChomageP2", "CAFP2", "AutreRevenusP2")),
        ("E_Charges", ("Loyer", "CreditImmo", "Charges", "Scolarite"))
    )
    values = ''
    for somme in sommes:
        valeurs = UpdateE_(somme[0], somme[1], infosFamille)
        if valeurs:
            if values:
                values += ',\n\t'
            values += valeurs
    return values


def UpdateE_(nom_somme, noms_colonnes, infosFamille):
    valeurs_colonnes = tuple(
        val(nom_colonne, infosFamille) for nom_colonne in noms_colonnes)
    somme_valeurs = reduce(lambda a, b: a + b, valeurs_colonnes)

    if somme_valeurs == val(nom_somme, infosFamille):
        return ''

    IDreponse = getVal("ID_" + nom_somme, infosFamille)
    return "({IDreponse}, {IDquestion}, {IDfamille}, {reponse})".format(
        IDreponse=IDreponse if IDreponse else 'NULL',
        IDquestion=ID_QUESTION[nom_somme],
        IDfamille=getVal("IDfamille", infosFamille),
        reponse=somme_valeurs
    )


def val(colonne, infosFamille):
    saved = getVal(colonne, infosFamille)
    if saved is None:
        return 0.0
    return float(saved)


def getVal(colonne, infosFamille):
    return infosFamille[liste_colonnes.index(colonne)]


def Request(Req):
    DB = GestionDB.DB()
    DB.ExecuterReq(Req)
    return DB.ResultatReq()
