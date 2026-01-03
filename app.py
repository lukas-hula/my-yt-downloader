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

# --- ANALÝZA HUDBY ---
def analyze_music(url):
    filename = "downloaded_track.mp3"
    try:
        # 1. Stažení souboru (BEZ User-Agent hlaviček, které blokovaly stahování)
        response = requests.get(url, stream=True)
        
        # Kontrola, zda server souhlasí (200 OK)
        if response.status_code != 200:
            return "Chyba serveru", f"Kód {response.status_code}"

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
        
        # Kontrola velikosti (zda není soubor prázdný)
        file_size = os.path.getsize(filename)
        if file_size < 50000: # Méně než 50kB je podezřelé
            return "Chyba souboru", f"Staženo jen {file_size} bytů"

        # 2. Analýza pomocí Librosa (načítáme 60s pro jistotu)
        # Nyní by to mělo projít, protože soubor bude kompletní
        y, sr = librosa.load(filename, duration=60)
        
        # Tónina
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[np.argmax(np.mean(chroma, axis=1))]
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        return str(key), f"{int(round(float(tempo)))} BPM"

    except Exception as e:
        return "Chyba analýzy", str(e)[:30] # Vypíše kousek chyby
    
    finally:
        # Úklid
        if os.path.exists(filename):
            os.remove(filename)

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
            
            for i in range(1, 11):
                progress_bar.progress(i * 9)
                status_text.text("Komunikuji se serverem...")
                response = requests.get(api_url, headers=headers, params={"id": video_id})
                data = response.json()
                
                if data.get("status") == "ok":
                    status_text.text("Stahuji a analyzuji...")
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
                time.sleep(2)
        except Exception as e:
            st.error(f"Chyba: {e}")
    else:
        st.warning("Neplatný odkaz.")

st.markdown('</div>', unsafe_allow_html=True)
