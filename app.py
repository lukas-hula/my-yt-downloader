import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="AudioFlow | Clean Edition",
    page_icon="🎵",
    layout="centered"
)

# --- MINIMALISTICKÝ DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Import elegantního fontu */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
        color: #1d1d1f;
    }

    /* Vycentrování celého obsahu */
    .main {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Hlavní kontejner bez stínů, jen s jemnou linkou */
    .main-card {
        text-align: center;
        padding: 60px 20px;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Nadpis v Apple stylu */
    .title-text {
        font-weight: 800;
        font-size: 3.2rem;
        letter-spacing: -0.05em;
        color: #1d1d1f;
        margin-bottom: 10px;
    }

    .subtitle-text {
        font-weight: 400;
        color: #86868b;
        font-size: 1.2rem;
        margin-bottom: 50px;
    }

    /* Stylování inputu */
    .stTextInput div div input {
        background-color: #f5f5f7 !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        color: #1d1d1f !important;
        font-size: 1rem !important;
        transition: all 0.2s ease-in-out;
    }

    .stTextInput div div input:focus {
        border-color: #0071e3 !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1) !important;
    }

    /* Hlavní černé tlačítko */
    .stButton button {
        background-color: #1d1d1f !important;
        color: #ffffff !important;
        border-radius: 25px !important;
        padding: 12px 35px !important;
        font-weight: 600 !important;
        border: none !important;
        width: auto !important;
        min-width: 200px;
        transition: all 0.2s ease;
        margin-top: 20px;
    }

    .stButton button:hover {
        background-color: #000000 !important;
        transform: scale(1.02);
    }

    /* Tlačítko pro stažení - modré (jako iOS) */
    .download-btn {
        display: inline-block;
        background-color: #0071e3;
        color: #ffffff !important;
        padding: 16px 40px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 40px;
        transition: background 0.2s ease;
    }

    .download-btn:hover {
        background-color: #0077ed;
        box-shadow: 0 8px 20px rgba(0, 113, 227, 0.2);
    }

    /* Info hlášky */
    .stAlert {
        border-radius: 15px !important;
        background-color: #f5f5f7 !important;
        border: none !important;
        color: #1d1d1f !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- STRUKTURA STRÁNKY ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Simple. Powerful. Pure Audio.</p>', unsafe_allow_html=True)

# Vstupní pole a tlačítko (vše uvnitř vycentrovaného kontejneru)
url_input = st.text_input("", placeholder="Vložte YouTube link...")
submit_btn = st.button("Convert to MP3")

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

        status_container = st.empty()
        
        try:
            attempts = 0
            while attempts < 10:
                response = requests.get(api_url, headers=headers, params=params)
                data = response.json()

                if data.get("status") == "ok":
                    status_container.empty()
                    st.markdown(f"""
                        <div style="margin-top: 30px;">
                            <p style="color: #86868b; margin-bottom: 10px;">{data.get('title')}</p>
                            <a href="{data.get('link')}" target="_blank" class="download-btn">
                                Download MP3
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    break
                
                elif data.get("status") == "processing":
                    status_container.text("Processing your request...")
                    time.sleep(3)
                    attempts += 1
                else:
                    st.error("Something went wrong. Please try again.")
                    break
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid URL.")

st.markdown('</div>', unsafe_allow_html=True)

# Patička
st.markdown("""
    <div style="position: fixed; bottom: 20px; left: 0; right: 0; text-align: center; color: #d2d2d7; font-size: 0.8rem;">
        Minimalist Audio Extractor &copy; 2026
    </div>
""", unsafe_allow_html=True)
