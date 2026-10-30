# CodeCuddles — Music Discovery

A shared music-discovery project with:
- A Flask web app
- A Python desktop app (Tkinter)
- Mood-based recommendations
- Search and language filtering
- Favourites and playlists saved in SQLite
- Support for your existing `songs.json` file

## 1. Set up

Install Python 3.10 or newer. Open a terminal in this folder:

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Add your music database

Put your existing `songs.json` in the project root (beside `app.py`).

Each song should look like:

```json
{
  "English": [
    {
      "title": "Song title",
      "artist": "Artist name",
      "album": "Album name",
      "mood": "Chill",
      "secondary_moods": ["Happy"],
      "img": "https://example.com/cover.jpg",
      "link": "https://example.com/listen"
    }
  ]
}
```

The app also works without `songs.json` and loads a small sample catalogue. Replace the sample with your own properly licensed/linked catalogue.

## 3. Run the web app

```bash
python app.py
```

Open http://127.0.0.1:5000

For access from another device on the same Wi-Fi, run:

```bash
python app.py --host 0.0.0.0
```

Then open `http://YOUR-COMPUTER-IP:5000` on that device. Do not expose the development server directly to the public internet.

## 4. Run the desktop app

In another terminal:

```bash
python desktop.py
```

Both apps use the same `songs.json` and `codecuddles.db`, so favourites and playlists are shared when run on the same computer.

## 5. Important notes

- Mood detection currently uses transparent keyword matching, not a trained AI model.
- The Listen button opens the song's supplied `link`; it does not stream or host copyrighted audio.
- Image loading is optional. Broken or unavailable image URLs fall back to a designed placeholder.
- The included catalogue is only sample data. Add your own verified song metadata and links.
