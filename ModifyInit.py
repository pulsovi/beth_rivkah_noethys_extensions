# coding: utf8

import zipfile
import os
import shutil

customUtilInit = """# coding: utf8
import sys
import UTILS_Fichiers
sys.path.append(UTILS_Fichiers.GetRepExtensions())
import debug
from Ctrl import CTRL_Identification


trueMain = CTRL_Identification.Dialog.__init__

def customMain(self, parent, id=-1, title=u"Identification", listeUtilisateurs=[], nomFichier=None):
    debug.message(str({
        "self": self,
        "parent": parent,
        "id": id,
        "title": title
    }))
    debug.message("\\n".join(sys.argv))
    trueMain(self, parent, id, title, listeUtilisateurs, nomFichier)


CTRL_Identification.Dialog.__init__ = customMain

"""


def main():
    noezip = "C:\\Noethys\\library.zip"
    tempzip = ".\\sortie.zip"
    if os.path.isfile(tempzip):
        os.remove(tempzip)
    zin = zipfile.ZipFile(noezip, 'r')
    zout = zipfile.ZipFile(tempzip, 'w')
    for item in zin.infolist():
        if not item.filename.startswith("Utils/__init__"):
            buffer = zin.read(item.filename)
            zout.writestr(item, buffer)
        else:
            if zin.read(item.filename).decode("utf8") == customUtilInit:
                zout.close()
                zin.close()
                print(u"Le fichier est déjà à jour")
                return
            zout.writestr("Utils/__init__.py", customUtilInit)
    zout.close()
    zin.close()
    os.remove(noezip)
    shutil.copy(tempzip, noezip)


if (__name__ == "__main__"):
    main()
