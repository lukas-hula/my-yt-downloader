import streamlit as st
import yt_dlp
import os
import base64

# Konfigurace stránky
st.set_page_config(
    page_title="AudioFlow | YT to MP3",
    page_icon="🎵",
    layout="centered"
)

# Vlastní CSS pro "vzdušný" a elegantní vzhled
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        border: none;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff1a1a;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input {
        border-radius: 15px;
    }
    .main-card {
        padding: 40px;
        background: white;
        border-radius: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    h1 {
        color: #1e1e1e;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-align: center;
        font-weight: 800;
    }
    .subtitle {
        text-align: center;
        color: #6c757d;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Hlavička aplikace
st.markdown("<h1>🎵 AudioFlow</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Stáhněte si své oblíbené skladby v nejvyšší kvalitě</p>", unsafe_allow_html=True)

# Hlavní kontejner (karta)
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    url = st.text_input("", placeholder="Vložte YouTube odkaz zde (např. https://youtube.com/...)")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("Převést na MP3")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Logika zpracování
if submit_button:
    if url:
        # Progress bar pro vizuální efekt
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Připojuji se k YouTube...")
            progress_bar.progress(20)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status_text.text("Stahuji a převádím audio...")
                progress_bar.progress(60)
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                mp3_filename = os.path.splitext(filename)[0] + ".mp3"

            progress_bar.progress(100)
            status_text.empty()
            
            # Úspěšná zpráva s tlačítkem pro stažení
            st.balloons()
            st.success(f"✨ **{info['title']}** je připravena!")
            
            with open(mp3_filename, "rb") as f:
                st.download_button(
                    label="💾 STÁHNOUT SOUBOR",
                    data=f,
                    file_name=mp3_filename,
                    mime="audio/mpeg",
                    use_container_width=True
                )
            
            # Úklid
            os.remove(mp3_filename)

        except Exception as e:
            st.error(f"⚠️ Omlouváme se, došlo k chybě: {str(e)}")
            progress_bar.empty()
    else:
        st.warning("Před kliknutím vložte prosím odkaz.")

# Patička
st.markdown("<br><hr><p style='text-align: center; color: #ced4da;'>Vytvořeno pomocí AI & Streamlit</p>", unsafe_allow_html=True)
