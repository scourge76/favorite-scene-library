import sqlite3
from datetime import datetime

from .context import DATABASE
from .util import ensure_profile


class SceneDatabase:
    def __init__(self):
        ensure_profile()
        self.connection = sqlite3.connect(DATABASE)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS scenes (
                bookmark_id INTEGER PRIMARY KEY,
                file_id INTEGER,
                movie_id INTEGER,
                movie_title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                start_seconds REAL NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Favorites',
                scene_thumb TEXT NOT NULL DEFAULT '',
                poster TEXT NOT NULL DEFAULT '',
                fanart TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        self.connection.commit()

    def sync_bookmark(self, scene):
        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        exists = self.connection.execute(
            "SELECT 1 FROM scenes WHERE bookmark_id=?", (scene["bookmark_id"],)
        ).fetchone()
        if exists:
            self.connection.execute("""
                UPDATE scenes SET file_id=?,movie_id=?,movie_title=?,file_path=?,
                    start_seconds=?,scene_thumb=?,poster=?,fanart=?,updated_at=?
                WHERE bookmark_id=?
            """, (scene["file_id"], scene["movie_id"], scene["movie_title"],
                  scene["file_path"], scene["start_seconds"], scene["scene_thumb"],
                  scene["poster"], scene["fanart"], now, scene["bookmark_id"]))
        else:
            self.connection.execute("""
                INSERT INTO scenes(bookmark_id,file_id,movie_id,movie_title,file_path,
                    start_seconds,name,category,scene_thumb,poster,fanart,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,'Favorites',?,?,?,?,?)
            """, (scene["bookmark_id"], scene["file_id"], scene["movie_id"],
                  scene["movie_title"], scene["file_path"], scene["start_seconds"],
                  scene["default_name"], scene["scene_thumb"], scene["poster"],
                  scene["fanart"], now, now))
        self.connection.commit()

    def list_scenes(self, category=None, movie=None):
        sql, where, values = "SELECT * FROM scenes", [], []
        if category:
            where.append("category=?"); values.append(category)
        if movie:
            where.append("movie_title=?"); values.append(movie)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY movie_title COLLATE NOCASE,start_seconds"
        return [dict(row) for row in self.connection.execute(sql, values)]

    def list_movies(self):
        return [dict(row) for row in self.connection.execute("""
            SELECT movie_title,poster,fanart,COUNT(*) AS scene_count FROM scenes
            GROUP BY movie_title ORDER BY movie_title COLLATE NOCASE
        """)]

    def list_categories(self):
        return [dict(row) for row in self.connection.execute("""
            SELECT category,COUNT(*) AS scene_count FROM scenes
            GROUP BY category ORDER BY category COLLATE NOCASE
        """)]

    def rename(self, bookmark_id, name):
        self.connection.execute("UPDATE scenes SET name=?,updated_at=datetime('now') WHERE bookmark_id=?", (name, bookmark_id))
        self.connection.commit()

    def set_category(self, bookmark_id, category):
        self.connection.execute("UPDATE scenes SET category=?,updated_at=datetime('now') WHERE bookmark_id=?", (category, bookmark_id))
        self.connection.commit()

    def delete(self, bookmark_id):
        self.connection.execute("DELETE FROM scenes WHERE bookmark_id=?", (bookmark_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()
