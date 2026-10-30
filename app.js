const $ = (id) => document.getElementById(id);
let currentMood = "Trending Now";
let currentSongs = [];

function escapeHtml(value="") {
  return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function songCard(song) {
  const safe = escapeHtml(JSON.stringify(song));
  const cover = song.img ? `<img class="cover" src="${escapeHtml(song.img)}" alt="" onerror="this.outerHTML='<div class=&quot;cover&quot;>♫</div>'">` : `<div class="cover">♫</div>`;
  return `<article class="song-card">${cover}<div class="song-info"><b>${escapeHtml(song.title)}</b><small>${escapeHtml(song.artist)} · ${escapeHtml(song.language || "")}</small></div><div class="song-actions"><button class="icon-btn" title="Add to favourites" data-fav='${safe}'>♡</button><button class="icon-btn" title="Listen" data-listen='${escapeHtml(song.link || "")}' data-title="${escapeHtml(song.title)}" data-artist="${escapeHtml(song.artist)}">↗</button></div></article>`;
}
async function loadSongs(message="") {
  const params = new URLSearchParams({mood: currentMood, language:$("language").value, q:$("search").value, message});
  $("results-title").textContent = message ? "Picked for your feeling" : `Songs for ${currentMood.toLowerCase()}`;
  $("results-eyebrow").textContent = "YOUR MUSIC PICKS";
  $("song-grid").innerHTML = `<div class="empty-state">Finding your music…</div>`;
  const response = await fetch(`/api/songs?${params}`);
  const data = await response.json();
  currentMood = data.mood;
  currentSongs = data.songs;
  $("results-title").textContent = `Songs for ${currentMood.toLowerCase()}`;
  $("song-grid").innerHTML = data.songs.length ? data.songs.map(songCard).join("") : `<div class="empty-state">No matches yet. Try another mood, language or search.</div>`;
}
async function loadFavourites() {
  const songs = await (await fetch("/api/favourites")).json();
  $("favourites-grid").innerHTML = songs.length ? songs.map(songCard).join("") : `<div class="empty-state">Your favourites will live here. Tap ♡ on any song to save it.</div>`;
}
async function loadPlaylists() {
  const lists = await (await fetch("/api/playlists")).json();
  $("playlist-list").innerHTML = lists.length ? lists.map(p => `<div class="playlist-card"><b>${escapeHtml(p.name)}</b><small>${p.songs.length} saved song(s)</small>${p.songs.map(s=>`<small>♫ ${escapeHtml(s.title)} — ${escapeHtml(s.artist)}</small>`).join("")}</div>`).join("") : `<div class="empty-state">Create your first playlist to collect songs for every kind of day.</div>`;
}
document.addEventListener("click", async e => {
  const mood = e.target.closest("[data-mood]");
  if (mood) { currentMood = mood.dataset.mood; $("search").value=""; await loadSongs(); }
  const fav = e.target.closest("[data-fav]");
  if (fav) { await fetch("/api/favourites",{method:"POST",headers:{"Content-Type":"application/json"},body:fav.dataset.fav}); fav.textContent="♥"; }
  const listen = e.target.closest("[data-listen]");
  if (listen) {
    $("now-title").textContent=listen.dataset.title;
    $("now-artist").textContent=listen.dataset.artist;
    if (listen.dataset.listen) window.open(listen.dataset.listen,"_blank","noopener");
  }
  const nav = e.target.closest("[data-view]");
  if (nav) {
    document.querySelectorAll(".view").forEach(v=>v.classList.add("hidden"));
    $(`${nav.dataset.view}-view`).classList.remove("hidden");
    document.querySelectorAll(".nav-item").forEach(n=>n.classList.toggle("active",n===nav));
    $("page-title").textContent = ({discover:"Find your sound.",favourites:"Your favourites.",playlists:"Your playlists."})[nav.dataset.view];
    if(nav.dataset.view==="favourites") loadFavourites();
    if(nav.dataset.view==="playlists") loadPlaylists();
  }
});
$("mood-form").addEventListener("submit", async e=>{e.preventDefault(); currentMood="Trending Now"; await loadSongs($("mood-message").value);});
$("language").addEventListener("change",()=>loadSongs());
let searchTimer;
$("search").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadSongs(),220);});
$("playlist-form").addEventListener("submit",async e=>{
  e.preventDefault(); const name=$("playlist-name").value.trim(); if(!name)return;
  const res=await fetch("/api/playlists",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name})});
  if(res.ok){$("playlist-name").value="";loadPlaylists();} else alert("That playlist name may already exist.");
});
loadSongs();
