import streamlit as st
import requests
import time
import librosa
import numpy as np
import os
from pydub import AudioSegment

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

# --- ANALÝZA S PŘEVODEM NA WAV ---
def analyze_music(url):
    temp_mp3 = "temp_audio.mp3"
    temp_wav = "temp_audio.wav"
    try:
        # 1. Stažení MP3 (prvních 5MB pro jistotu)
        response = requests.get(url, stream=True, timeout=20)
        with open(temp_mp3, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                if os.path.getsize(temp_mp3) > 5000000: break 
        
        # 2. Konverze MP3 -> WAV pomocí pydub (vyžaduje ffmpeg)
        # Toto je klíčový krok pro stabilitu
        audio = AudioSegment.from_mp3(temp_mp3)
        # Ořízneme na 30 sekund pro rychlejší analýzu
        audio = audio[:30000] 
        audio.export(temp_wav, format="wav")
        
        # 3. Načtení WAV do Librosa
        y, sr = librosa.load(temp_wav)
        
        # 4. Výpočet
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[np.argmax(np.mean(chroma, axis=1))]
        
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        return str(key), f"{int(round(float(tempo)))} BPM"

    except Exception as e:
        # Vypíšeme celou chybu pro debug
        return "Chyba", str(e)
    
    finally:
        # Úklid
        if os.path.exists(temp_mp3): os.remove(temp_mp3)
        if os.path.exists(temp_wav): os.remove(temp_wav)

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
                status_text.text("Připravuji soubor na serveru...")
                response = requests.get(api_url, headers=headers, params={"id": video_id})
                data = response.json()
                
                if data.get("status") == "ok":
                    status_text.text("Konvertuji a analyzuji (FFmpeg)...")
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
