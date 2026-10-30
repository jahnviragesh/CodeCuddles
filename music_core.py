"""Shared recommendation and storage logic for CodeCuddles."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SONGS_FILE = ROOT / "songs.json"
DB_FILE = ROOT / "codecuddles.db"

MOOD_KEYWORDS = {
    "Party": ["happy", "party", "dance", "fun", "excited", "celebrate"],
    "Sad": ["sad", "cry", "heartbreak", "lonely", "miss", "down"],
    "Romantic": ["love", "romantic", "crush", "date", "heart", "relationship"],
    "Motivational": ["motivate", "workout", "strong", "pump", "energy", "goal"],
    "Chill": ["relax", "calm", "study", "focus", "chill", "peaceful"],
    "Energetic": ["energetic", "hype", "run", "jump", "adrenaline"],
}
MOODS = ["Happy", "Sad", "Romantic", "Party", "Motivational", "Chill", "Energetic", "Trending Now"]
LANGUAGES = ["All languages", "English", "Punjabi", "Spanish"]

SAMPLE_SONGS = {
    "English": [
        {"title":"Golden Hour","artist":"JVKE","album":"this is what ____ feels like","mood":"Romantic","secondary_moods":["Chill"],"img":"","link":"https://www.youtube.com/results?search_query=JVKE+Golden+Hour"},
        {"title":"Good Life","artist":"OneRepublic","album":"Waking Up","mood":"Happy","secondary_moods":["Party"],"img":"","link":"https://www.youtube.com/results?search_query=OneRepublic+Good+Life"},
        {"title":"The Nights","artist":"Avicii","album":"The Days / Nights","mood":"Motivational","secondary_moods":["Energetic"],"img":"","link":"https://www.youtube.com/results?search_query=Avicii+The+Nights"},
        {"title":"Someone You Loved","artist":"Lewis Capaldi","album":"Divinely Uninspired to a Hellish Extent","mood":"Sad","secondary_moods":["Romantic"],"img":"","link":"https://www.youtube.com/results?search_query=Lewis+Capaldi+Someone+You+Loved"},
        {"title":"Sunset Lover","artist":"Petit Biscuit","album":"Presence","mood":"Chill","secondary_moods":["Romantic"],"img":"","link":"https://www.youtube.com/results?search_query=Petit+Biscuit+Sunset+Lover"}
    ],
    "Punjabi": [
        {"title":"Excuses","artist":"AP Dhillon","album":"Hidden Gems","mood":"Chill","secondary_moods":["Romantic"],"img":"","link":"https://www.youtube.com/results?search_query=AP+Dhillon+Excuses"}
    ],
    "Spanish": [
        {"title":"Vivir Mi Vida","artist":"Marc Anthony","album":"3.0","mood":"Party","secondary_moods":["Happy"],"img":"","link":"https://www.youtube.com/results?search_query=Marc+Anthony+Vivir+Mi+Vida"}
    ]
}

def load_songs() -> list[dict[str, Any]]:
    if SONGS_FILE.exists():
        try:
            raw = json.loads(SONGS_FILE.read_text(encoding="utf-8"))
            songs = []
            if isinstance(raw, dict):
                for language, entries in raw.items():
                    if isinstance(entries, list):
                        for item in entries:
                            if isinstance(item, dict):
                                song = dict(item)
                                song.setdefault("language", language)
                                songs.append(song)
            elif isinstance(raw, list):
                songs = [dict(x) for x in raw if isinstance(x, dict)]
            return [normalise_song(s) for s in songs]
        except (json.JSONDecodeError, OSError):
            pass
    songs = []
    for language, entries in SAMPLE_SONGS.items():
        for item in entries:
            song = dict(item)
            song["language"] = language
            songs.append(normalise_song(song))
    return songs

def normalise_song(song: dict[str, Any]) -> dict[str, Any]:
    song.setdefault("title", "Untitled")
    song.setdefault("artist", "Unknown artist")
    song.setdefault("album", "Single")
    song.setdefault("mood", "Trending Now")
    song.setdefault("secondary_moods", [])
    song.setdefault("img", "")
    song.setdefault("link", "")
    song.setdefault("language", "Other")
    return song

def detect_mood(message: str) -> str:
    msg = (message or "").lower()
    for mood, words in MOOD_KEYWORDS.items():
        if any(word in msg for word in words):
            return mood
    return "Trending Now"

def recommend_songs(message: str = "", mood: str = "Trending Now",
                    language: str = "All languages", query: str = "",
                    limit: int = 60) -> tuple[str, list[dict[str, Any]]]:
    selected_mood = detect_mood(message) if message.strip() else mood
    songs = load_songs()
    q = query.strip().lower()
    results = []
    for song in songs:
        song_moods = [str(song.get("mood", "")).lower()] + [
            str(x).lower() for x in song.get("secondary_moods", [])
        ]
        mood_match = selected_mood == "Trending Now" or selected_mood.lower() in song_moods
        lang_match = language == "All languages" or song.get("language", "").lower() == language.lower()
        text_match = not q or q in " ".join(str(song.get(k, "")) for k in ("title", "artist", "album", "language")).lower()
        if mood_match and lang_match and text_match:
            results.append(song)
    return selected_mood, results[:limit]

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, artist TEXT NOT NULL, album TEXT,
            language TEXT, mood TEXT, img TEXT, link TEXT,
            UNIQUE(title, artist)
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS playlist_songs (
            playlist_id INTEGER NOT NULL,
            title TEXT NOT NULL, artist TEXT NOT NULL, album TEXT,
            language TEXT, mood TEXT, img TEXT, link TEXT,
            UNIQUE(playlist_id, title, artist),
            FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
        )""")

def list_favourites():
    init_db()
    with connect_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM favourites ORDER BY id DESC")]

def add_favourite(song):
    init_db()
    with connect_db() as db:
        db.execute("""INSERT OR IGNORE INTO favourites
            (title,artist,album,language,mood,img,link) VALUES (?,?,?,?,?,?,?)""",
            tuple(song.get(k, "") for k in ("title","artist","album","language","mood","img","link")))

def remove_favourite(title, artist):
    init_db()
    with connect_db() as db:
        db.execute("DELETE FROM favourites WHERE title=? AND artist=?", (title, artist))

def list_playlists():
    init_db()
    with connect_db() as db:
        rows = db.execute("SELECT * FROM playlists ORDER BY name").fetchall()
        output = []
        for row in rows:
            songs = db.execute("SELECT * FROM playlist_songs WHERE playlist_id=?", (row["id"],)).fetchall()
            output.append({"id": row["id"], "name": row["name"], "songs": [dict(x) for x in songs]})
        return output

def create_playlist(name):
    name = name.strip()
    if not name:
        return False
    init_db()
    try:
        with connect_db() as db:
            db.execute("INSERT INTO playlists(name) VALUES (?)", (name,))
        return True
    except sqlite3.IntegrityError:
        return False

def add_to_playlist(playlist_id, song):
    init_db()
    with connect_db() as db:
        db.execute("""INSERT OR IGNORE INTO playlist_songs
            (playlist_id,title,artist,album,language,mood,img,link) VALUES (?,?,?,?,?,?,?,?)""",
            (playlist_id, song.get("title",""), song.get("artist",""), song.get("album",""),
             song.get("language",""), song.get("mood",""), song.get("img",""), song.get("link","")))
