import streamlit as st
from groq import Groq

# API Key'i Streamlit Secrets'tan güvenli bir şekilde alıyoruz
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Fatih1453 AI", page_icon="🇹🇷⚔️")
st.title("🇹🇷⚔️ Fatih1453 Yapay Zekası")

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
    with st.chat_message("assistant", avatar="🛡️"):
        # API isteği
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Senin adın Fatih1453. Samimi ve esprili ol. Bilge bir Osmanlı padişahı gibi Türkçe konuş."},
                *st.session_state.messages
            ],
            stream=True
        )
        
        full_response = ""
        placeholder = st.empty()
        
        # Gelen veriyi parça parça oku
        for chunk in completion:
            # İçerik varsa ekle (Hata almamak için None kontrolü yapıyoruz)
            content = chunk.choices[0].delta.content
            if content is not None:
                full_response += content
                placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)

    # Asistan cevabını hafızaya kaydet
    st.session_state.messages.append({"role": "assistant", "content": full_response})