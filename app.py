import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YouTube to MP3 Downloader", page_icon="🎵")

st.title("🎵 YouTube to MP3")
url = st.text_input("Vložte odkaz na YouTube video:")

if st.button("Převést na MP3"):
    if url:
        with st.spinner('Pracuji na tom... (stahuji a převádím)'):
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    mp3_filename = os.path.splitext(filename)[0] + ".mp3"

                # Nabídnutí souboru ke stažení v prohlížeči
                with open(mp3_filename, "rb") as f:
                    st.download_button(
                        label="Klikněte zde pro uložení MP3",
                        data=f,
                        file_name=mp3_filename,
                        mime="audio/mpeg"
                    )
                st.success(f"Hotovo! Soubor '{mp3_filename}' je připraven.")
                
                # Úklid: smazání souboru ze serveru po stažení
                os.remove(mp3_filename)

            except Exception as e:
                st.error(f"Něco se nepovedlo: {e}")
    else:
        st.warning("Prosím, vložte odkaz.")
