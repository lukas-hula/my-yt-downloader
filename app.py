import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- KONFIGURACE ---
st.set_page_config(page_title="AudioFlow Pro", page_icon="🎵", layout="centered")

# --- DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .main-card { text-align: center; max-width: 550px; margin: 0 auto; }
    .title-text { font-weight: 800; font-size: 3rem; color: #1d1d1f; margin-bottom: 5px; }
    .subtitle-text { color: #86868b; font-size: 1.1rem; margin-bottom: 40px; }
    .analysis-table { width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f5f5f7; border-radius: 15px; overflow: hidden; }
    .analysis-table td { padding: 15px 20px; border-bottom: 1px solid #e5e5e7; text-align: left; }
    .label-col { color: #86868b !important; font-weight: 600; width: 40%; }
    
    /* Styly pro tlačítka služeb */
    .service-link {
        display: inline-block;
        padding: 8px 15px;
        margin: 5px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        transition: 0.2s;
    }
    .chordify { background-color: #eb613d; color: white !important; }
    .genius { background-color: #ffff64; color: black !important; }
    .youtube { background-color: #ff0000; color: white !important; }
    
    .download-link { 
        display: block; background-color: #0071e3 !important; color: white !important; 
        padding: 18px; border-radius: 15px; text-decoration: none; font-weight: 700; 
        margin-top: 15px; text-align: center; font-size: 1.1rem;
    }
    .history-title { margin-top: 50px; font-weight: 800; font-size: 1.8rem; color: #1d1d1f; text-align: left; border-bottom: 2px solid #f5f5f7; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCE PRO LOGOVÁNÍ ---
def log_to_csv(title, video_id, duration_str):
    log_file = "history.csv"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    new_data = pd.DataFrame([{"Čas": timestamp, "Skladba": title, "ID": video_id, "Délka": duration_str}])
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(log_file, mode='a', index=False, header=False, encoding='utf-8-sig')

# --- UI ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Hudební nástroj nové generace</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("ZPRACOVAT SKLADBU")

if submit_btn and url_input:
    # Extrakce ID
    video_id = ""
    if "v=" in url_input: video_id = url_input.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_input: video_id = url_input.split("youtu.be/")[1].split("?")[0]
    else: video_id = url_input.split("/")[-1].split("?")[0]

    if video_id:
        try:
            RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
            headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"}
            
            with st.spinner("Příprava chytrých odkazů..."):
                response = requests.get("https://youtube-mp36.p.rapidapi.com/dl", headers=headers, params={"id": video_id})
                data = response.json()

                if data.get("status") == "ok":
                    title = data.get('title')
                    duration_str = f"{int(data.get('duration') // 60)}m {int(data.get('duration') % 60):02d}s"
                    
                    # Logování
                    log_to_csv(title, video_id, duration_str)
                    
                    # Generování vyhledávacích dotazů pro externí služby
                    search_query = urllib.parse.quote(title)
                    chordify_url = f"https://chordify.net/search/{search_query}"
                    genius_url = f"https://genius.com/search?q={search_query}"
                    yt_url = f"https://www.youtube.com/watch?v={video_id}"

                    st.balloons()
                    st.markdown(f"""
                        <table class="analysis-table">
                            <tr><td class="label-col">Skladba</td><td>{title}</td></tr>
                            <tr><td class="label-col">Délka</td><td>{duration_str}</td></tr>
                            <tr>
                                <td class="label-col">Služby</td>
                                <td>
                                    <a href="{chordify_url}" target="_blank" class="service-link chordify">🎸 Akordy</a>
                                    <a href="{genius_url}" target="_blank" class="service-link genius">📝 Text</a>
                                    <a href="{yt_url}" target="_blank" class="service-link youtube">📺 Video</a>
                                </td>
                            </tr>
                        </table>
                        <a href="{data.get('link')}" target="_blank" class="download-link">💾 STÁHNOUT MP3</a>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Chyba při komunikaci s YouTube serverem.")
        except Exception as e:
            st.error(f"Chyba: {e}")
    else:
        st.warning("Neplatný odkaz.")

# --- HISTORIE ---
st.markdown('<div class="history-title">Historie stažení</div>', unsafe_allow_html=True)
if os.path.isfile("history.csv"):
    df_history = pd.read_csv("history.csv")
    st.dataframe(df_history.sort_index(ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("Historie je prázdná.")

st.markdown('</div>', unsafe_allow_html=True)
