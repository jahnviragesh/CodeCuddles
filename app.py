from flask import Flask, jsonify, render_template, request
import argparse
from music_core import (recommend_songs, list_favourites, add_favourite,
    remove_favourite, list_playlists, create_playlist, add_to_playlist, init_db)

app = Flask(__name__)
init_db()

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/songs")
def songs():
    mood, results = recommend_songs(
        message=request.args.get("message", ""),
        mood=request.args.get("mood", "Trending Now"),
        language=request.args.get("language", "All languages"),
        query=request.args.get("q", "")
    )
    return jsonify({"mood": mood, "songs": results, "count": len(results)})

@app.get("/api/favourites")
def favourites():
    return jsonify(list_favourites())

@app.post("/api/favourites")
def favourite_add():
    add_favourite(request.get_json(force=True))
    return jsonify({"ok": True})

@app.delete("/api/favourites")
def favourite_delete():
    data = request.get_json(force=True)
    remove_favourite(data.get("title", ""), data.get("artist", ""))
    return jsonify({"ok": True})

@app.get("/api/playlists")
def playlists():
    return jsonify(list_playlists())

@app.post("/api/playlists")
def playlist_create():
    data = request.get_json(force=True)
    ok = create_playlist(data.get("name", ""))
    return jsonify({"ok": ok}), (200 if ok else 400)

@app.post("/api/playlists/<int:playlist_id>/songs")
def playlist_add(playlist_id):
    add_to_playlist(playlist_id, request.get_json(force=True))
    return jsonify({"ok": True})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)
