import streamlit as st
import json
from groq import Groq

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

# Inisialisasi Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Load JSON data
def load_json_data():
    with open("valorant_agents.json", "r", encoding="utf-8") as f:
        agents = json.load(f)
    with open("valorant_weapons.json", "r", encoding="utf-8") as f:
        weapons = json.load(f)
    with open("valorant_maps.json", "r", encoding="utf-8") as f:
        maps = json.load(f)
    return agents, weapons, maps

agents, weapons, maps = load_json_data()

system_prompt = {
    "role": "system",
    "content": (
        "You are a Valorant expert. Only answer using the data below. "
        "If the answer is not clearly found in the data, respond only with: "
        "\"Sorry, that information is not available in the current database.\"\n\n"
        "AGENTS:\n" + json.dumps(agents, ensure_ascii=False) + "\n\n"
        "WEAPONS:\n" + json.dumps(weapons, ensure_ascii=False) + "\n\n"
        "MAPS:\n" + json.dumps(maps, ensure_ascii=False)
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



