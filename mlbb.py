import streamlit as st
from groq import Groq

st.set_page_config(page_title="MLBB GPT Chatbot", layout="centered")

# CSS mirip GPT UI
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
        margin-bottom: 80px;
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
    }
    .reset-btn {
        position: fixed;
        bottom: 90px;
        right: 30px;
        background-color: #ff6961;
        color: white;
        border: none;
        border-radius: 100px;
        padding: 0.7rem 1.2rem;
        font-size: 14px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Groq API client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi memori obrolan
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas, kontekstual, dan mudah dimengerti."}
    ]

# Tampilkan seluruh riwayat chat
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history[1:]:  # skip system message
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><b>Kamu:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="chat-bubble-bot"><b>Bot:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Tombol reset tetap di pojok kanan bawah
st.markdown("""
    <form method="post">
        <button class="reset-btn" name="reset" type="submit">🔁 Reset</button>
    </form>
""", unsafe_allow_html=True)

# Proses reset jika tombol ditekan
if st.session_state.get("reset_trigger", False):
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas, kontekstual, dan mudah dimengerti."}
    ]
    st.session_state.reset_trigger = False
    st.rerun()

# Menangkap input POST manual (karena pakai <form>)
if st.requested_url_query_params.get("reset") == "":
    st.session_state.reset_trigger = True
    st.rerun()

# Kolom input tetap di bawah layar
with st.container():
    st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
    user_input = st.text_input("Tulis pertanyaanmu di sini lalu tekan Enter", key="user_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# Proses input dan jawabannya
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Bot sedang berpikir..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    st.rerun()
