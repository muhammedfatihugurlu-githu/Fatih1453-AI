import streamlit as st
from groq import Groq

# API Key'i Streamlit Secrets'tan alıyoruz
# Eğer hata alırsan Streamlit Secrets kısmına yeni bir key koymayı unutma!
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol edin.")

st.set_page_config(page_title="Fatih1453 AI", page_icon="🇹🇷⚔️")
st.title("🇹🇷⚔️ Fatih1453 - v0.1")

# Hafıza (Chat History) ayarları
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Fatih1453'e sorun..."):
    # Kullanıcı mesajını hafızaya ekle ve ekrana yaz
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan cevabı
    with st.chat_message("assistant", avatar="🤖"):
        try:
            # Model ismini daha stabil olanla güncelledim
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": "Senin adın Fatih1453. Samimi ve esprili ol. Bilge birisin. Çok ama çok komik birisin. Muhammed Fatih Uğurlu, seni yapan kişi, 2026 yılında bir kodyazar, Osmanlı padişahı değil, ona saygılı ol. İnsanlara her konuda yardımcı ol. Türkçe konuş."},
                    *st.session_state.messages
                ],
                stream=True
            )
            
            full_response = ""
            placeholder = st.empty()
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response += content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            # Cevabı hafızaya kaydet
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Yapmaa, bir hata oluştu: {e}")

# --- YAN MENÜ (SIDEBAR) AYARLARI ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
