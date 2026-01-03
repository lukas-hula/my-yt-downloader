import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- KONFIGURACE ---
st.set_page_config(page_title="AudioFlow Pro", page_icon="🎵", layout="centered")

# --- DESIGN (Oprava paddingu tlačítka) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .main-card { text-align: center; max-width: 550px; margin: 0 auto; }
    .title-text { font-weight: 800; font-size: 3rem; color: #1d1d1f; margin-bottom: 5px; }
    .subtitle-text { color: #86868b; font-size: 1.1rem; margin-bottom: 40px; }
    
    /* Vylepšené Černé tlačítko s větším paddingem */
    .stButton button { 
        background-color: #1d1d1f !important; 
        color: white !important; 
        border-radius: 30px !important; /* Více zaoblené */
        width: 100% !important; 
        border: none !important; 
        padding: 16px 32px !important; /* Zvětšený padding (nahoře/dole, vlevo/vpravo) */
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em !important; /* Rozestup písmen */
        transition: all 0.2s ease-in-out !important;
    }

    /* Efekt při najetí myší */
    .stButton button:hover {
        background-color: #333333 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Tabulka s miniaturou */
    .analysis-table { width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f5f5f7; border-radius: 15px; overflow: hidden; }
    .analysis-table td { padding: 15px 20px; border-bottom: 1px solid #e5e5e7; text-align: left; vertical-align: middle; }
    .label-col { color: #86868b !important; font-weight: 600; width: 35%; }
    .mini-thumb { width: 80px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    
    .stTextInput input { border-radius: 12px !important; background-color: #f5f5f7 !important; border: 1px solid #d2d2d7 !important; padding: 12px !important; }
    
    .service-link { display: inline-block; padding: 6px 12px; margin: 2px 4px 2px 0; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: 600; }
    .chordify { background-color: #eb613d; color: white !important; }
    .genius { background-color: #ffff64; color: black !important; }
    
    .download-link { 
        display: block; background-color: #0071e3 !important; color: white !important; 
        padding: 18px; border-radius: 15px; text-decoration: none; font-weight: 700; 
        margin-top: 15px; text-align: center; font-size: 1.1rem; 
    }
    .history-title { margin-top: 50px; font-weight: 800; font-size: 1.8rem; color: #1d1d1f; text-align: left; border-bottom: 2px solid #f5f5f7; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def log_to_csv(title, video_id, duration_str):
    log_file = "history.csv"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    new_data = pd.DataFrame([{"Čas": timestamp, "Skladba": title, "ID": video_id, "Délka": duration_str}])
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(log_file, mode='a', index=False, header=False, encoding='utf-8-sig')

# --- HLAVNÍ STRÁNKA ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Profesionální hudební nástroj</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("PŘIPRAVIT MP3")

if submit_btn and url_input:
    video_id = ""
    if "v=" in url_input: video_id = url_input.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_input: video_id = url_input.split("youtu.be/")[1].split("?")[0]
    
    if video_id:
        try:
            # Metadata přes oEmbed
            info_res = requests.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json")
            video_info = info_res.json()
            title = video_info.get('title', 'Skladba z YouTube')
            thumb_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" # Menší náhled pro tabulku
            
            # RapidAPI pro MP3
            RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
            headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"}
            
            with st.spinner("Zpracovávám..."):
                found_link = None
                duration_str = "Neznámo"
                for _ in range(8):
                    res = requests.get("https://youtube-mp36.p.rapidapi.com/dl", headers=headers, params={"id": video_id})
                    api_data = res.json()
                    if api_data.get("status") == "ok":
                        found_link = api_data.get("link")
                        duration = api_data.get("duration", 0)
                        duration_str = f"{int(duration // 60)}m {int(duration % 60):02d}s"
                        break
                    time.sleep(2)
            
            search_query = urllib.parse.quote(title)
            
            # ZOBRAZENÍ TABULKY S MINIATUROU A ÚDAJI
            st.markdown(f"""
                <table class="analysis-table">
                    <tr>
                        <td class="label-col">Náhled</td>
                        <td><img src="{thumb_url}" class="mini-thumb"></td>
                    </tr>
                    <tr><td class="label-col">Název</td><td>{title}</td></tr>
                    <tr><td class="label-col">Délka</td><td>{duration_str}</td></tr>
                    <tr><td class="label-col">Kvalita</td><td>320 kbps (HD)</td></tr>
                    <tr><td class="label-col">YouTube ID</td><td><code>{video_id}</code></td></tr>
                    <tr>
                        <td class="label-col">Externí zdroje</td>
                        <td>
                            <a href="https://chordify.net/search/{search_query}" target="_blank" class="service-link chordify">🎸 Akordy</a>
                            <a href="https://genius.com/search?q={search_query}" target="_blank" class="service-link genius">📝 Text</a>
                        </td>
                    </tr>
                </table>
            """, unsafe_allow_html=True)
            
            if found_link:
                st.balloons()
                st.markdown(f'<a href="{found_link}" target="_blank" class="download-link">💾 STÁHNOUT SOUBOR</a>', unsafe_allow_html=True)
                log_to_csv(title, video_id, duration_str)
            else:
                st.warning("⚠️ Převod trvá déle než obvykle. Zkuste prosím za okamžik znovu kliknout na tlačítko.")
                
        except Exception as e:
            st.error("Chyba při komunikaci se serverem.")
    else:
        st.warning("Vložte platný odkaz.")

# --- HISTORIE ---
st.markdown('<div class="history-title">Historie stažení</div>', unsafe_allow_html=True)
if os.path.isfile("history.csv"):
    df_history = pd.read_csv("history.csv")
    st.dataframe(df_history.sort_index(ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("Historie je prázdná.")
st.markdown('</div>', unsafe_allow_html=True)
