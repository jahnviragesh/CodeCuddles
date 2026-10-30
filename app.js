// CodeCuddles — static GitHub Pages edition
const $ = (id) => document.getElementById(id);
const STORAGE = { favourites: "codecuddles-favourites", playlists: "codecuddles-playlists" };
let catalogue = [];
let currentMood = "Trending Now";

const readStore = (key, fallback=[]) => {
  try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch { return fallback; }
};
const writeStore = (key, value) => localStorage.setItem(key, JSON.stringify(value));
const escapeHtml = (value="") => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const songKey = s => [s.title,s.artist,s.language].join("|");
const allSongs = () => catalogue.flatMap(group => group.songs.map(song => ({...song,language:group.language})));
function card(song) {
  const key=encodeURIComponent(JSON.stringify(song));
  const saved=readStore(STORAGE.favourites).some(s=>songKey(s)===songKey(song));
  const cover=song.img ? '<img class="cover" src="'+escapeHtml(song.img)+'" alt="" onerror="this.style.display=\'none\'">' : '<div class="cover">♫</div>';
  return '<article class="song-card">'+cover+'<div class="song-info"><b>'+escapeHtml(song.title)+'</b><small>'+escapeHtml(song.artist)+' · '+escapeHtml(song.language)+'</small></div><div class="song-actions"><button class="icon-btn" title="Favourite" data-fav="'+key+'">'+(saved?"♥":"♡")+'</button><button class="icon-btn" title="Add to playlist" data-add="'+key+'">＋</button><button class="icon-btn" title="Listen" data-listen="'+escapeHtml(song.link||"")+'" data-title="'+escapeHtml(song.title)+'" data-artist="'+escapeHtml(song.artist)+'">↗</button></div></article>';
}
function renderSongs(songs, target="song-grid") {
  $(target).innerHTML=songs.length?songs.map(card).join(""):'<div class="empty-state">No matches found. Try another mood or search.</div>';
}
function moodFromText(text) {
  const t=text.toLowerCase();
  const map={Happy:["happy","good","cheerful","joy","upbeat","sunny"],Sad:["sad","down","heartbroken","cry","lonely"],Romantic:["love","romantic","date","crush"],Party:["party","dance","celebrate","club"],Chill:["chill","calm","relax","peaceful","study"],Motivational:["motivate","motivated","focus","workout","energy","inspire","morning"]};
  for(const [m,words] of Object.entries(map)) if(words.some(w=>t.includes(w))) return m;
  return "Trending Now";
}
function filteredSongs(message="") {
  const language=$("language").value, query=$("search").value.trim().toLowerCase();
  let songs=allSongs();
  if(currentMood!=="Trending Now") songs=songs.filter(s=>s.mood===currentMood||(s.secondary_moods||[]).includes(currentMood));
  if(language!=="All languages") songs=songs.filter(s=>s.language===language);
  if(query) songs=songs.filter(s=>(s.title+" "+s.artist+" "+s.album).toLowerCase().includes(query));
  if(message && currentMood==="Trending Now") songs=songs.filter(s=>true);
  return songs;
}
function loadSongs(message="") {
  if(message) currentMood=moodFromText(message);
  $("results-title").textContent=currentMood==="Trending Now"?"Songs to explore":'Songs for '+currentMood.toLowerCase();
  $("results-eyebrow").textContent="YOUR MUSIC PICKS";
  renderSongs(filteredSongs(message));
}
function loadFavourites(){renderSongs(readStore(STORAGE.favourites),"favourites-grid");}
function loadPlaylists(){
  const lists=readStore(STORAGE.playlists);
  $("playlist-list").innerHTML=lists.length?lists.map((p,i)=>'<div class="playlist-card"><b>'+escapeHtml(p.name)+'</b><small>'+p.songs.length+' saved song(s)</small>'+p.songs.map(s=>'<small>♫ '+escapeHtml(s.title)+' — '+escapeHtml(s.artist)+'</small>').join("")+'<button class="icon-btn" data-delete-playlist="'+i+'" aria-label="Delete playlist">×</button></div>').join(""):'<div class="empty-state">Create your first playlist to collect songs for every kind of day.</div>';
}
function showView(name) {
  document.querySelectorAll(".view").forEach(v=>v.classList.add("hidden"));
  $(name+"-view").classList.remove("hidden");
  document.querySelectorAll(".nav-item").forEach(n=>n.classList.toggle("active",n.dataset.view===name));
  $("page-title").textContent=({discover:"Find your sound.",favourites:"Your favourites.",playlists:"Your playlists."})[name];
  if(name==="favourites")loadFavourites();
  if(name==="playlists")loadPlaylists();
}
document.addEventListener("click",e=>{
  const mood=e.target.closest("[data-mood]");
  if(mood){currentMood=mood.dataset.mood;$("search").value="";loadSongs();}
  const nav=e.target.closest("[data-view]");if(nav)showView(nav.dataset.view);
  const fav=e.target.closest("[data-fav]");
  if(fav){const song=JSON.parse(decodeURIComponent(fav.dataset.fav));let items=readStore(STORAGE.favourites);const exists=items.some(s=>songKey(s)===songKey(song));items=exists?items.filter(s=>songKey(s)!==songKey(song)):[...items,song];writeStore(STORAGE.favourites,items);fav.textContent=exists?"♡":"♥";if(!$("favourites-view").classList.contains("hidden"))loadFavourites();}
  const add=e.target.closest("[data-add]");
  if(add){const song=JSON.parse(decodeURIComponent(add.dataset.add));const lists=readStore(STORAGE.playlists);if(!lists.length){alert("Create a playlist first, then add songs here.");showView("playlists");return;}const choice=prompt("Add to which playlist?\n"+lists.map((p,i)=>(i+1)+". "+p.name).join("\n"));const index=Number(choice)-1;if(Number.isInteger(index)&&lists[index]){if(!lists[index].songs.some(s=>songKey(s)===songKey(song)))lists[index].songs.push(song);writeStore(STORAGE.playlists,lists);add.textContent="✓";}}
  const listen=e.target.closest("[data-listen]");
  if(listen){$("now-title").textContent=listen.dataset.title;$("now-artist").textContent=listen.dataset.artist;if(listen.dataset.listen)window.open(listen.dataset.listen,"_blank","noopener,noreferrer");}
  const del=e.target.closest("[data-delete-playlist]");
  if(del){const lists=readStore(STORAGE.playlists);lists.splice(Number(del.dataset.deletePlaylist),1);writeStore(STORAGE.playlists,lists);loadPlaylists();}
});
$("mood-form").addEventListener("submit",e=>{e.preventDefault();loadSongs($("mood-message").value);});
$("language").addEventListener("change",()=>loadSongs());
let searchTimer;
$("search").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadSongs(),180);});
$("playlist-form").addEventListener("submit",e=>{e.preventDefault();const name=$("playlist-name").value.trim();if(!name)return;const lists=readStore(STORAGE.playlists);if(lists.some(p=>p.name.toLowerCase()===name.toLowerCase())){alert("That playlist already exists.");return;}lists.push({name,songs:[]});writeStore(STORAGE.playlists,lists);$("playlist-name").value="";loadPlaylists();});
async function init(){
  try{
    const response=await fetch(new URL("songs.json",document.baseURI));
    if(!response.ok)throw new Error("Could not load song catalogue");
    const data=await response.json();
    catalogue=Object.entries(data).map(([language,songs])=>({language,songs}));
    loadSongs();
  }catch(error){$("song-grid").innerHTML='<div class="empty-state">Could not load songs. Please refresh the page and try again.</div>';console.error(error);}
}
init();
