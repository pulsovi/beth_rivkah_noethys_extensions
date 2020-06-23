# coding: utf8

import sys
import os
from Utils import UTILS_Fichiers
import importlib
import wx
import Data
import traceback
from six.moves import reload_module

VERSION = "_v1.2.4"


def getFileList():
    # Récupére la liste des fichiers
    fichiers = os.listdir(UTILS_Fichiers.GetRepExtensions())
    fichiers.sort()
    return fichiers


def launch(fichier):
    # Execute les Initialisation des extensions et collecte les erreurs
    if not fichier.endswith(ext):
        return
    nomFichier = os.path.split(fichier)[1]
    titre = nomFichier[:-(len(ext) + 1)]
    try:
        module = importlib.import_module(titre)
        initialisation = getattr(module, "Initialisation", None)
        if callable(initialisation):
            module.Initialisation()
        return module
    except Exception as erreur:
        key = str(erreur)
        if key not in listeErreurs:
            listeErreurs[key] = []
        listeErreurs[key].append(titre)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write("\n")


# Ajoute la version du bootstrap dans le repertoire des extensions chargées
Data.extensionsAutomatiques = ["Utils__init__" + VERSION]
# Ajoute le repertoire des extensions au PATH
sys.path.append(UTILS_Fichiers.GetRepExtensions())

ext = "py"
mainFile = "Extensions_automatiques.py"
listeErreurs = {}

fichiers = getFileList()
if mainFile in fichiers:
    mainModule = launch(mainFile)
    fichiers = getFileList()
    if mainModule:
        reload_module(mainModule)
for fichier in fichiers:
    launch(fichier)

# Affiche les erreurs
if listeErreurs:
    app = wx.App()
    for erreur, fichiersErreur in listeErreurs.iteritems():
        if len(fichiersErreur) == 1:
            message = [u"L'extension suivante n'a pas pu être chargée:"]
        else:
            message = [u"Les extensions suivante n'ont pas pu être chargées:"]
        dlg = wx.MessageDialog(
            parent=None,
            message="\n".join(message + fichiersErreur + [
                "",
                "Erreur:",
                erreur
            ]),
            caption="Erreur",
            style=wx.OK | wx.ICON_ERROR
        )
        dlg.ShowModal()
        dlg.Destroy()
    app.Destroy()
