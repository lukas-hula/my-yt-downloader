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
    .thumbnail-img { width: 100%; border-radius: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .analysis-table { width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #f5f5f7; border-radius: 15px; overflow: hidden; }
    .analysis-table td { padding: 15px 20px; border-bottom: 1px solid #e5e5e7; text-align: left; }
    .label-col { color: #86868b !important; font-weight: 600; width: 40%; }
    .service-link { display: inline-block; padding: 8px 15px; margin: 5px 5px 5px 0; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 600; }
    .chordify { background-color: #eb613d; color: white !important; }
    .genius { background-color: #ffff64; color: black !important; }
    .download-link { display: block; background-color: #0071e3 !important; color: white !important; padding: 18px; border-radius: 15px; text-decoration: none; font-weight: 700; margin-top: 15px; text-align: center; }
    .history-title { margin-top: 50px; font-weight: 800; font-size: 1.8rem; color: #1d1d1f; text-align: left; border-bottom: 2px solid #f5f5f7; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCE PRO LOGOVÁNÍ ---
def log_to_csv(title, video_id):
    log_file = "history.csv"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    new_data = pd.DataFrame([{"Čas": timestamp, "Skladba": title, "ID": video_id}])
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
    # Extrakce ID videa
    video_id = ""
    if "v=" in url_input: video_id = url_input.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_input: video_id = url_input.split("youtu.be/")[1].split("?")[0]
    else: video_id = url_input.split("/")[-1].split("?")[0]

    if video_id:
        try:
            # Použijeme stabilní Cobalt API (prostředník)
            with st.spinner("Získávám data ze serveru..."):
                payload = {"url": url_input, "isAudioOnly": True}
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                response = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=headers)
                data = response.json()

                if data.get("url"):
                    # Získání názvu přes oEmbed (bezpečnější)
                    info_res = requests.get(f"https://www.youtube.com/oembed?url={url_input}&format=json")
                    title = info_res.json().get('title', 'Skladba z YouTube')
                    
                    thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                    log_to_csv(title, video_id)
                    
                    search_query = urllib.parse.quote(title)
                    chordify_url = f"https://chordify.net/search/{search_query}"
                    genius_url = f"https://genius.com/search?q={search_query}"

                    st.balloons()
                    st.markdown(f'<img src="{thumb_url}" class="thumbnail-img">', unsafe_allow_html=True)
                    st.markdown(f"""
                        <table class="analysis-table">
                            <tr><td class="label-col">Skladba</td><td>{title}</td></tr>
                            <tr><td class="label-col">Status</td><td>Připraveno ke stažení</td></tr>
                            <tr>
                                <td class="label-col">Hledat</td>
                                <td>
                                    <a href="{chordify_url}" target="_blank" class="service-link chordify">🎸 Akordy</a>
                                    <a href="{genius_url}" target="_blank" class="service-link genius">📝 Text</a>
                                </td>
                            </tr>
                        </table>
                        <a href="{data.get('url')}" target="_blank" class="download-link">💾 STÁHNOUT MP3 SOUBOR</a>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Nepodařilo se vygenerovat odkaz. Zkuste to prosím znovu za chvíli.")
        except Exception as e:
            st.error(f"Chyba při komunikaci: Služba je momentálně přetížena.")
    else:
        st.warning("Neplatný odkaz.")

# --- HISTORIE ---
st.markdown('<div class="history-title">Historie a metadata</div>', unsafe_allow_html=True)
if os.path.isfile("history.csv"):
    df_history = pd.read_csv("history.csv")
    st.dataframe(df_history.sort_index(ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("Historie je prázdná.")
st.markdown('</div>', unsafe_allow_html=True)
