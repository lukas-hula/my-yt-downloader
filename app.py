import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="AudioFlow Premium",
    page_icon="🎵",
    layout="centered"
)

# --- MODERNÍ DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Hlavní pozadí s gradientem */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Glassmorphism karta */
    .main-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px;
        border-radius: 28px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        margin-top: 20px;
    }

    /* Elegantní nadpis */
    .title-text {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0px;
    }

    .subtitle-text {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Vstupní pole */
    .stTextInput input {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
    }

    /* Hlavní tlačítko */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3.5em;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        border: none;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        margin-top: 10px;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
        border: none;
        color: white;
    }

    /* Tlačítko pro stažení (Zelené) */
    .download-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background: linear-gradient(90deg, #10b981, #059669);
        color: white !important;
        padding: 15px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 700;
        box-shadow: 0 10px 15px rgba(16, 185, 129, 0.2);
        margin-top: 20px;
        transition: 0.3s;
    }
    
    .download-btn:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 20px rgba(16, 185, 129, 0.3);
    }

    /* Patička */
    .footer {
        text-align: center;
        color: #475569;
        margin-top: 50px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- OBSAH STRÁNKY ---
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Elegantní převodník z YouTube do vysoké kvality MP3</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    url_input = st.text_input("", placeholder="Vložte odkaz (např. https://youtu.be/...)")
    submit_btn = st.button("GENEROVAT MP3")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIKA ---
if submit_btn and url_input:
    # 1. Extrakce ID videa
    video_id = ""
    if "youtu.be/" in url_input:
        video_id = url_input.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url_input:
        video_id = url_input.split("v=")[1].split("&")[0]
    
    if video_id:
        # Tady vložte svůj API klíč
        RAPIDAPI_KEY = "68011bf4f8msh2befeaf67d8207cp1fc142jsndcb8d16ee5f8" 
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
        }
        params = {"id": video_id}
        api_url = "https://youtube-mp36.p.rapidapi.com/dl"

        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        try:
            attempts = 0
            while attempts < 10:
                progress_val = min((attempts + 1) * 10, 95)
                progress_bar.progress(progress_val)
                
                response = requests.get(api_url, headers=headers, params=params)
                data = response.json()

                if data.get("status") == "ok":
                    progress_bar.progress(100)
                    status_placeholder.empty()
                    st.balloons()
                    
                    # Úspěšná karta výsledku
                    st.markdown(f"""
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; padding: 20px; border-radius: 15px; margin-top: 20px;">
                            <p style="margin:0; color:#10b981; font-weight:700;">✨ Skladba je připravena!</p>
                            <p style="margin:5px 0 0 0; color:white; opacity:0.8; font-size:0.9rem;">{data.get('title')}</p>
                        </div>
                        <a href="{data.get('link')}" target="_blank" class="download-btn">
                            💾 STÁHNOUT MP3 SOUBOR
                        </a>
                    """, unsafe_allow_html=True)
                    break
                
                elif data.get("status") == "processing":
                    status_placeholder.info(f"⏳ Server pracuje na převodu... (pokus {attempts + 1}/10)")
                    time.sleep(3)
                    attempts += 1
                else:
                    st.error("Chyba: API server neodpovídá správně. Zkuste to za chvíli.")
                    break
            
            if attempts == 10:
                st.warning("Zpracování trvá příliš dlouho. Zkuste kliknout na tlačítko znovu za okamžik.")

        except Exception as e:
            st.error(f"⚠️ Došlo k neočekávané chybě: {e}")
    else:
        st.warning("Uups! Tento odkaz nevypadá jako platný YouTube link.")

st.markdown('<div class="footer">Premium API Edition • 2026</div>', unsafe_allow_html=True)
