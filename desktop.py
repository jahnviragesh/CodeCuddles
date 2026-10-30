"""CodeCuddles desktop companion. Uses the same music_core.py and SQLite database."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
from music_core import MOODS, LANGUAGES, recommend_songs, list_favourites, add_favourite

BG = "#F7F6F8"
INK = "#24212A"
MUTED = "#89838F"
PURPLE = "#65468B"
WHITE = "#FFFFFF"

class CodeCuddlesDesktop:
    def __init__(self, root):
        self.root = root
        root.title("CodeCuddles — Your music, your mood")
        root.geometry("1040x760")
        root.minsize(760, 600)
        root.configure(bg=BG)
        self.mood = tk.StringVar(value="Trending Now")
        self.language = tk.StringVar(value="All languages")
        self.message = tk.StringVar()
        self.search = tk.StringVar()
        self.build_ui()
        self.show_songs()

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=34, pady=(25, 15))
        tk.Label(header, text="CodeCuddles", bg=BG, fg=INK,
                 font=("Georgia", 25, "bold")).pack(side="left")
        tk.Label(header, text="YOUR PERSONAL MUSIC COMPANION", bg=BG, fg=MUTED,
                 font=("Arial", 8, "bold")).pack(side="right", pady=12)

        hero = tk.Frame(self.root, bg="#5C4479", padx=28, pady=23)
        hero.pack(fill="x", padx=34)
        tk.Label(hero, text="What's your vibe today?", bg="#5C4479", fg=WHITE,
                 font=("Georgia", 25)).pack(anchor="w")
        tk.Label(hero, text="Tell us how you're feeling. We'll help you find your music.",
                 bg="#5C4479", fg="#E7DDED", font=("Arial", 10)).pack(anchor="w", pady=(7, 0))

        mood_area = tk.Frame(self.root, bg=BG)
        mood_area.pack(fill="x", padx=34, pady=(23, 12))
        tk.Label(mood_area, text="CHOOSE YOUR MOOD", bg=BG, fg=MUTED,
                 font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 10))
        moods = ["Happy", "Sad", "Romantic", "Party", "Chill", "Motivational", "Energetic"]
        mood_row = tk.Frame(mood_area, bg=BG)
        mood_row.pack(fill="x")
        for mood in moods:
            tk.Button(mood_row, text=mood, command=lambda m=mood: self.choose_mood(m),
                      bg=WHITE, fg=PURPLE, activebackground="#F0EAF6",
                      relief="flat", bd=0, padx=13, pady=10,
                      font=("Arial", 9, "bold"), cursor="hand2").pack(side="left", padx=(0, 7))

        search_area = tk.Frame(self.root, bg=BG)
        search_area.pack(fill="x", padx=34, pady=10)
        entry = tk.Entry(search_area, textvariable=self.message, font=("Arial", 11),
                         relief="flat", bg=WHITE, fg=INK)
        entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 8))
        entry.insert(0, "")
        tk.Button(search_area, text="Find my music", command=self.detect_and_show,
                  bg=PURPLE, fg=WHITE, relief="flat", padx=18, pady=10,
                  font=("Arial", 9, "bold")).pack(side="left")

        filters = tk.Frame(self.root, bg=BG)
        filters.pack(fill="x", padx=34, pady=(12, 8))
        tk.Label(filters, text="YOUR SONGS", bg=BG, fg=INK,
                 font=("Georgia", 18)).pack(side="left")
        ttk.Combobox(filters, textvariable=self.language, values=LANGUAGES,
                     state="readonly", width=16).pack(side="right")
        self.language.trace_add("write", lambda *_: self.show_songs())

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=BG)
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(34, 0), pady=(5, 20))
        self.scroll.pack(side="right", fill="y", padx=(0, 24), pady=(5, 20))

        footer = tk.Frame(self.root, bg=WHITE, height=48)
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text="♫  Your music, your mood.", bg=WHITE, fg=MUTED,
                 font=("Arial", 9)).pack(pady=14)

    def choose_mood(self, mood):
        self.mood.set(mood)
        self.message.set("")
        self.show_songs()

    def detect_and_show(self):
        _, songs = recommend_songs(message=self.message.get(),
                                   language=self.language.get())
        self.render(songs)

    def show_songs(self):
        _, songs = recommend_songs(mood=self.mood.get(),
                                   language=self.language.get())
        self.render(songs)

    def render(self, songs):
        for child in self.list_frame.winfo_children():
            child.destroy()
        if not songs:
            tk.Label(self.list_frame, text="No songs found. Try another mood or language.",
                     bg=BG, fg=MUTED, font=("Arial", 11)).pack(pady=30)
            return
        for song in songs:
            card = tk.Frame(self.list_frame, bg=WHITE, padx=13, pady=12,
                            highlightbackground="#ECE9EF", highlightthickness=1)
            card.pack(fill="x", pady=5, padx=(0, 12))
            cover = tk.Label(card, text="♫", bg="#EEE8F5", fg=PURPLE,
                             width=4, height=2, font=("Georgia", 19))
            cover.pack(side="left", padx=(0, 13))
            info = tk.Frame(card, bg=WHITE)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=song["title"], bg=WHITE, fg=INK,
                     font=("Arial", 11, "bold")).pack(anchor="w")
            tk.Label(info, text=f'{song["artist"]}  ·  {song["album"]}  ·  {song["language"]}',
                     bg=WHITE, fg=MUTED, font=("Arial", 9)).pack(anchor="w", pady=(4, 0))
            tk.Button(card, text="♡", command=lambda s=song: self.save_favourite(s),
                      bg=WHITE, fg=PURPLE, relief="flat", font=("Arial", 16)).pack(side="right", padx=5)
            tk.Button(card, text="Listen ↗", command=lambda s=song: self.listen(s),
                      bg="#F2EDF7", fg=PURPLE, relief="flat", padx=12, pady=7,
                      font=("Arial", 9, "bold")).pack(side="right")

    def save_favourite(self, song):
        add_favourite(song)
        messagebox.showinfo("CodeCuddles", f'Added "{song["title"]}" to your favourites.')

    def listen(self, song):
        if song.get("link"):
            webbrowser.open(song["link"])
        else:
            messagebox.showwarning("No listening link", "This song does not have a listening link yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeCuddlesDesktop(root)
    root.mainloop()
