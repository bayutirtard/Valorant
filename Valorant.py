import streamlit as st
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- Fungsi simpan log ke Google Sheets
def save_feedback_to_gsheet(user_q, bot_a, feedback):
    creds = Credentials.from_service_account_file(
        "gspread_cred.json", scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Nlis6U5BCx7afjdulH2pRKvJmZG0PpwpBFpoMTN1L4s/edit?usp=sharing")
    ws = sh.sheet1
    ws.append_row([str(datetime.now()), user_q, bot_a, feedback])

# --- Streamlit config
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [system_prompt]
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

def render_chat(role, content):
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)

def rating_buttons(idx):
    col1, col2 = st.columns([1,1])
    chat_hist = st.session_state.chat_history[1:]
    user_msg = None
    bot_msg = None
    msg_i = idx*2
    if msg_i >= 0 and (msg_i+1) < len(chat_hist):
        user_msg = chat_hist[msg_i]["content"]
        bot_msg = chat_hist[msg_i+1]["content"]
    with col1:
        if st.button("👍", key=f"up_{idx}"):
            st.session_state[f"rate_{idx}"] = "up"
            st.success("Terima kasih atas ratingnya!")
            if user_msg and bot_msg:
                save_feedback_to_gsheet(user_msg, bot_msg, "up")
    with col2:
        if st.button("👎", key=f"down_{idx}"):
            st.session_state[f"rate_{idx}"] = "down"
            st.info("Terima kasih atas feedbacknya!")
            if user_msg and bot_msg:
                save_feedback_to_gsheet(user_msg, bot_msg, "down")

# --- Tampilkan chat & rating
for idx in range(0, (len(st.session_state.chat_history)-1)//2):
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

if submit and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Answering..."):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        save_feedback_to_gsheet(user_input, answer, "")   # log QnA tanpa feedback
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
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith('rate_')]
            for k in keys_to_delete:
                del st.session_state[k]
            st.session_state.confirm_reset = False
            st.rerun()
    with col2:
        if st.button("Cancel", key="confirm_no"):
            st.session_state.confirm_reset = False
            st.rerun()

# --- Statistik feedback
n_like = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "up")
n_dislike = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "down")
st.markdown(f"### Statistik Feedback Sesi Ini:  \n👍 **{n_like}** &nbsp;&nbsp;&nbsp; 👎 **{n_dislike}**")
