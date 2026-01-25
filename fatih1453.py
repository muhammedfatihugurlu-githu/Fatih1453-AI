import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image
import time

# --- AYARLAR VE API BAĞLANTILARI ---
st.set_page_config(page_title="Fatih1453 AI", page_icon="🇹🇷⚔️", layout="wide")

try:
    # Groq (Metin Zekası için)
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    # Gemini (Fotoğraf Görme Yeteneği için)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Anahtarları eksik reis! Secrets kısmını kontrol et.")

# --- SİSTEM MESAJI (KARAKTER TANIMI) ---
FATIH_PROMPT = """Senin adın Fatih1453. Samimi, bilge ve çok esprili birisin. 
Seni Muhammed Fatih Uğurlu yaptı.O 2026 yılında bir kodyazaz. Ona saygılı ol. 
Zeynep Sude Oktay ile sevgililer (kimse sormadıkça söyleme). 
Türkçe konuş, resimleri analiz ederken komik benzetmeler yap."""

# --- HAFIZA AYARLARI ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    for isim in list(st.session_state.arsiv.keys()):
        col1, col2 = st.columns([4, 1])
        if col1.button(isim, key=f"load_{isim}"):
            st.session_state.messages = st.session_state.arsiv[isim]
            st.rerun()
        if col2.button("🗑️", key=f"del_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun()

# --- ANA SAYFA ARAYÜZÜ ---
st.title("🇹🇷⚔️ Fatih1453 - v0.3")
st.caption("Muhammed Fatih Uğurlu'nun Gözü Açık Asistanı")

# ŞIK FOTOĞRAF YÜKLEME BUTONU (POPOVER)
with st.popover("📸 Fotoğraf Gönder"):
    uploaded_file = st.file_uploader("Bir resim seç hünkarım...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Analiz edilecek resim")

# MESAJLARI EKRANA BAS
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT MANTIĞI ---
if prompt := st.chat_input("Fatih1453'e yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        full_response = ""
        placeholder = st.empty()

        try:
            # SENARYO 1: FOTOĞRAF VARSA (GEMINI DEVREDE)
            if uploaded_file:
                vision_model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(uploaded_file)
                # Gemini stream desteklese de hızlı olduğu için direkt alıyoruz
                response = vision_model.generate_content([FATIH_PROMPT + "\nSoru: " + prompt, img])
                full_response = response.text
                placeholder.markdown(full_response)
            
            # SENARYO 2: SADECE METİN VARSA (GROQ 70B DEVREDE)
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
            st.error(f"Hünkarım bir sorun çıktı: {e}")

# --- KAYDETME BUTONU (SAYFA SONU) ---
if st.button("💾 Sohbeti Arşive Kaldır"):
    if st.session_state.messages:
        tarih = time.strftime("%H:%M")
        ozet = st.session_state.messages[0]["content"][:15]
        st.session_state.arsiv[f"{tarih} | {ozet}"] = list(st.session_state.messages)
        st.toast("Sohbet arşive eklendi!", icon="✅")