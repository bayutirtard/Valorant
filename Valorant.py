import streamlit as st
from groq import Groq
import csv
import os
from datetime import datetime

# === Logging ke CSV ===
def log_interaction(user_msg, bot_msg, feedback=None, filename="chat_feedback_log.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "user_question", "bot_answer", "feedback"])
        writer.writerow([datetime.now().isoformat(), user_msg, bot_msg, feedback or ""])

# --- Streamlit config
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

# --- Init Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Load markdown (dummy)
def load_markdown_data():
    try:
        with open("valorant.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Valorant data not found."

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

# --- Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [system_prompt]
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

# --- Fungsi render chat
def render_chat(role, content):
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)

# --- Feedback Button Streamlit + Log feedback
def rating_buttons(idx):
    col1, col2 = st.columns([1,1])
    # Ambil chat user & bot untuk idx ini (asumsi urutan user, bot, user, bot, ...)
    user_msg = None
    bot_msg = None
    msg_i = idx*2  # chat_history[1:] (jadi idx ke-n = user ke-(2n), bot ke-(2n+1))
    chat_hist = st.session_state.chat_history[1:]  # skip system_prompt
    if msg_i >= 0 and (msg_i+1) < len(chat_hist):
        user_msg = chat_hist[msg_i]["content"]
        bot_msg = chat_hist[msg_i+1]["content"]
    with col1:
        if st.button("👍", key=f"up_{idx}"):
            st.session_state[f"rate_{idx}"] = "up"
            st.success("Terima kasih atas ratingnya!")
            # Simpan feedback ke CSV (feedback=up)
            if user_msg and bot_msg:
                log_interaction(user_msg, bot_msg, feedback="up")
    with col2:
        if st.button("👎", key=f"down_{idx}"):
            st.session_state[f"rate_{idx}"] = "down"
            st.info("Terima kasih atas feedbacknya!")
            # Simpan feedback ke CSV (feedback=down)
            if user_msg and bot_msg:
                log_interaction(user_msg, bot_msg, feedback="down")

# --- Tampilkan chat (dan rating)
for idx in range(0, (len(st.session_state.chat_history)-1)//2):
    # setiap idx = 1 chat (user + bot)
    msg_user = st.session_state.chat_history[1:][idx*2]
    msg_bot = st.session_state.chat_history[1:][idx*2+1]
    render_chat(msg_user["role"], msg_user["content"])
    render_chat(msg_bot["role"], msg_bot["content"])
    rating_buttons(idx)
    st.markdown("---")

# --- Input form
st.markdown("<br>", unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.text_input(
            "Type your question here",
            key="input_text",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
    with col2:
        submit = st.form_submit_button("Send")
    with col3:
        reset = st.form_submit_button("Reset")

# --- Proses input user (dan log chat ke CSV)
if submit and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Answering..."):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        # LOG CHAT: User + Bot (feedback None, hanya record QnA)
        log_interaction(user_input, answer)
    st.rerun()

# --- RESET dengan popup konfirmasi & hapus feedback
if reset:
    st.session_state.confirm_reset = True
    st.rerun()

if st.session_state.get("confirm_reset", False):
    st.markdown("---")
    st.error("⚠️ Are you sure you want to reset the entire conversation?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, reset", key="confirm_yes"):
            st.session_state.chat_history = [system_prompt]
            # Reset feedback
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith('rate_')]
            for k in keys_to_delete:
                del st.session_state[k]
            st.session_state.confirm_reset = False
            st.rerun()
    with col2:
        if st.button("Cancel", key="confirm_no"):
            st.session_state.confirm_reset = False
            st.rerun()

# --- Statistik total Like/Dislike
n_like = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "up")
n_dislike = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "down")
st.markdown(f"### Statistik Feedback Sesi Ini:  \n👍 **{n_like}** &nbsp;&nbsp;&nbsp; 👎 **{n_dislike}**")
