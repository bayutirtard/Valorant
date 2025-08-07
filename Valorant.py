import streamlit as st
from groq import Groq

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

# CSS untuk dark theme dan gambar responsif
st.markdown("""
<style>
    img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Baca isi markdown valorant.md
def load_markdown_data():
    try:
        with open("valorant.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Valorant data not found."

# Simpan isi markdown ke variabel
markdown_data = load_markdown_data()

system_prompt = {
    "role": "system",
    "content": (
        "You are a Valorant expert. You are only allowed to answer based on the data provided below. "
        "You must not use any outside knowledge. Do not guess. Do not refer to other games. "
        "If the answer is not clearly found in the data, respond only with: "
        "\"Sorry, that information is not available in the current database.\" "
        "Even if the question seems obvious or easy, do not use general knowledge. "
        "Use ONLY the following data as your source:\n\n"
        + markdown_data
    )
}

# Inisialisasi riwayat chat jika belum ada
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [system_prompt]

# Fungsi render chat
def render_chat(role, content):
    if role == "user":
        st.markdown(f"""
        <div style="background-color:#1e1e1e; padding:10px; border-radius:10px; margin-bottom:10px; color:white;">
            <b>You:</b><br>{content}
        </div>
        """, unsafe_allow_html=True)

    elif role == "assistant":
        st.markdown(f"""
        <div style="background-color:#2a2a2a; padding:10px; border-radius:10px; margin-bottom:10px; color:white;">
            <b>Bot 🎮:</b>
        </div>
        """, unsafe_allow_html=True)

        # Gunakan markdown normal (tanpa HTML)
        st.markdown(content)  # Jangan pakai unsafe_allow_html!

# Tampilkan riwayat chat (skip sistem message)
for msg in st.session_state.chat_history[1:]:
    render_chat(msg["role"], msg["content"])

# Input form
st.markdown("<br>", unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.text_input("Type your question here", placeholder="Type your question here...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Send")
    with col3:
        reset = st.form_submit_button("Reset")

# Proses input user
if submit and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Answering..."):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# Tombol reset
if reset:
    st.session_state.chat_history = [system_prompt]
    st.rerun()

