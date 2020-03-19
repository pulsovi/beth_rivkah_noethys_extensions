# coding: utf8

import zipfile
import os
import shutil
import wx
from Utils import UTILS_Fichiers

customUtilInit = """# coding: utf8

import sys
import os
import UTILS_Fichiers
import importlib

#sys.stderr.write("\\n\\n\\nLancement des extensions ...\\n\\n\\n")

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

"""


def Extension():
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
            if zipIn.read(item.filename).decode("utf8") == customUtilInit:
                zipOut.close()
                zipIn.close()
                message(u"L'installation est déjà active.")
                return
            zipOut.writestr("Utils/__init__.py", customUtilInit)
    zipOut.close()
    zipIn.close()
    os.remove(noezip)
    shutil.copy(tempzip, noezip)
    os.remove(tempzip)
    message(u"L'installation s'est correctement déroulée.")


def message(text, title=u"Information"):
    dlg = wx.MessageDialog(
        parent=None,
        message=text,
        caption=title,
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()
