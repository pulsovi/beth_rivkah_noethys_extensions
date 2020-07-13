# coding: utf8

# exposes:
#     classes: DB
#     functions: addModule, deprecate, getQuery, hasModule, message, printErr
import json
import os
import shutil
import subprocess
import sys
import traceback
import zipfile

from six.moves import urllib
import wx

import Data
from Utils import UTILS_Fichiers
import FonctionsPerso
import GestionDB

VERSION = "_v1.4.0"
BOOT = "Utils__init__"
BOOTpy = BOOT + ".py"
BOOTpyc = BOOT + ".pyc"

officialVersionsCache = None


def Extension():
    wait = wx.BusyInfo(u"Verifications en cours, merci de patienter…")
    text = ""
    try:
        bootstrapVersion = getOfficialVersion(BOOTpy)
        uptodate = hasModule(BOOT + bootstrapVersion)
        updated = hasModule(BOOT + bootstrapVersion + u" installée")

        if uptodate:
            text = u"Extension installée et activée."
        elif updated:
            text = u"L'extension est installée. Merci de redémarrer Noethys pour l'activer"
        else:
            updateBootstrap()
            addModule(BOOT + bootstrapVersion + u" installée")
            text = (u"L'installation s'est correctement déroulée."
                u" Il est necessaire de redémarrer Noethys pour l'activer.")
    except Exception as err:
        printErr(err, False)
        text = u"Impossible d'installer l'extension."
    del wait
    message(text, __name__ + VERSION)


def Initialisation():
    app = wx.App()
    wait = wx.BusyInfo(u"Mise à jour des extensions en cours, merci de patienter…")
    updates = UpdateAll()
    del wait
    if updates:
        message(u"Les extensions suivantes ont été mises à jour:" + u"\n  - ".join([""] + updates))
        bootOrUpdater = [update for update in updates if BOOTpy in update or __name__ in update]
        if bootOrUpdater:
            subprocess.Popen(sys.argv)
            sys.exit(0)
    app.Destroy()


def UpdateAll():
    updates = []
    try:
        officialBootstrapVersion = getOfficialVersion(BOOTpy)
        if not hasModule(BOOT + officialBootstrapVersion):
            if not hasattr(Data, "extensionsAutomatiques"):
                oldVersion = ""
            else:
                for extension in Data.extensionsAutomatiques:
                    if extension.startswith(BOOT):
                        oldVersion = extension.split("_v")[1]
            updateBootstrap()
            updates.append(BOOTpy + " " + oldVersion + " > " + officialBootstrapVersion)
        for extension, version in officialVersionsCache.iteritems():
            if extension == BOOTpy:
                continue
            currentVersion = getFileVersion(extension) or ""
            # if currentVersion is None: update
            if currentVersion != version:
                success = updateExtension(extension)
                if success:
                    updates.append("{} {} > {}".format(extension, currentVersion, version))
    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write("\n")
        sys.stderr.flush()
        message(str(err), "Erreur", wx.OK | wx.ICON_ERROR)
    finally:
        return updates


def addModule(moduleName):
    if not hasattr(Data, "extensionsAutomatiques"):
        Data.extensionsAutomatiques = []
    Data.extensionsAutomatiques.append(moduleName)


def deprecate(text="Deprecated function"):
    sys.stderr.write(text)
    sys.stderr.write("\n")
    traceback.print_stack(file=sys.stderr)
    sys.stderr.write("\n")
    sys.stderr.flush()


def getFileVersion(filename):
    path = UTILS_Fichiers.GetRepExtensions(filename)
    try:
        fd = open(path, "r")
        lines = fd.readlines()
        for line in lines:
            if "VERSION =" in line:
                return line.split('"')[1]
        return None
    except Exception:
        return None


def getFromGithub(
    filename,
    version=FonctionsPerso.GetVersionLogiciel(),
    repository="beth_rivkah_noethys_extensions",
    user="pulsovi",
    asFd=False
):
    url = githubUrl(filename, version, repository, user)
    try:
        fd = urllib.request.urlopen(url + "\n")
        if asFd:
            return fd
        content = fd.read()
        fd.close()
        return content
    except Exception as err:
        if str(type(err)) == "<class 'urllib2.HTTPError'>":
            return None
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write("\n")
        sys.stderr.flush()
        message(str(err))
        return None


def getOfficialVersion(filename, noethysVersion=FonctionsPerso.GetVersionLogiciel()):
    if officialVersionsCache is not None:
        if filename in officialVersionsCache:
            return officialVersionsCache[filename]
    getOfficialVersions(noethysVersion)
    if officialVersionsCache is None:
        raise Exception("Impossible de trouver la version officielle.")
    return officialVersionsCache[filename]


def getOfficialVersions(noethysVersion):
    global officialVersionsCache
    jsonString = getFromGithub("versions.json", noethysVersion)
    if jsonString is None:
        return None
    dictVersions = json.loads(jsonString)
    officialVersionsCache = dictVersions


def getQuery(query):
    db = GestionDB.DB()
    db.ExecuterReq(query)
    response = db.ResultatReq()
    db.Close()
    return response


def githubUrl(
    filename,
    version=FonctionsPerso.GetVersionLogiciel(),
    repository="beth_rivkah_noethys_extensions",
    user="pulsovi",
):
    basename = u"https://raw.githubusercontent.com"
    url = u"{basename}/{user}/{repository}/{version}/{filename}".format(
        basename=basename,
        user=user,
        repository=repository,
        version=version,
        filename=filename
    )
    return urllib.parse.quote(url, safe=":/")


def hasModule(moduleName):
    if not hasattr(Data, "extensionsAutomatiques"):
        return False
    return moduleName in Data.extensionsAutomatiques


def message(text, title=u"Information", style=wx.OK | wx.ICON_INFORMATION):
    dlg = wx.MessageDialog(
        parent=None,
        message=text,
        caption=title,
        style=style
    )
    response = dlg.ShowModal()
    dlg.Destroy()
    return response


def printErr(err, display=message):
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write("\n")
    sys.stderr.flush()
    if callable(display):
        display(str(err))


def updateBootstrap():
    customUtilInit = getFromGithub(BOOTpyc)
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
            zipOut.writestr("Utils/__init__.pyc", customUtilInit)
    zipOut.close()
    zipIn.close()
    os.remove(noezip)
    shutil.copy(tempzip, noezip)
    os.remove(tempzip)


def updateExtension(extension):
    filename = UTILS_Fichiers.GetRepExtensions(extension)
    url = githubUrl(extension)
    renamed = False
    if os.path.exists(filename):
        renamed = True
        os.rename(filename, filename + ".old")
    urllib.request.urlcleanup()
    urllib.request.urlretrieve(url, filename)
    if renamed:
        os.remove(filename + ".old")
    return True


class DB(GestionDB.DB, object):
    def __init__(self):
        super(DB, self).__init__()

    def GetQuery(self, query):
        success = self.ExecuterReq(query)
        response = self.ResultatReq()
        return response, success

    def GetResponse(self, query):
        return self.GetQuery(query)[0]
