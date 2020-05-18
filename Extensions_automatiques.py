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
import wx

Data.extensionsAutomatiques = ["{idString}"]

sys.path.append(UTILS_Fichiers.GetRepExtensions())

ext = "py"
fichiers = os.listdir(UTILS_Fichiers.GetRepExtensions())
fichiers.sort()
listeExtensions = []
fichiersErreurs = []
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
            fichiersErreurs.append((titre, str(erreur)))
if len(fichiersErreurs) > 0:
    app = wx.App(redirect=False)
    for titre, erreur in fichiersErreurs:
        dlg = wx.MessageDialog(
            parent=None,
            message="\\n".join([
                u"L'extension suivante n'a pas pu être chargée:",
                titre,
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
""".format(idString=__name__ + VERSION)


def Extension():
    if hasModule(__name__ + VERSION):
        message(u"Extension installée et activée.", __name__ + VERSION)
        return

    if hasModule(__name__ + VERSION + u" installée"):
        message(u"L'extension est installée. Merci de redémarrer Noethys pour l'activer", __name__ + VERSION)
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
Il est necessaire de redémarrer Noethys pour l'activer.""", __name__ + VERSION)


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
