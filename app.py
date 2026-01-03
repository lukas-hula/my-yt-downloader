import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="AudioFlow",
    page_icon="🎵",
    layout="centered"
)

# --- ČISTÝ DESIGN (OPRAVA MEZER) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Odstranění prázdného místa nahoře */
    .block-container {
        padding-top: 2rem !important;
    }
    header {visibility: hidden;}
    
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    .main-card {
        text-align: center;
        max-width: 500px;
        margin: 0 auto;
    }

    .title-text {
        font-weight: 800;
        font-size: 2.8rem;
        letter-spacing: -0.05em;
        color: #1d1d1f;
        margin-bottom: 0px;
    }

    .subtitle-text {
        color: #86868b;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Elegantní input a tlačítko */
    .stTextInput input {
        border-radius: 12px !important;
        background-color: #f5f5f7 !important;
        border: 1px solid #d2d2d7 !important;
    }

    .stButton button {
        background-color: #1d1d1f !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 10px 40px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    
    .download-btn {
        display: block;
        background-color: #0071e3;
        color: white !important;
        padding: 15px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Čistý převod na MP3</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("Převést na MP3")

if submit_btn and url_input:
    # Extrakce ID videa
    video_id = url_input.split("v=")[-1] if "v=" in url_input else url_input.split("/")[-1].split("?")[0]
    
    if video_id:
        try:
            # Načtení klíče z konfigurace (Streamlit Secrets)
            RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
            
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
            }
            params = {"id": video_id}
            api_url = "https://youtube-mp36.p.rapidapi.com/dl"

            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(1, 11):
                progress_bar.progress(i * 10)
                status_text.text("Připravuji audio soubor...")
                
                response = requests.get(api_url, headers=headers, params=params)
                data = response.json()

                if data.get("status") == "ok":
                    progress_bar.empty()
                    status_text.empty()
                    st.balloons()
                    st.success(f"Skladba '{data.get('title')}' je připravena")
                    st.markdown(f'<a href="{data.get("link")}" target="_blank" class="download-btn">STÁHNOUT MP3</a>', unsafe_allow_html=True)
                    break
                
                time.sleep(3) # Čekání na zpracování
        except Exception as e:
            st.error("Chyba v konfiguraci nebo spojení.")
    else:
        st.warning("Neplatný odkaz.")

st.markdown('</div>', unsafe_allow_html=True)
