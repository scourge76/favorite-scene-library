import sys
import urllib.parse

import xbmc
import xbmcgui

from .context import ADDON_NAME, tr
from .database import SceneDatabase
from .kodi_library import read_bookmarks
from .player import play
from .util import notify
from . import views

DEFAULT_CATEGORIES = [
    "Favorites", "Action", "Atmos", "Bass Demo",
    "Dolby Vision", "Music", "Reference Picture", "Funny"
]


def _params():
    query = sys.argv[2][1:] if len(sys.argv) > 2 else ""
    return urllib.parse.parse_qs(query)


def _one(params, key, default=""):
    return params.get(key, [default])[0]


def synchronize(database, silent=False):
    bookmarks = read_bookmarks()
    for bookmark in bookmarks:
        database.sync_bookmark(bookmark)
    if not silent:
        notify(tr(30020) % len(bookmarks))


def run():
    params = _params()
    action = _one(params, "action", "root")
    database = SceneDatabase()
    try:
        if action in ("root", "scenes", "movies", "categories"):
            synchronize(database, silent=True)

        if action == "root":
            views.root()
        elif action == "scenes":
            views.scenes(database.list_scenes(
                category=_one(params, "category") or None,
                movie=_one(params, "movie") or None
            ))
        elif action == "movies":
            views.folders(database.list_movies(), "movies")
        elif action == "categories":
            views.folders(database.list_categories(), "categories")
        elif action == "sync":
            synchronize(database)
            xbmc.executebuiltin("Container.Refresh")
        elif action == "play":
            play(_one(params, "path"), float(_one(params, "seconds", "0")))
        elif action == "rename":
            bookmark_id = int(_one(params, "bookmark_id"))
            name = xbmcgui.Dialog().input(tr(30008), defaultt=_one(params, "current"))
            if name and name.strip():
                database.rename(bookmark_id, name.strip())
                notify(tr(30021))
                xbmc.executebuiltin("Container.Refresh")
        elif action == "category":
            bookmark_id = int(_one(params, "bookmark_id"))
            categories = sorted(set(DEFAULT_CATEGORIES + [row["category"] for row in database.list_categories()]))
            selected = xbmcgui.Dialog().select(tr(30009), categories)
            if selected >= 0:
                database.set_category(bookmark_id, categories[selected])
                notify(tr(30022))
                xbmc.executebuiltin("Container.Refresh")
        elif action == "delete":
            bookmark_id = int(_one(params, "bookmark_id"))
            name = _one(params, "name", tr(30012))
            if xbmcgui.Dialog().yesno(ADDON_NAME, tr(30030) % name):
                database.delete(bookmark_id)
                notify(tr(30023))
                xbmc.executebuiltin("Container.Refresh")
    except Exception as exc:
        xbmc.log("[FSL] %s" % exc, xbmc.LOGERROR)
        xbmcgui.Dialog().ok(ADDON_NAME, str(exc))
    finally:
        database.close()
