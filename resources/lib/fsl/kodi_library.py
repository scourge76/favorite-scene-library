import os
import sqlite3
import xbmcvfs


def _find_video_db():
    directory = xbmcvfs.translatePath("special://database/")
    _, filenames = xbmcvfs.listdir(directory)
    candidates = []
    for filename in filenames:
        if filename.startswith("MyVideos") and filename.endswith(".db"):
            digits = "".join(ch for ch in filename if ch.isdigit())
            candidates.append((int(digits or 0), os.path.join(directory, filename)))
    if not candidates:
        raise RuntimeError("No Kodi video database found.")
    return sorted(candidates, reverse=True)[0][1]


def read_bookmarks():
    connection = sqlite3.connect(_find_video_db())
    connection.row_factory = sqlite3.Row
    bcols = {r[1] for r in connection.execute("PRAGMA table_info(bookmark)")}
    thumb = "COALESCE(b.thumbNailImage,'')" if "thumbNailImage" in bcols else "''"
    type_filter = "AND (b.type=0 OR b.type IS NULL)" if "type" in bcols else ""
    rows = [dict(r) for r in connection.execute("""
        SELECT b.idBookmark bookmark_id,b.idFile file_id,b.timeInSeconds start_seconds,
               {thumb} scene_thumb,COALESCE(m.idMovie,0) movie_id,
               COALESCE(m.c00,'') movie_title,
               COALESCE(p.strPath,'')||COALESCE(f.strFilename,'') file_path
        FROM bookmark b JOIN files f ON f.idFile=b.idFile JOIN path p ON p.idPath=f.idPath
        LEFT JOIN movie m ON m.idFile=b.idFile
        WHERE b.timeInSeconds>0 {type_filter}
        ORDER BY movie_title COLLATE NOCASE,b.timeInSeconds
    """.format(thumb=thumb, type_filter=type_filter))]
    tables = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    counts = {}
    for row in rows:
        title = (row["movie_title"] or "").strip()
        if not title:
            title = os.path.splitext(os.path.basename(row["file_path"]))[0] or "Unknown movie"
        row["movie_title"] = title
        counts[title] = counts.get(title, 0) + 1
        row["default_name"] = "Scene %d" % counts[title]
        row["poster"], row["fanart"] = "", ""
        if "art" in tables and row["movie_id"]:
            for art in connection.execute("SELECT type,url FROM art WHERE media_id=? AND media_type='movie' AND type IN ('poster','fanart','thumb')", (row["movie_id"],)):
                if art["type"] == "poster": row["poster"] = art["url"]
                elif art["type"] == "fanart": row["fanart"] = art["url"]
                elif art["type"] == "thumb" and not row["poster"]: row["poster"] = art["url"]
    connection.close()
    return rows
