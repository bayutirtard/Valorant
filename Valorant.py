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
        "Show the picture of the agents, weapon and others if user ask about the name of it "
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
    col1, col2, col3 = st.columns([6, 1, 1, 1])
    with col1:
        user_input = st.text_input("Type your question here", placeholder="Type your question here...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Send")
    with col3:
        reset = st.form_submit_button("Reset")
    with col4:
    # Text input untuk user (nanti diisi hasil dictation)
    user_input = st.text_input("Type your question here", key="input_text", placeholder="Type your question here...", label_visibility="collapsed")

    # Tombol Dictate + Script HTML (hanya tampil di browser support)
    st.components.v1.html("""
        <button id="dictateBtn" style="margin-top:6px;padding:3px 12px 3px 5px;border-radius:6px;border:1px solid #ccc;background:#1e232b;color:#fff;cursor:pointer;font-size:15px;">
            🎤 Dictate
        </button>
        <script>
        const inputBox = window.parent.document.querySelector('input[data-testid="stTextInput"][id^="input_text"]');
        const btn = document.getElementById('dictateBtn');
        if (btn && inputBox) {
            btn.onclick = function() {
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {
                    alert('Browser tidak support speech recognition!');
                    return;
                }
                var recognition = new SpeechRecognition();
                recognition.lang = "id-ID"; // Bisa diganti "en-US" sesuai kebutuhan
                recognition.onresult = function(event) {
                    inputBox.value = event.results[0][0].transcript;
                    inputBox.dispatchEvent(new Event('input', { bubbles: true }));
                };
                recognition.start();
            }
        }
        </script>
    """, height=38)


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




