# coding: utf8
import GestionDB
from Utils.UTILS_Traduction import _

from Extensions_automatiques import addModule, hasModule, message
from divers import copyToClipboard

VERSION = "_v0.0.0"


def Extension():
    if not hasModule(__name__ + VERSION):
        message(u"L'extension est correctement installée, " +
            u"merci de redémarrer Noethys pour l'activer.")
        return
    message(u"Extension installée et activée.", __name__ + VERSION)


def Initialisation():
    GestionDB.DB.ExecuterReq = ExecuterReq
    addModule(__name__ + VERSION)


def ExecuterReq(self, req):
    if self.echec == 1:
        return False
    # Pour parer le pb des () avec MySQL
    if self.isNetwork:
        req = req.replace("()", "(10000000, 10000001)")
    try:
        self.cursor.execute(req)
        GestionDB.DICT_CONNEXIONS[self.IDconnexion].append(req)
    except Exception as err:
        err = str(err).encode("ascii", "replace")
        req = req.encode("ascii", "replace")
        message(err + u"\n\n" + req)
        print(_(u"Requete SQL incorrecte :\n%s\nErreur detectee:\n%s") % (req, err))
        return 0
    else:
        return 1
