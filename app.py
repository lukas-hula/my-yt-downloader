import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="AudioFlow | Aurora Edition",
    page_icon="⚡",
    layout="centered"
)

# --- AURORA UI DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Celkové pozadí a font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    .stApp {
        background-color: #050505;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Aurora Glow efekty na pozadí */
    .stApp::before {
        content: "";
        position: fixed;
        top: -10%;
        left: -10%;
        width: 40%;
        height: 40%;
        background: radial-gradient(circle, rgba(0, 255, 242, 0.15) 0%, rgba(0, 0, 0, 0) 70%);
        z-index: -1;
    }
    
    .stApp::after {
        content: "";
        position: fixed;
        bottom: -10%;
        right: -10%;
        width: 50%;
        height: 50%;
        background: radial-gradient(circle, rgba(174, 255, 0, 0.1) 0%, rgba(0, 0, 0, 0) 70%);
        z-index: -1;
    }

    /* Minimalistická karta */
    .main-card {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 50px;
        border-radius: 40px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        text-align: center;
    }

    /* Futuristický nadpis */
    .title-text {
        color: #ffffff;
        font-weight: 800;
        font-size: 3.5rem;
        letter-spacing: -2px;
        margin-bottom: 0px;
        text-shadow: 0 0 20px rgba(255,255,255,0.2);
    }

    .subtitle-text {
        color: #666;
        font-size: 1rem;
        margin-bottom: 40px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Input pole */
    .stTextInput input {
        background: #111 !important;
        border: 2px solid #222 !important;
        color: #00fff2 !important;
        border-radius: 20px !important;
        padding: 15px 25px !important;
        transition: 0.3s;
    }
    
    .stTextInput input:focus {
        border-color: #00fff2 !important;
        box-shadow: 0 0 15px rgba(0, 255, 242, 0.2) !important;
    }

    /* Tlačítka */
    .stButton>button {
        background: #ffffff;
        color: #000000;
        border-radius: 20px;
        height: 4em;
        font-weight: 800;
        border: none;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .stButton>button:hover {
        background: #00fff2;
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 255, 242, 0.4);
    }

    /* Download Button */
    .download-btn {
        display: block;
        background: transparent;
        border: 2px solid #aeff00;
        color: #aeff00 !important;
        padding: 20px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 800;
        margin-top: 30px;
        transition: 0.3s;
        text-transform: uppercase;
    }

    .download-btn:hover {
        background: #aeff00;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(174, 255, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LAYOUT ---
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Next-Gen Audio Extraction</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    url_input = st.text_input("", placeholder="Vložte YouTube URL...")
    submit_btn = st.button("EXTRAKCE AUDIA")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIKA ---
if submit_btn and url_input:
    video_id = ""
    if "youtu.be/" in url_input:
        video_id = url_input.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url_input:
        video_id = url_input.split("v=")[1].split("&")[0]
    
    if video_id:
        # !!! SEM VLOŽTE SVŮJ KLÍČ !!!
        RAPIDAPI_KEY = "68011bf4f8msh2befeaf67d8207cp1fc142jsndcb8d16ee5f8" 
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
        }
        params = {"id": video_id}
        api_url = "https://youtube-mp36.p.rapidapi.com/dl"

        status_msg = st.empty()
        
        try:
            attempts = 0
            while attempts < 10:
                response = requests.get(api_url, headers=headers, params=params)
                data = response.json()

                if data.get("status") == "ok":
                    status_msg.empty()
                    st.success(f"⚡ PŘIPRAVENO: {data.get('title')}")
                    
                    st.markdown(f"""
                        <a href="{data.get('link')}" target="_blank" class="download-btn">
                            ↓ STÁHNOUT MP3
                        </a>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    break
                
                elif data.get("status") == "processing":
                    status_msg.warning(f"🚧 Zpracování na serveru... ({attempts + 1}/10)")
                    time.sleep(3)
                    attempts += 1
                else:
                    st.error("API Error. Zkuste to znovu.")
                    break
        except Exception as e:
            st.error(f"Chyba: {e}")
    else:
        st.info("Zadejte prosím odkaz.")

st.markdown("<p style='text-align:center; color:#333; margin-top:50px;'>2026 // AURORA TERMINAL</p>", unsafe_allow_html=True)
