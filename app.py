import streamlit as st
import requests
import time

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="AudioFlow", page_icon="🎵", layout="centered")

# --- DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .block-container { padding-top: 2rem !important; }
    header {visibility: hidden;}
    
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    .main-card {
        text-align: center;
        max-width: 550px;
        margin: 0 auto;
    }

    .title-text {
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -0.05em;
        color: #1d1d1f;
        margin-bottom: 5px;
    }

    .subtitle-text {
        color: #86868b;
        font-size: 1.1rem;
        margin-bottom: 40px;
    }

    /* Tabulka údajů */
    .analysis-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 0.95rem;
        border-radius: 15px;
        overflow: hidden;
        background-color: #f5f5f7;
    }
    
    .analysis-table td {
        padding: 15px 20px;
        border-bottom: 1px solid #e5e5e7;
        text-align: left;
        color: #1d1d1f;
    }

    .label-col {
        color: #86868b !important;
        font-weight: 600;
        width: 40%;
    }

    /* Vstupní pole */
    .stTextInput input {
        border-radius: 12px !important;
        background-color: #f5f5f7 !important;
        border: 1px solid #d2d2d7 !important;
        padding: 12px 20px !important;
    }

    /* Černé tlačítko */
    .stButton button {
        background-color: #1d1d1f !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 10px 40px !important;
        font-weight: 600 !important;
        width: 100% !important;
        border: none !important;
    }

    /* Modré tlačítko ke stažení */
    .download-link {
        display: block;
        background-color: #0071e3;
        color: white !important;
        padding: 18px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 700;
        margin-top: 10px;
        font-size: 1.1rem;
        transition: 0.3s;
        text-align: center;
    }

    .download-link:hover {
        background-color: #0077ed;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HLAVNÍ UI ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">AudioFlow</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Profesionální převodník skladeb</p>', unsafe_allow_html=True)

url_input = st.text_input("", placeholder="Vložte YouTube odkaz...")
submit_btn = st.button("PŘIPRAVIT MP3")

if submit_btn and url_input:
    # Extrakce ID videa
    video_id = ""
    if "v=" in url_input:
        video_id = url_input.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url_input:
        video_id = url_input.split("youtu.be/")[1].split("?")[0]
    else:
        video_id = url_input.split("/")[-1].split("?")[0]

    if video_id:
        try:
            RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
            headers = {
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
            }
            params = {"id": video_id}
            api_url = "https://youtube-mp36.p.rapidapi.com/dl"

            status_placeholder = st.empty()
            progress_bar = st.progress(0)

            success = False
            # Polling pro získání dat
            for i in range(1, 15):
                progress_bar.progress(i * 7 if i < 14 else 99)
                status_placeholder.text("Vyhledávám informace o skladbě...")
                
                response = requests.get(api_url, headers=headers, params=params)
                data = response.json()

                if data.get("status") == "ok":
                    progress_bar.progress(100)
                    status_placeholder.empty()
                    st.balloons()
                    
                    # Výpočet délky v minutách a sekundách
                    raw_sec = data.get('duration', 0)
                    minutes = int(raw_sec // 60)
                    seconds = int(raw_sec % 60)
                    
                    # Zobrazení TABULKY s údaji
                    st.markdown(f"""
                        <table class="analysis-table">
                            <tr>
                                <td class="label-col">Název skladby</td>
                                <td>{data.get('title')}</td>
                            </tr>
                            <tr>
                                <td class="label-col">Délka</td>
                                <td>{minutes}m {seconds:02d}s</td>
                            </tr>
                            <tr>
                                <td class="label-col">Kvalita</td>
                                <td>320kbps (HQ)</td>
                            </tr>
                            <tr>
                                <td class="label-col">Formát</td>
                                <td>MP3 Audio</td>
                            </tr>
                        </table>
                        
                        <a href="{data.get('link')}" target="_blank" class="download-link">
                            💾 STÁHNOUT SOUBOR
                        </a>
                        <p style="color: #86868b; font-size: 0.8rem; margin-top: 10px;">
                            Kliknutím na tlačítko se otevře přímý odkaz na soubor.
                        </p>
                    """, unsafe_allow_html=True)
                    
                    success = True
                    break
                
                elif data.get("status") == "processing":
                    time.sleep(2)
                else:
                    st.error("Nepodařilo se získat data z YouTube. Zkuste jiný odkaz.")
                    break
            
            if not success and i == 14:
                st.warning("Serveru to trvá trochu déle. Zkuste to prosím za moment.")

        except Exception as e:
            st.error(f"Chyba při komunikaci s API: {e}")
    else:
        st.warning("Neplatný odkaz. Vložte prosím URL adresu videa.")

st.markdown('</div>', unsafe_allow_html=True)
