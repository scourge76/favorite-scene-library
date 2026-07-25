import os
import sys

import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
DATABASE = os.path.join(PROFILE, "fsl.db")


def tr(string_id):
    return ADDON.getLocalizedString(string_id)
