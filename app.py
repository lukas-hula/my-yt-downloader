import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- KONFIGURACE ---
st.set_page_config(page_title="AudioFlow Pro", page_icon="🎵", layout="centered")

# --- KOMPLETNÍ OPRAVA DESIGNU (Light Mode & Fix oříznutí) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp { background-color: #ffffff !important; font-family: 'Inter', sans-serif; color: #1d1d1f !important; }
    .title-text { font-weight: 800; font-size: 3rem; color: #1d1d1f !important; margin-bottom: 5px; }
    .subtitle-text { color: #86868b !important; font-size: 1.1rem; margin-bottom: 40px; }
    
    /* FIX OŘÍZNUTÍ INPUTU */
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] div {
        height: auto !important;
        min-height: unset !important;
        max-height: unset !important;
        background-color: transparent !important;
    }

    /* OPRAVA TABULKY HISTORIE - Vynucení světlého vzhledu */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e5e7 !important;
        border-radius: 15px !important;
    }

    /* Barva textu v buňkách a hlavičce */
    [data-testid="stDataFrame"] div[data-testid="stTable"] td, 
    [data-testid="stDataFrame"] div[data-testid="stTable"] th {
        color: #1d1d1f !important;
        background-color: #ffffff !important;
    }

    /* Oprava nečitelných ikon v pravém horním rohu tabulky */
    [data-testid="stDataFrameToolbar"] button {
        color: #1d1d1f !important;
        fill: #1d1d1f !important;
    }
    
    /* Tabulka metadat skladby */
    .analysis-table { width: 100%; border-collapse: collapse; margin: 10px 0; background-color: #f5f5f7; border-radius: 15px; overflow: hidden; }
    .analysis-table td { padding: 15px 20px; border-bottom: 1px solid #e5e5e7; text-align: left; color: #1d1d1f !important; }
    
    /* Tlačítka a ostatní zůstává zafixováno */
    .stButton button { background-color: #1d1d1f !important; color: white !important; border-radius: 30px !important; padding: 16px 32px !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCE ---
def get_itunes_meta(query):
    try:
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=song&limit=1"
        res = requests.get(url).json()
        if res['resultCount'] > 0:
            track = res['results'][0]
            return {"album": track.get("collectionName", "Neznámo"), "genre": track.get("primaryGenreName", "Neznámo"), "year": track.get("releaseDate", "0000")[:4]}
    except: pass
    return None

def log_to_csv(title, video_id, duration_str):
    log_file = "history.csv"
    new_data = pd.DataFrame([{"Čas": datetime.now().strftime("%d.%m.%Y %H:%M"), "Skladba": title, "ID": video_id, "Délka": duration_str}])
    if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False, encoding='utf-8-sig')
    else: new_data.to_csv(log_file, mode='a', index=False, header=False, encoding='utf-8-sig')

# --- HLAVNÍ STRÁNKA ---
st.markdown('<div class="main-card"><h1 class="title-text">AudioFlow</h1><p class="subtitle-text">Hudební nástroj nové generace</p>', unsafe_allow_html=True)
url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("PŘIPRAVIT MP3")

if submit_btn and url_input:
    video_id = url_input.split("v=")[1].split("&")[0] if "v=" in url_input else url_input.split("/")[-1].split("?")[0]
    if video_id:
        try:
            info_res = requests.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json").json()
            title = info_res.get('title', 'Skladba')
            music_meta = get_itunes_meta(title)
            
            with st.spinner("Zpracovávám..."):
                headers = {"x-rapidapi-key": st.secrets["RAPIDAPI_KEY"], "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"}
                api_data = requests.get("https://youtube-mp36.p.rapidapi.com/dl", headers=headers, params={"id": video_id}).json()
                found_link = api_data.get("link")
                dur = api_data.get("duration", 0)
                duration_str = f"{int(dur // 60)}m {int(dur % 60):02d}s"

            st.markdown(f'<table class="analysis-table"><tr><td class="label-col">Skladba</td><td><img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" class="mini-thumb"><br><strong>{title}</strong></td></tr><tr><td class="label-col">Délka</td><td>{duration_str}</td></tr></table>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={video_id}")

            itunes_rows = ""
            if music_meta:
                itunes_rows = f'<tr><td class="label-col">Album</td><td>{music_meta["album"]}</td></tr><tr><td class="label-col">Žánr</td><td>{music_meta["genre"]}</td></tr><tr><td class="label-col">Rok</td><td>{music_meta["year"]}</td></tr>'

            search_query = urllib.parse.quote(title)
            st.markdown(f'<table class="analysis-table">{itunes_rows}<tr><td class="label-col">Kvalita</td><td>320 kbps (HD)</td></tr><tr><td class="label-col">YouTube ID</td><td><code>{video_id}</code></td></tr><tr><td class="label-col">Služby</td><td><a href="https://chordify.net/search/{search_query}" target="_blank" class="service-link chordify">🎸 Akordy</a><a href="https://genius.com/search?q={search_query}" target="_blank" class="service-link genius">📝 Text</a><a href="https://open.spotify.com/search/{search_query}" target="_blank" class="service-link spotify">🎧 Spotify</a></td></tr></table>', unsafe_allow_html=True)
            
            if found_link:
                st.balloons()
                st.markdown(f'<a href="{found_link}" target="_blank" class="download-link">💾 STÁHNOUT SOUBOR</a>', unsafe_allow_html=True)
                log_to_csv(title, video_id, duration_str)
        except: st.error("Chyba při zpracování.")
st.markdown('</div>', unsafe_allow_html=True)

# --- HISTORIE ---
st.markdown('<div class="history-title">Historie stažení</div>', unsafe_allow_html=True)
if os.path.isfile("history.csv"): 
    df = pd.read_csv("history.csv").sort_index(ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)
else: st.info("Historie je prázdná.")
