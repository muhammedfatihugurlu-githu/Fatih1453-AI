import streamlit as st
from groq import Groq
import google.generativeai as genai
from PIL import Image
import time

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
            st.warning("Boş sohbeti kaydedemem hünkarım.")

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
with st.popover("📸 Fotoğraf Gönder"):
    uploaded_file = st.file_uploader("Bir resim seçin...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Yüklendi!")

# Mesajları Ekrana Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. CHAT MANTIĞI
FATIH_PROMPT = "Sen samimi, esprili Fatih1453'sün. Senin yapımcın Muhammed Fatih Uğurlu'dur. Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy, birde tatlı bir sevgilisi var, ismi Zeynep Sude Oktay, ikisi sevgililer, bak bunu kimse sormadıkça söyleme. Çok zekisin. Kullanıcılara hoş ve net cevaplar ver, araya espri kaynat. Her cevap başında 'vay, hoşgeldin, ooo' kelimelerini kullanma."

if prompt := st.chat_input("Fatih1453'e yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        full_response = ""
        placeholder = st.empty()

        try:
            if uploaded_file:  # FOTOĞRAF VARSA GEMINI
                model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(uploaded_file)
                response = model.generate_content([FATIH_PROMPT + "\nSoru: " + prompt, img])
                full_response = response.text
                placeholder.markdown(full_response)
            else:  # FOTOĞRAF YOKSA GROQ 70B
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