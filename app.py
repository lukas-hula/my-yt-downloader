import streamlit as st
import requests
import time
import librosa
import numpy as np
import os

# --- KONFIGURACE A DESIGN ---
st.set_page_config(page_title="AudioFlow", page_icon="🎵", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .block-container { padding-top: 2rem !important; }
    header {visibility: hidden;}
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .main-card { text-align: center; max-width: 550px; margin: 0 auto; }
    .title-text { font-weight: 800; font-size: 2.8rem; letter-spacing: -0.05em; color: #1d1d1f; margin-bottom: 0px; }
    .subtitle-text { color: #86868b; font-size: 1.1rem; margin-bottom: 30px; }
    .analysis-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.95rem; border-radius: 15px; overflow: hidden; background-color: #f5f5f7; }
    .analysis-table td { padding: 15px 20px; border-bottom: 1px solid #e5e5e7; text-align: left; color: #1d1d1f; }
    .stTextInput input { border-radius: 12px !important; background-color: #f5f5f7 !important; border: 1px solid #d2d2d7 !important; padding: 12px !important; }
    .stButton button { background-color: #1d1d1f !important; color: white !important; border-radius: 20px !important; width: 100% !important; }
    .download-btn { display: block; background-color: #0071e3; color: white !important; padding: 15px; border-radius: 12px; text-decoration: none; font-weight: 600; margin-top: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FINÁLNÍ ANALYTICKÁ FUNKCE ---
def analyze_music(url):
    temp_file = "full_track.mp3"
    try:
        # 1. Stažení CELÉHO souboru (oprava chyby "Could not seek")
        # Přidáme hlavičky, aby nás server neodmítl
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True)
        
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024): # 1MB chunky
                f.write(chunk)
                
        # 2. Načtení přímo do Librosa
        # Díky packages.txt s ffmpegem toto nyní bude fungovat
        # Načteme jen 30 sekund pro rychlou analýzu, ale ze zdravého souboru
        y, sr = librosa.load(temp_file, duration=30)
        
        # 3. Analýza tóniny
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[np.argmax(np.mean(chroma, axis=1))]
        
        # 4. Analýza tempa
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        return str(key), f"{int(round(float(tempo)))} BPM"

    except Exception as e:
        return "Chyba", str(e) # Vypíše chybu, kdyby něco
    
    finally:
        # Úklid
        if os.path.exists(temp_file):
            os.remove(temp_file)

# --- UI LOGIKA ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Profesionální analýza hudby</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("Analyzovat a převést")

if submit_btn and url_input:
    video_id = url_input.split("v=")[-1] if "v=" in url_input else url_input.split("/")[-1].split("?")[0]
    
    if video_id:
        try:
            RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
            headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"}
            api_url = "https://youtube-mp36.p.rapidapi.com/dl"
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(1, 15):
                progress_bar.progress(min(i * 7, 90))
                status_text.text("Zpracovávám audio na serveru...")
                response = requests.get(api_url, headers=headers, params={"id": video_id})
                data = response.json()
                
                if data.get("status") == "ok":
                    status_text.text("Stahuji a analyzuji (to může chvilku trvat)...")
                    tonina, tempo = analyze_music(data.get("link"))
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    st.balloons()
                    
                    st.markdown(f"""
                        <table class="analysis-table">
                            <tr><td style="color:#86868b; font-weight:600;">Skladba</td><td>{data.get('title')}</td></tr>
                            <tr><td style="color:#86868b; font-weight:600;">Tónina</td><td><b>{tonina}</b></td></tr>
                            <tr><td style="color:#86868b; font-weight:600;">Tempo</td><td>{tempo}</td></tr>
                            <tr><td style="color:#86868b; font-weight:600;">Délka</td><td>{int(data.get('duration') // 60)}m {int(data.get('duration') % 60)}s</td></tr>
                        </table>
                        <a href="{data.get('link')}" target="_blank" class="download-btn">STÁHNOUT MP3</a>
                    """, unsafe_allow_html=True)
                    break
                time.sleep(3)
        except Exception as e:
            st.error(f"Kritická chyba: {e}")
    else:
        st.warning("Neplatný odkaz.")

st.markdown('</div>', unsafe_allow_html=True)
