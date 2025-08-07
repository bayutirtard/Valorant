import streamlit as st
from groq import Groq

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

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
        "Show the picture of the agents, arsenal and others if user ask something about it "
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
        st.markdown(f"**You:** {content}")

    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)


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
            model="meta-llama/llama-guard-4-12b",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# === 11. RESET CHAT DENGAN SIMULASI POPUP ===
if reset:
    st.session_state.confirm_reset = True

# Tampilkan "popup" konfirmasi jika diminta
if st.session_state.get("confirm_reset", False):
    with st.container():
        st.markdown("---")
        st.error("⚠️ Are you sure you want to reset the entire conversation?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, reset", key="confirm_yes"):
                st.session_state.chat_history = [system_prompt]
                st.session_state.confirm_reset = False
                st.rerun()
        with col2:
            if st.button("Cancel", key="confirm_no"):
                st.session_state.confirm_reset = False
                st.rerun()















