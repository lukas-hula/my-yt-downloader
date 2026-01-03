import streamlit as st
import requests
import librosa
import numpy as np
import os
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="AudioFlow Pro", page_icon="🎵", layout="centered")

# --- DESIGN (Zůstává stejný) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .block-container { padding-top: 2rem !important; }
    header {visibility: hidden;}
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .main-card { text-align: center; max-width: 600px; margin: 0 auto; }
    .title-text { font-weight: 800; font-size: 2.8rem; letter-spacing: -0.05em; color: #1d1d1f; margin-bottom: 0px; }
    .subtitle-text { color: #86868b; font-size: 1.1rem; margin-bottom: 30px; }
    .analysis-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.95rem; border-radius: 15px; overflow: hidden; background-color: #f5f5f7; }
    .analysis-table td { padding: 15px 20px; border-bottom: 1px solid #e5e5e7; text-align: left; color: #1d1d1f; }
    .stTextInput input { border-radius: 12px !important; background-color: #f5f5f7 !important; border: 1px solid #d2d2d7 !important; padding: 12px !important; }
    .stButton button { background-color: #1d1d1f !important; color: white !important; border-radius: 20px !important; width: 100% !important; font-weight: 600 !important; }
    
    .stDownloadButton button {
        background-color: #0071e3 !important; color: white !important;
        border-radius: 12px !important; padding: 15px !important;
        font-weight: 600 !important; width: 100% !important; border: none !important;
    }
    .stDownloadButton button:hover { background-color: #0077ed !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCE: ZÍSKÁNÍ ODKAZU PŘES COBALT ---
def get_stream_url(video_url):
    # Použijeme veřejnou instanci Cobalt API
    api_url = "https://api.cobalt.tools/api/json"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    payload = {
        "url": video_url,
        "isAudioOnly": True,
        "aFormat": "mp3"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        
        if "url" in data:
            return data["url"]
        else:
            return None
    except:
        return None

# --- HLAVNÍ PROCES ---
def process_audio(direct_url):
    filename = "downloaded_song.mp3"
    try:
        # 1. Stažení souboru z Cobaltu
        # Tady už blokace nehrozí, protože stahujeme z jejich CDN, ne z YouTube
        with requests.get(direct_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
        
        # Ověření velikosti
        if os.path.getsize(filename) < 50000:
            return None, "Chyba: Stažený soubor je prázdný."

        # 2. Analýza (Librosa)
        y, sr = librosa.load(filename, duration=60)
        
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[np.argmax(np.mean(chroma, axis=1))]
        
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Zjistíme délku ze souboru
        duration = librosa.get_duration(y=y, sr=sr)
        
        stats = {
            "key": key,
            "tempo": f"{int(round(float(tempo)))} BPM",
            "duration": "Analýza vzorku hotova"
        }
        return stats, None

    except Exception as e:
        return None, str(e)
    finally:
        # Soubor nemažeme hned, aby si ho uživatel mohl stáhnout
        pass

# --- UI LOGIKA ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Bypass Edition</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
process_btn = st.button("Zpracovat skladbu")

if process_btn and url_input:
    # Úklid předchozích souborů
    if os.path.exists("downloaded_song.mp3"):
        os.remove("downloaded_song.mp3")

    if "youtu" in url_input:
        with st.spinner("🔄 Připojuji se k externímu serveru..."):
            # 1. Získání odkazu
            stream_url = get_stream_url(url_input)
            
            if stream_url:
                # 2. Stažení a analýza
                stats, error = process_audio(stream_url)
                
                if error:
                    st.error(f"Chyba při analýze: {error}")
                else:
                    st.balloons()
                    
                    st.markdown(f"""
                        <table class="analysis-table">
                            <tr><td style="color:#86868b; font-weight:600;">Odkaz</td><td>Úspěšně zpracován</td></tr>
                            <tr><td style="color:#86868b; font-weight:600;">Tónina</td><td><b>{stats['key']}</b></td></tr>
                            <tr><td style="color:#86868b; font-weight:600;">Tempo</td><td>{stats['tempo']}</td></tr>
                        </table>
                    """, unsafe_allow_html=True)
                    
                    # Tlačítko pro stažení
                    if os.path.exists("downloaded_song.mp3"):
                        with open("downloaded_song.mp3", "rb") as file:
                            st.download_button(
                                label="💾 ULOŽIT MP3 DO POČÍTAČE",
                                data=file,
                                file_name="audioflow_track.mp3",
                                mime="audio/mpeg"
                            )
            else:
                st.error("Nepodařilo se získat stream. Zkuste to za chvíli nebo s jiným videem.")
    else:
        st.warning("Vložte platný odkaz.")

st.markdown('</div>', unsafe_allow_html=True)
