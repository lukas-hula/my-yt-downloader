import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime
import os

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
    .stTextInput input { border-radius: 12px !important; background-color: #f5f5f7 !important; border: 1px solid #d2d2d7 !important; }
    .stButton button { background-color: #1d1d1f !important; color: white !important; border-radius: 25px !important; width: 100% !important; border: none !important; }
    .download-link { display: block; background-color: #0071e3; color: white !important; padding: 18px; border-radius: 15px; text-decoration: none; font-weight: 700; margin-top: 10px; text-align: center; }
    
    /* Styl pro nadpis historie */
    .history-title { margin-top: 50px; font-weight: 800; font-size: 1.8rem; color: #1d1d1f; text-align: left; border-bottom: 2px solid #f5f5f7; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCE PRO LOGOVÁNÍ ---
def log_to_csv(title, video_id, duration_str):
    log_file = "history.csv"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    new_data = pd.DataFrame([{
        "Čas": timestamp,
        "Skladba": title,
        "ID Videa": video_id,
        "Délka": duration_str
    }])

    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(log_file, mode='a', index=False, header=False, encoding='utf-8-sig')

# --- HLAVNÍ STRÁNKA (PŘEVODNÍK) ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Profesionální převodník s evidencí</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("PŘIPRAVIT MP3")

if submit_btn and url_input:
    video_id = ""
    if "v=" in url_input: video_id = url_input.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_input: video_id = url_input.split("youtu.be/")[1].split("?")[0]
    else: video_id = url_input.split("/")[-1].split("?")[0]

    if video_id:
        try:
            RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
            headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"}
            params = {"id": video_id}
            
            with st.spinner("Zpracovávám..."):
                response = requests.get("https://youtube-mp36.p.rapidapi.com/dl", headers=headers, params=params)
                data = response.json()

                if data.get("status") == "ok":
                    minutes, seconds = int(data.get('duration') // 60), int(data.get('duration') % 60)
                    duration_str = f"{minutes}m {seconds:02d}s"
                    
                    # ZÁPIS DO CSV
                    log_to_csv(data.get('title'), video_id, duration_str)
                    
                    st.balloons()
                    st.markdown(f"""
                        <table class="analysis-table">
                            <tr><td class="label-col">Název</td><td>{data.get('title')}</td></tr>
                            <tr><td class="label-col">Délka</td><td>{duration_str}</td></tr>
                        </table>
                        <a href="{data.get('link')}" target="_blank" class="download-link">💾 STÁHNOUT SOUBOR</a>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Chyba při generování. Zkuste to znovu.")
        except Exception as e:
            st.error(f"Chyba: {e}")
    else:
        st.warning("Vložte platný odkaz.")

# --- SEKCE HISTORIE (PŘÍMO VIDITELNÁ) ---
st.markdown('<div class="history-title">Historie stažení</div>', unsafe_allow_html=True)

if os.path.isfile("history.csv"):
    df_history = pd.read_csv("history.csv")
    
    # Zobrazení tabulky (nejnovější záznamy nahoře)
    st.dataframe(
        df_history.sort_index(ascending=False), 
        use_container_width=True,
        hide_index=True
    )
    
    # Tlačítko pro export do CSV
    csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Stáhnout celou historii jako CSV",
        data=csv_data,
        file_name=f"audioflow_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("Zatím nebyla stažena žádná skladba. Historie se objeví po prvním převodu.")

st.markdown('</div>', unsafe_allow_html=True)
