import streamlit as st
from groq import Groq

# Konfigurasi halaman
st.set_page_config(page_title="MLBB GPT Chatbot", layout="centered")

# CSS untuk tata letak mirip ChatGPT
st.markdown("""
    <style>
    .main {
        padding: 1rem 2rem;
    }
    .chat-area {
        max-height: 70vh;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 8px;
        background-color: #f5f5f5;
        margin-bottom: 100px;
    }
    .chat-bubble-user {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .chat-bubble-bot {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border: 1px solid #ddd;
    }
    .fixed-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: white;
        padding: 1rem 2rem;
        box-shadow: 0 -3px 10px rgba(0,0,0,0.1);
        z-index: 9998;
    }
    div[data-testid="stButton"][key="reset_btn"] {
        position: fixed;
        bottom: 100px;
        right: 30px;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas, kontekstual, dan mudah dimengerti."}
    ]

# Area chat yang bisa discroll
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history[1:]:  # Skip system message
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><b>Kamu:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="chat-bubble-bot"><b>Bot:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Tombol reset tetap di pojok kanan bawah
reset = st.button("🔁 Reset", key="reset_btn")
if reset:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas, kontekstual, dan mudah dimengerti."}
    ]
    st.rerun()

# Kolom input tetap di bawah
st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
user_input = st.text_input("Ketik pertanyaanmu lalu tekan Enter", key="user_input", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Proses input user
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("🤖 Bot sedang menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        bot_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    st.rerun()
