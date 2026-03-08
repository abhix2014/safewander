import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("DB_PATH", ROOT / "data" / "safewander.db"))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_handle(name: str) -> str:
    handle = re.sub(r"[^a-z0-9_]+", "", name.strip().lower().replace(" ", "_"))
    return handle[:40] or "guest_traveler"


def parse_limit(raw: str, default: int = 20, min_v: int = 1, max_v: int = 100) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(min_v, min(max_v, value))


def db_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_db() -> None:
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                handle TEXT NOT NULL UNIQUE,
                avatar TEXT NOT NULL,
                verified INTEGER NOT NULL DEFAULT 1,
                trust_score REAL NOT NULL DEFAULT 9.0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                text TEXT NOT NULL,
                image_emoji TEXT,
                likes INTEGER NOT NULL DEFAULT 0,
                comments INTEGER NOT NULL DEFAULT 0,
                is_safety_alert INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS sos_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                lat REAL,
                lng REAL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                location TEXT NOT NULL,
                starts_on TEXT NOT NULL,
                spots_left INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS hostels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                price_per_night INTEGER NOT NULL,
                rating REAL NOT NULL,
                travelers_now INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            now = utc_now_iso()
            conn.executemany(
                "INSERT INTO users(name, handle, avatar, verified, trust_score, created_at) VALUES(?,?,?,?,?,?)",
                [
                    ("Riya Kapoor", "riya.k", "RK", 1, 9.5, now),
                    ("Meera Trivedi", "meera.t", "MT", 1, 9.2, now),
                    ("Sahil Arora", "sahil.a", "SA", 1, 9.1, now),
                ],
            )
            conn.executemany(
                "INSERT INTO posts(user_id, location, text, image_emoji, likes, comments, is_safety_alert, created_at) VALUES(?,?,?,?,?,?,?,?)",
                [
                    (1, "Shivpuri", "Grade 4 rafting at Shivpuri was absolutely wild 🌊 Water levels are perfect this week. Connected with 4 people through SafeWander — now we're friends for life! Highly recommend using the buddy match feature.", "🏄", 42, 8, 0, now),
                    (2, "Laxman Jhula", "⚠️ Safety Alert: Bag snatching reported near Laxman Jhula market today after 8pm. Stay alert, keep bags in front. Local police notified. Be safe out there everyone 🙏", None, 91, 23, 1, now),
                    (3, "Parmarth", "7-day yoga retreat at Parmarth starts next Monday. 2 spots open — looking for women solo travelers interested in joining. DM me directly. All background-verified participants only 🧘‍♀️", None, 28, 14, 0, now),
                ],
            )
            conn.executemany(
                "INSERT INTO events(title, location, starts_on, spots_left, created_at) VALUES(?,?,?,?,?)",
                [
                    ("Kedarnath Base Camp Trek", "Rishikesh Bus Stand", "2026-11-12", 3, now),
                    ("Morning Yoga Retreat · 7 Days", "Parmarth Niketan", "2026-11-15", 5, now),
                ],
            )
            conn.executemany(
                "INSERT INTO hostels(name, location, price_per_night, rating, travelers_now, created_at) VALUES(?,?,?,?,?,?)",
                [
                    ("Riverside Camp Shivpuri", "Shivpuri Beach", 350, 4.9, 12, now),
                    ("Ganga View Hostel", "Laxman Jhula Road", 550, 4.7, 8, now),
                ],
            )


def list_posts(limit: int) -> list[dict]:
    with db_conn() as conn:
        rows = conn.execute(
            """
            SELECT p.id, u.name, u.avatar, u.verified, p.location, p.text, p.image_emoji,
                   p.likes, p.comments, p.is_safety_alert, p.created_at
            FROM posts p
            JOIN users u ON u.id = p.user_id
            ORDER BY p.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def create_post(name: str, location: str, text: str) -> int:
    handle = normalize_handle(name)
    avatar = "".join(part[0] for part in name.split()[:2]).upper() or "GT"
    now = utc_now_iso()
    with db_conn() as conn:
        existing = conn.execute("SELECT id FROM users WHERE handle=?", (handle,)).fetchone()
        if existing:
            user_id = existing[0]
        else:
            cur = conn.execute(
                "INSERT INTO users(name, handle, avatar, verified, trust_score, created_at) VALUES(?,?,?,?,?,?)",
                (name, handle, avatar, 1, 8.8, now),
            )
            user_id = cur.lastrowid
        cur = conn.execute(
            "INSERT INTO posts(user_id, location, text, image_emoji, likes, comments, is_safety_alert, created_at) VALUES(?,?,?,?,?,?,?,?)",
            (user_id, location, text, None, 0, 0, 1 if "alert" in text.lower() else 0, now),
        )
        return cur.lastrowid


def create_incident(name: str, lat: float | None, lng: float | None) -> int:
    with db_conn() as conn:
        cur = conn.execute(
            "INSERT INTO sos_incidents(user_name, lat, lng, status, created_at) VALUES(?,?,?,?,?)",
            (name, lat, lng, "alerting_nearby", utc_now_iso()),
        )
        return cur.lastrowid


def list_incidents(limit: int) -> list[dict]:
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT id, user_name, lat, lng, status, created_at FROM sos_incidents ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def stats() -> dict:
    with db_conn() as conn:
        return {
            "verified_travelers": conn.execute("SELECT COUNT(*) FROM users WHERE verified=1").fetchone()[0],
            "posts": conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0],
            "sos_incidents": conn.execute("SELECT COUNT(*) FROM sos_incidents").fetchone()[0],
        }


def list_events() -> list[dict]:
    with db_conn() as conn:
        rows = conn.execute("SELECT id, title, location, starts_on, spots_left FROM events ORDER BY starts_on ASC").fetchall()
    return [dict(r) for r in rows]


def list_hostels() -> list[dict]:
    with db_conn() as conn:
        rows = conn.execute("SELECT id, name, location, price_per_night, rating, travelers_now FROM hostels ORDER BY rating DESC").fetchall()
    return [dict(r) for r in rows]
