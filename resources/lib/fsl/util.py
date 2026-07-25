import json
import urllib.parse

import xbmc
import xbmcgui
import xbmcvfs

from .context import ADDON_NAME, BASE_URL, PROFILE


def ensure_profile():
    if not xbmcvfs.exists(PROFILE):
        xbmcvfs.mkdirs(PROFILE)


def notify(message, error=False):
    icon = xbmcgui.NOTIFICATION_ERROR if error else xbmcgui.NOTIFICATION_INFO
    xbmcgui.Dialog().notification(ADDON_NAME, message, icon, 3500)


def build_url(action, **values):
    args = {"action": action}
    args.update(values)
    return BASE_URL + "?" + urllib.parse.urlencode(args)


def format_time(value):
    total = max(0, int(round(float(value))))
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def seconds_to_kodi_time(value):
    total_ms = max(0, int(round(float(value) * 1000)))
    hours, remainder = divmod(total_ms, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return {"hours": hours, "minutes": minutes, "seconds": seconds, "milliseconds": milliseconds}


def json_rpc(method, params):
    request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
    if "error" in response:
        error = response["error"]
        raise RuntimeError("%s: %s" % (error.get("code"), error.get("message")))
    return response.get("result")
