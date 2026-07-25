import xbmcgui
import xbmcplugin

from .context import HANDLE, tr
from .util import build_url, format_time


def _art(item, scene):
    art = {}
    if scene.get("scene_thumb"):
        art["thumb"] = scene["scene_thumb"]
        art["icon"] = scene["scene_thumb"]
    if scene.get("poster"):
        art["poster"] = scene["poster"]
        art.setdefault("icon", scene["poster"])
    if scene.get("fanart"):
        art["fanart"] = scene["fanart"]
    if art:
        item.setArt(art)


def root():
    entries = [
        (tr(30001), "scenes", True),
        (tr(30002), "movies", True),
        (tr(30003), "categories", True),
        (tr(30004), "sync", False),
    ]
    for label, action, folder in entries:
        item = xbmcgui.ListItem(label=label)
        xbmcplugin.addDirectoryItem(HANDLE, build_url(action), item, folder)
    xbmcplugin.endOfDirectory(HANDLE)


def scenes(rows):
    for scene in rows:
        item = xbmcgui.ListItem(
            label="%s – %s" % (scene["movie_title"], scene["name"]),
            label2=format_time(scene["start_seconds"])
        )
        item.setProperty("IsPlayable", "true")
        item.setInfo("video", {
            "title": scene["name"],
            "originaltitle": scene["movie_title"],
            "plot": "%s\n\n%s: %s\n%s: %s" % (
                scene["movie_title"], tr(30010), scene["category"],
                tr(30011), format_time(scene["start_seconds"])
            ),
            "mediatype": "video",
        })
        _art(item, scene)
        play_url = build_url("play", path=scene["file_path"], seconds=scene["start_seconds"])
        item.addContextMenuItems([
            (tr(30005), 'RunPlugin("%s")' % build_url("rename", bookmark_id=scene["bookmark_id"], current=scene["name"])),
            (tr(30006), 'RunPlugin("%s")' % build_url("category", bookmark_id=scene["bookmark_id"], current=scene["category"])),
            (tr(30007), 'RunPlugin("%s")' % build_url("delete", bookmark_id=scene["bookmark_id"], name=scene["name"])),
        ])
        xbmcplugin.addDirectoryItem(HANDLE, play_url, item, False)
    xbmcplugin.setContent(HANDLE, "videos")
    xbmcplugin.endOfDirectory(HANDLE)


def folders(rows, kind):
    for row in rows:
        if kind == "movies":
            item = xbmcgui.ListItem(label="%s (%d)" % (row["movie_title"], row["scene_count"]))
            item.setArt({k: v for k, v in {"poster": row.get("poster", ""), "fanart": row.get("fanart", "")}.items() if v})
            url = build_url("scenes", movie=row["movie_title"])
        else:
            item = xbmcgui.ListItem(label="%s (%d)" % (row["category"], row["scene_count"]))
            url = build_url("scenes", category=row["category"])
        xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
    xbmcplugin.endOfDirectory(HANDLE)
