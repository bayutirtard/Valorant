import streamlit as st
from groq import Groq
import re

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

# Inisialisasi Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Baca isi markdown
def load_markdown_data():
    try:
        with open("valorant.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Valorant data not find."

# Simpan isi markdown
markdown_data = load_markdown_data()

# Inisialisasi riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": "You are a Valorant expert. You are only allowed to answer based on the data provided below. "
    "You must not use any outside knowledge. Do not guess. Do not refer to other games. "
    "If the answer is not clearly found in the data, respond only with: "
    "\"Sorry, that information is not available in the current database.\" "
    "Even if the question seems obvious or easy, do not use general knowledge. "
    "Use ONLY the following data as your source:\n\n"
    + markdown_data
        }
    ]

def render_chat(role, content):
    if role == "user":
        st.markdown(f"""
        <div style="background-color:#1e1e1e; padding:10px; border-radius:10px; margin-bottom:10px; color:white;">
            <b>You:</b> {content}
        </div>
        """, unsafe_allow_html=True)

    elif role == "assistant":
        # Buat HTML wrapper
        html = f"""
        <div style="background-color:#2a2a2a; padding:10px; border-radius:10px; margin-bottom:10px; color:white;">
            <b>Bot 🎮:</b><br>
        """

        # Gabungkan teks dan gambar
        pattern = r'!\[.*?\]\((.*?)\)'
        last_end = 0
        for match in re.finditer(pattern, content):
            # Tambahkan teks sebelum gambar
            if match.start() > last_end:
                text_before = content[last_end:match.start()].strip().replace("\n", "<br>")
                html += f"{text_before}<br>"

            # Tambahkan gambar sebagai tag HTML <img>
            img_url = match.group(1)
            html += f"<img src='{img_url}' style='max-width:100%; border-radius:10px; margin-top:10px; margin-bottom:10px;'><br>"
            last_end = match.end()

        # Tambahkan sisa teks setelah gambar terakhir
        if last_end < len(content):
            text_after = content[last_end:].strip().replace("\n", "<br>")
            html += f"{text_after}"

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)


# Tampilkan riwayat chat
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

# Kirim pertanyaan
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

# Reset chat
if reset:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": "You are a Valorant expert. You are only allowed to answer based on the data provided below. "
            "You must not use any outside knowledge. Do not guess. Do not refer to other games. "
            "If the answer is not clearly found in the data, respond only with: "
            "\"Sorry, that information is not available in the current database.\" "
            "Even if the question seems obvious or easy, do not use general knowledge. "
            "Use ONLY the following data as your source:\n\n"
            + markdown_data
        }
    ]
    st.rerun()






