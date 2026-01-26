import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image
import time
from streamlit_mic_recorder import mic_recorder, speech_to_text

# --- 🪄 SADECE ALT YAZIYI VE MENÜYÜ GİZLE (SİDEBAR KALSIN) ---
st.markdown("""
    <style>
    /* Diğer uygulamaları gösteren menüyü gizle */
    #MainMenu {visibility: hidden;} 
    
    /* En alttaki Created by Streamlit yazısını siler */
    footer {visibility: hidden;}
    
    /* Sayfanın altındaki boşluğu sıfırlar */
    .stAppDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* Sidebar (Yan menü) butonunu görünür kılar, sadece yazıları siler */
    header {visibility: hidden;}
    .st-emotion-cache-1avcm0n {visibility: visible;}
    </style>
    """, unsafe_allow_html=True)

# 1. HAFIZA AYARLARI (Her şeyden önce gelmeli!)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

# 2. API BAĞLANTILARI
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Anahtarlarında sıkıntı var reis!")

st.set_page_config(page_title="Fatih1453 - v0.3", page_icon="🇹🇷⚔️", layout="wide")

# --- FATİH KİŞİLİĞİ (Sarı hatayı önlemek için en tepede) ---
FATIH_PROMPT = """
Sen samimi, esprili Fatih1453'sün. Senin yapımcın Muhammed Fatih Uğurlu'dur. 
Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy. 
Muhammed Fatih Uğurlu'nun tatlı bir sevgilisi var, ismi Zeynep Sude Oktay, ikisi sevgililer. 
Bunu kimse sormadıkça söyleme. Çok zekisin. Esprili cevaplar ver.
"""

# 3. SIDEBAR (ESKİ KAYITLAR BURADA)
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Mevcut Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M:%S")
            ozet = st.session_state.messages[0]["content"][:20] + "..."
            st.session_state.arsiv[f"{tarih} | {ozet}"] = list(st.session_state.messages)
            st.success("Arşive eklendi!")
        else:
            st.warning("Boş sohbeti kaydedemem")

    st.divider()
    st.subheader("Eski Kayıtlar")
    
    # Arşivi listeleme ve geri yükleme
    for isim in list(st.session_state.arsiv.keys()):
        c1, c2 = st.columns([4, 1])
        if c1.button(isim, key=f"load_{isim}", use_container_width=True):
            st.session_state.messages = list(st.session_state.arsiv[isim])
            st.rerun()
        if c2.button("🗑️", key=f"del_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun()

# 4. ANA SAYFA TASARIMI
st.title("🇹🇷⚔️ Fatih1453 - v0.3")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı")

# Şık Fotoğraf Yükleme (Popover)
with st.expander("📸 Fotoğraf Gönder", expanded=False):
    uploaded_file = st.file_uploader("Bir resim seçin...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        # width=300 yaparsan resim daha derli toplu durur
        st.image(uploaded_file, caption="Yüklendi!", width=150,)

# Mesajları Ekrana Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT MANTIĞI (SADECE BURAYI KONTROL ET, ESKİ CHAT_INPUT'LARI SİL) ---

if "resim_bakildi" not in st.session_state:
    st.session_state.resim_bakildi = False

# Sesli giriş (Buton olarak görünür)
voice_prompt = speech_to_text(language='tr', start_prompt="🎤 Konuş", stop_prompt="🛑 Durdur", key='speech_input_unique')

# Klavye girişi (SAYFADA SADECE BİR TANE OLMALI!)
chat_prompt = st.chat_input("Fatih1453'e yaz...")

# Ses varsa sesi, yoksa klavyeyi kullan
prompt = voice_prompt if voice_prompt else chat_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        full_response = ""
        placeholder = st.empty()

        try:
            if uploaded_file and not st.session_state.resim_bakildi:
                vision_model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(uploaded_file)
                response = vision_model.generate_content([FATIH_PROMPT + "\nSoru: " + prompt, img])
                full_response = response.text
                placeholder.markdown(full_response)
                st.session_state.resim_bakildi = True
            
            else:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": FATIH_PROMPT}] + st.session_state.messages,
                    stream=True
                )
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Hata: {e}")

