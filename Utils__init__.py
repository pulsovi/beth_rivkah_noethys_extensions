# coding: utf8

import sys
import os
import UTILS_Fichiers
import importlib
import wx

VERSION = "_v1.1.1"

sys.path.append(UTILS_Fichiers.GetRepExtensions())

ext = "py"
fichiers = os.listdir(UTILS_Fichiers.GetRepExtensions())
fichiers.sort()
mainFile = "Extensions_automatiques.py"
if mainFile in fichiers:
    index = fichiers.index(mainFile)
    fichiers = [mainFile] + fichiers[0:index] + fichiers[index + 1:]
listeErreurs = {}
for fichier in fichiers:
    if fichier.endswith(ext):
        nomFichier = os.path.split(fichier)[1]
        titre = nomFichier[:-(len(ext) + 1)]
        try:
            module = importlib.import_module(titre)
            initialisation = getattr(module, "Initialisation", None)
            if callable(initialisation):
                module.Initialisation()
        except Exception as erreur:
            key = str(erreur)
            if key not in listeErreurs:
                listeErreurs[key] = []
            listeErreurs[key].append(titre)
if len(listeErreurs) > 0:
    app = wx.App(redirect=False)
    for erreur, fichiersErreur in listeErreurs.iteritems():
        if len(fichiersErreur) == 1:
            message = [u"L'extension suivante n'a pas pu être chargée:"]
        else:
            message = [u"Les extensions suivante n'ont pas pu être chargées:"]
        dlg = wx.MessageDialog(
            parent=None,
            message="\\n".join(message + fichiersErreur + [
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
else:
    importlib.import_module(mainFile[:-(len(ext) + 1)]).addModule(__name__ + VERSION)
