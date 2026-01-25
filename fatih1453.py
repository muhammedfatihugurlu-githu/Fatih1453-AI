import streamlit as st
from groq import Groq
import time
import base64

# API Key'i Streamlit Secrets'tan alıyoruz
# Eğer hata alırsan Streamlit Secrets kısmına yeni bir key koymayı unutma!
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol et abim.")

# Fotoğrafı yapay zekanın anlayacağı dile çeviren fonksiyon
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Başlıklar
st.set_page_config(page_title="Fatih1453 AI", page_icon="🇹🇷⚔️", layout="wide")
st.title("🇹🇷⚔️ Fatih1453 - v0.2")
st.caption("Muhammed Fatih Uğurlu'nun Özel Yapay Zeka Asistanı")

# --- ŞIK DOSYA YÜKLEME BUTONU ---
# Bu buton ana sayfada durur, basınca içindeki yükleme alanı açılır.
with st.popover("📸 Fotoğraf Gönder"):
    uploaded_file = st.file_uploader("Analiz edilecek resmi seç", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Yüklenen Resim Önizleme")

# Hafıza (Chat History) ayarları
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fatih1453'e yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # FOTOĞRAF VARSA: Vizyon modelini kullan, YOKSA: 70b ile devam et
           # En güncel vision modelini buraya ekledik
            model_id = "pixtral-12b-2409" if uploaded_file else "llama-3.3-70b-versatile"
            
            # Mesaj içeriğini Vision formatına uygun hazırlıyoruz
            if uploaded_file:
                base64_image = encode_image(uploaded_file)
                api_messages = [
                    {"role": "system", "content": "Senin adın Fatih1453. Samimi ve esprili ol. Bilge birisin. Resimdekileri yorumla. Çok ama çok komik birisin. Muhammed Fatih Uğurlu, seni yapan kişi, 2026 yılında bir kodyazar, Osmanlı padişahı değil, ona saygılı ol, birde tatlı bir sevgilisi var, ismi Zeynep Sude Oktay, ikisi sevgililer, bak bunu kimse sormadıkça söyleme. İnsanlara her konuda yardımcı ol. Türkçe konuş."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ]
            else:
                # Normal metin sohbeti (Senin eski sistemin)
                api_messages = [
                    {"role": "system", "content": "Senin adın Fatih1453. Samimi ve esprili ol. Bilge birisin. Çok ama çok komik birisin. Muhammed Fatih Uğurlu, seni yapan kişi, 2026 yılında bir kodyazar, Osmanlı padişahı değil, ona saygılı ol, birde tatlı bir sevgilisi var, ismi Zeynep Sude Oktay, ikisi sevgililer, bak bunu kimse sormadıkça söyleme. İnsanlara her konuda yardımcı ol. Türkçe konuş."},
                    *st.session_state.messages
                ]

            completion = client.chat.completions.create(
                model=model_id,
                messages=api_messages,
                stream=True
            )
            
            full_response = ""
            placeholder = st.empty()
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"yapmaa, bir sorun çıktı: {e}")

# --- HAFIZA KONTROLÜ (En üstte olmalı) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# HATA ALDIĞIN YER BURASI: Arşivi de buraya tanımlamalıyız
if "arsiv" not in st.session_state:
    st.session_state.arsiv = {}  # Boş bir sözlük oluşturduk

# --- YAN MENÜ (SIDEBAR) AYARLARI ---
with st.sidebar:
    st.title("📜 Fetih Arşivi")

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Sohbeti Kaydet", use_container_width=True):
        if st.session_state.messages:
            tarih = time.strftime("%H:%M")
            ozet = st.session_state.messages[0]["content"][:15]
            # Mesajları kopyalarken list() kullanmak doğru bir yaklaşım
            st.session_state.arsiv[f"{tarih} | {ozet}"] = list(st.session_state.messages)
            st.success("Kaydedildi abim!")  # Bu satır if bloğunun içinde olmalıydı

    st.divider()
    st.subheader("Eski Kayıtlar")

    # Sözlük üzerinde işlem yaparken list(keys()) kullanmak silme işlemleri için güvenlidir
    for isim in list(st.session_state.arsiv.keys()):
        c1, c2 = st.columns([4, 1])
        
        # Sohbeti Geri Yükle
        if c1.button(f"{isim}", key=f"load_{isim}"):
            st.session_state.messages = st.session_state.arsiv[isim]
            st.rerun()
            
        # Sohbeti Sil
        if c2.button("🗑️", key=f"del_{isim}"):
            del st.session_state.arsiv[isim]
            st.rerun() 