# coding: utf8

import zipfile
import os
import shutil
import wx
from Utils import UTILS_Fichiers
import Data
import FonctionsPerso
import GestionDB
from six.moves import urllib
import json

VERSION = "_v1.0.5"
officialVersionsCache = None


def Extension():
    wait = wx.BusyInfo(u"Verifications en cours, merci de patienter…")

    bootstrapVersion = getOfficialVersion("Utils__init__.py")

    uptodate = hasModule("Utils__init__" + bootstrapVersion)
    if not uptodate:
        success = updateBootstrap()
        if success:
            addModule("Utils__init__" + bootstrapVersion + u" installée")
        else:
            del wait
            message(u"Impossible d'installer l'extension.", __name__ + VERSION)
            return

    del wait
    updated = hasModule("Utils__init__" + bootstrapVersion + u" installée")
    if updated:
        message(u"L'extension est installée. Merci de redémarrer Noethys pour l'activer",
            __name__ + VERSION)
        return

    message(u"Extension installée et activée.", __name__ + VERSION)


def Initialisation():
    updates = UpdateAll()
    if updates:
        bootMessage(u"Les extensions suivantes ont été mises à jour:" + u"\n  - ".
            join([""] + updates))
    return
    message(u"L'installation s'est correctement déroulée." +
        u"Il est necessaire de redémarrer Noethys pour l'activer.", __name__ + VERSION)


def UpdateAll():
    updates = []
    officialBootstrapVersion = getOfficialVersion("Utils__init__.py")
    if officialBootstrapVersion is None:
        return updates
    if not hasModule("Utils__init__" + officialBootstrapVersion):
        if not hasattr(Data, "extensionsAutomatiques"):
            oldVersion = ""
        else:
            for extension in Data.extensionsAutomatiques:
                if extension.startswith("Utils__init__"):
                    oldVersion = extension.split("_v")[1]
        success = updateBootstrap()
        if success:
            updates.append("Utils__init__.py " + oldVersion + " > " + officialBootstrapVersion)
    for extension, version in officialVersionsCache.iteritems():
        if extension == "Utils__init__.py":
            continue
        currentVersion = getFileVersion(extension) or ""
        # if currentVersion is None: update
        if currentVersion != version:
            success = updateExtension(extension)
            if success:
                updates.append("{} {} > {}".format(extension, currentVersion, version))
    return updates


def addModule(moduleName):
    if not hasattr(Data, "extensionsAutomatiques"):
        Data.extensionsAutomatiques = []
    Data.extensionsAutomatiques.append(moduleName)


def bootMessage(text="", title=""):
    app = wx.App()
    message(text, title)
    app.Destroy()


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
        bootMessage(str(type(err)))
        return None


def getOfficialVersion(filename, noethysVersion=FonctionsPerso.GetVersionLogiciel()):
    if officialVersionsCache is not None:
        if filename in officialVersionsCache:
            return officialVersionsCache[filename]
    getOfficialVersions(noethysVersion)
    if officialVersionsCache is None:
        return None
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


def message(text, title=u"Information"):
    dlg = wx.MessageDialog(
        parent=None,
        message=text,
        caption=title,
        style=wx.OK | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()


def updateBootstrap():
    customUtilInit = getFromGithub("Utils__init__.pyc")
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
    return True


def updateExtension(extension):
    filename = UTILS_Fichiers.GetRepExtensions(extension)
    url = githubUrl(extension)
    urllib.request.urlretrieve(url, filename)
    return True
