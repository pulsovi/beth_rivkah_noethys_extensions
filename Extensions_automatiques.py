# coding: utf8

import zipfile
import os
import shutil
import wx
from Utils import UTILS_Fichiers
import Data
import GestionDB

VERSION = "_v1.0.4"

customUtilInit = """# coding: utf8

import sys
import os
import UTILS_Fichiers
import importlib
import Data

Data.extensionsAutomatiques = ["{idString}"]

sys.path.append(UTILS_Fichiers.GetRepExtensions())

ext = "py"
fichiers = os.listdir(UTILS_Fichiers.GetRepExtensions())
fichiers.sort()
listeExtensions = []
for fichier in fichiers:
    if fichier.endswith(ext):
        nomFichier = os.path.split(fichier)[1]
        titre = nomFichier[:-(len(ext) + 1)]
        module = importlib.import_module(titre)
        initialisation = getattr(module, "Initialisation", None)
        if callable(initialisation):
            module.Initialisation()
""".format(idString=__name__ + VERSION)


def Extension():
    if hasModule(__name__ + VERSION):
        message(u"Extension installée et activée.")
        return

    if hasModule(__name__ + VERSION + u" installée"):
        message(u"L'extension est installée. Merci de redémarrer Noethys pour l'activer")
        return

    noezip = os.path.realpath(os.path.join(UTILS_Fichiers.__file__, "..", ".."))
    tempzip = os.path.join(UTILS_Fichiers.GetRepTemp(), "sortie.zip")
    if os.path.isfile(tempzip):
        os.remove(tempzip)
    zipIn = zipfile.ZipFile(noezip, 'r')
    zipOut = zipfile.ZipFile(tempzip, 'w')
    for item in zipIn.infolist():
        if not item.filename.startswith("Utils/__init__"):
            buffer = zipIn.read(item.filename)
            zipOut.writestr(item, buffer)
        else:
            zipOut.writestr("Utils/__init__.py", customUtilInit)
    zipOut.close()
    zipIn.close()
    os.remove(noezip)
    shutil.copy(tempzip, noezip)
    os.remove(tempzip)
    addModule(__name__ + VERSION + u" installée")
    message(u"""L'installation s'est correctement déroulée. \
Il est necessaire de redémarrer Noethys pour l'activer.""")


def addModule(moduleName):
    if not hasattr(Data, "extensionsAutomatiques"):
        Data.extensionsAutomatiques = []
    Data.extensionsAutomatiques.append(moduleName)


def hasModule(moduleName):
    if not hasattr(Data, "extensionsAutomatiques"):
        return False
    return moduleName in Data.extensionsAutomatiques

# fonctions utiles


def message(text, title=u"Information"):
    dlg = wx.MessageDialog(
        parent=None,
        message=text,
        caption=title,
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()


def getQuery(query):
    db = GestionDB.DB()
    db.ExecuterReq(query)
    response = db.ResultatReq()
    db.Close()
    return response
