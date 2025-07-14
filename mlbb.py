import streamlit as st
from groq import Groq

# API Key dari secrets.toml
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="MLBB Chatbot AI Gratis", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends")

st.markdown("Tanyakan apa saja tentang hero, counter, build, atau meta MLBB!")

# Input pertanyaan
user_input = st.text_input("Ketik pertanyaan kamu di sini 👇")

# Hapus jawaban lama
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if user_input:
    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Kamu adalah pakar Mobile Legends."},
                {"role": "user", "content": user_input}
            ]
        )
        st.session_state.last_answer = response.choices[0].message.content

# Tampilkan jawaban terbaru saja
if st.session_state.last_answer:
    st.markdown("**🤖 Bot:**")
    st.write(st.session_state.last_answer)
