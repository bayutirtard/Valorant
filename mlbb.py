import streamlit as st
from groq import Groq
from PIL import Image

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot MLBB", page_icon="🎮")
st.title("Chatbot AI Mobile Legends")

# Inisialisasi Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Baca isi markdown
def load_markdown_data():
    try:
        with open("data_hero.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Data hero tidak ditemukan."

# Simpan isi markdown
markdown_data = load_markdown_data()

# Inisialisasi riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": "You are a Mobile Legends expert. You are only allowed to answer based on the data provided below. "
    "You must not use any outside knowledge. Do not guess. Do not refer to other games. "
    "If the answer is not clearly found in the data, respond only with: "
    "\"Sorry, that information is not available in the current database.\" "
    "Even if the question seems obvious or easy, do not use general knowledge. "
    "Use ONLY the following data as your source:\n\n"
    + markdown_data
        }
    ]

# Tampilkan obrolan sebelumnya
for msg in st.session_state.chat_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Bot:** {msg['content']}")

# Input form
st.markdown("<br>", unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.text_input("Ketik pertanyaan kamu", placeholder="Ketik pertanyaanmu disini", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Kirim")
    with col3:
        reset = st.form_submit_button("Reset")

# Kirim pertanyaan
if submit and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# Reset chat
if reset:
    st.session_state.chat_history = []
    st.rerun()















