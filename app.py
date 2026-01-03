import streamlit as st
import yt_dlp
import librosa
import numpy as np
import os
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="AudioFlow Pro", page_icon="🎵", layout="centered")

# --- DESIGN ---
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
    
    /* Vlastní styl pro stahovací tlačítko Streamlitu */
    .stDownloadButton button {
        background-color: #0071e3 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: 600 !important;
        width: 100% !important;
        border: none !important;
    }
    .stDownloadButton button:hover {
        background-color: #0077ed !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HLAVNÍ FUNKCE ---
def process_video(url):
    output_filename = "song.mp3"
    
    # 1. Nastavení yt-dlp pro stažení MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song',  # Jméno bez přípony
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }

    try:
        # Stažení
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Neznámá skladba')
            duration = info.get('duration', 0)
        
        # Ověření, že soubor existuje (yt-dlp automaticky přidá .mp3)
        if not os.path.exists(output_filename):
            return None, "Chyba při konverzi souboru."

        # 2. Hudební analýza (Librosa)
        y, sr = librosa.load(output_filename, duration=60)
        
        # Tónina
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[np.argmax(np.mean(chroma, axis=1))]
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo_val = int(round(float(tempo)))

        # Data pro tabulku
        stats = {
            "title": title,
            "key": key,
            "tempo": f"{tempo_val} BPM",
            "duration": f"{int(duration // 60)}m {int(duration % 60)}s"
        }
        
        return stats, None

    except Exception as e:
        return None, str(e)

# --- UI LOGIKA ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Profesionální extrakce a analýza</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
process_btn = st.button("Zpracovat skladbu")

if process_btn and url_input:
    if "youtu" in url_input:
        with st.spinner("⏳ Stahuji audio a provádím analýzu..."):
            # Smazání starého souboru před novým pokusem
            if os.path.exists("song.mp3"):
                os.remove("song.mp3")
                
            stats, error = process_video(url_input)
            
            if error:
                st.error(f"Chyba: {error}")
            else:
                st.balloons()
                
                # Tabulka výsledků
                st.markdown(f"""
                    <table class="analysis-table">
                        <tr><td style="color:#86868b; font-weight:600;">Skladba</td><td>{stats['title']}</td></tr>
                        <tr><td style="color:#86868b; font-weight:600;">Tónina</td><td><b>{stats['key']}</b></td></tr>
                        <tr><td style="color:#86868b; font-weight:600;">Tempo</td><td>{stats['tempo']}</td></tr>
                        <tr><td style="color:#86868b; font-weight:600;">Délka</td><td>{stats['duration']}</td></tr>
                    </table>
                """, unsafe_allow_html=True)
                
                # Přímé tlačítko pro stažení souboru ze serveru k uživateli
                with open("song.mp3", "rb") as file:
                    st.download_button(
                        label="💾 ULOŽIT MP3 DO POČÍTAČE",
                        data=file,
                        file_name=f"{stats['title']}.mp3",
                        mime="audio/mpeg"
                    )
    else:
        st.warning("Prosím vložte platný odkaz na YouTube.")

st.markdown('</div>', unsafe_allow_html=True)
