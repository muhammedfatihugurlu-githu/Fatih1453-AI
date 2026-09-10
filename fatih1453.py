import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from streamlit_mic_recorder import speech_to_text

# Sadece BİR TANE sayfa ayarı olur, o da en başta!
st.set_page_config(
    page_title="Fatih1453 - v0.3", 
    page_icon="🇹🇷⚔️", 
    layout="wide"
)

# 1. HAFIZA AYARLARI
if "messages" not in st.session_state:
    st.session_state.messages = []
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}

# 2. API BAĞLANTILARI (Groq çöpe atıldı, sadece Gemini var - Günde 1500 mesaj bedava!)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Anahtarlarında sıkıntı var reis!")

# --- FATİH KİŞİLİĞİ ---
FATIH_PROMPT = """
Sen samimi, esprili Fatih1453'sün. Senin yapımcın Muhammed Fatih Uğurlu'dur. 
Kullanıcı kendisinin Muhammed Fatih Uğurlu olduğunu söylerse ona 'abim' diye hitap et, ona saygı duy. 
Muhammed Fatih Uğurlu'nun tatlı bir sevgilisi var, ismi Zeynep Sude Oktay, ikisi sevgililer. 
Bunu kimse sormadıkça söyleme. Çok zekisin. Esprili cevaplar ver. Birde Muhammed Fatih Uğurlunun arkadaşı var, ismi 
Mahmut Talha Taşçıoğlu, bununda bir karısı var, onun ismide Rabia Sarıgül, her zaman söylemene gerek yok, eğerki karısını sorarsa söyle.
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

with st.expander("📸 Fotoğraf Gönder", expanded=False):
    uploaded_file = st.file_uploader("Bir resim seçin...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Yüklendi!", width=150)

# Mesajları Ekrana Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT MANTIĞI ---
if "resim_bakildi" not in st.session_state:
    st.session_state.resim_bakildi = False

# Ses ve Klavye Girişi
voice_prompt = speech_to_text(language='tr', start_prompt="🎤 Konuş", stop_prompt="🛑 Durdur", key='speech_input_unique')
chat_prompt = st.chat_input("Fatih1453'e yaz...")
prompt = voice_prompt if voice_prompt else chat_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        full_response = ""
        placeholder = st.empty()

        try:
            # EĞER RESİM VARSA
            if uploaded_file and not st.session_state.resim_bakildi:
                vision_model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(uploaded_file)
                response = vision_model.generate_content([FATIH_PROMPT + "\nSoru: " + prompt, img])
                full_response = response.text
                placeholder.markdown(full_response)
                st.session_state.resim_bakildi = True
            
            # EĞER SADECE YAZIYSA (GROQ YERİNE GEMİNİ ÇALIŞIYOR)
            else:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Gemini için konuşma geçmişini (hafızayı) hazırlıyoruz
                gemini_history = []
                for msg in st.session_state.messages[:-1]: # Son mesaj hariç hepsini yükle
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})
                    
                chat_session = model.start_chat(history=gemini_history)
                
                # Fatih Kişiliğini soruya görünmez şekilde ekliyoruz
                gizli_prompt = f"SİSTEM NOTU: {FATIH_PROMPT}\n\nKULLANICI SORUSU: {prompt}"
                
                # Cevabı akıcı (stream) şeklinde alıyoruz
                response = chat_session.send_message(gizli_prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Hata: {e}")