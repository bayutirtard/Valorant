import streamlit as st
from groq import Groq

# Konfigurasi dasar
st.set_page_config(page_title="Chatbot MLBB", layout="centered")

# CSS agar chat scrollable & input tetap di bawah
st.markdown("""
    <style>
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            border: 1px solid #ccc;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        .fixed-input {
            position: fixed;
            bottom: 2rem;
            left: 0;
            width: 100%;
            padding: 1rem;
            background-color: white;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }
        .block-container {
            padding-bottom: 8rem !important;  /* ruang buat input tetap terlihat */
        }
    </style>
""", unsafe_allow_html=True)

# Groq API setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Session state init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawab pertanyaan user dengan jelas dan mudah dipahami."}
    ]

st.title("🤖 Chatbot AI Mobile Legends")

# Chat area yang bisa discroll
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history[1:]:  # Skip system
        if msg["role"] == "user":
            st.markdown(f"**🧑 Kamu:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**🤖 Bot:** {msg['content']}")
    st.markdown('</div>', unsafe_allow_html=True)

# Input di bagian bawah (fixed)
with st.container():
    st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
    user_input = st.text_input("Ketik pertanyaan lalu tekan Enter", key="input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# Proses input
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    st.rerun()
