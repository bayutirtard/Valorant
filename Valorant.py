import streamlit as st
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# --- Simpan ke Google Sheets
def save_feedback_to_gsheet(user_q, bot_a, feedback):
    creds = Credentials.from_service_account_info(
        json.loads(st.secrets["GS_CRED_JSON"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1Nlis6U5BCx7afjdulH2pRKvJmZG0PpwpBFpoMTN1L4s/edit?usp=sharing"
    )
    ws = sh.sheet1
    ws.append_row([str(datetime.now()), user_q, bot_a, feedback])

# --- CSS untuk tombol session aktif
st.markdown("""
    <style>
    div[data-testid="stSidebar"] button.session-active {
        background-color: #666 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Chatbot config
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

# --- Init state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {
        "messages": [system_prompt],
        "ratings": {},
        "n_like": 0,
        "n_dislike": 0,
        "added_to_history": False
    }
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = None
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False
if "del_confirm_idx" not in st.session_state:
    st.session_state.del_confirm_idx = None

# --- Render chat bubble
def render_chat(role, content):
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)

# --- Rating buttons
def rating_buttons(idx):
    chat_data = st.session_state.chat_history
    ratings = chat_data["ratings"]

    chat_hist = chat_data["messages"][1:]
    msg_i = idx * 2
    if msg_i >= 0 and (msg_i + 1) < len(chat_hist):
        user_msg = chat_hist[msg_i]["content"]
        bot_msg = chat_hist[msg_i + 1]["content"]
    else:
        return

    if idx in ratings:
        thumb, stars = ratings[idx]
        st.markdown(f"{'👍' if thumb == 'up' else '👎'} Rated — {'⭐'*stars} ({stars} stars)")
        return

    col1, col2 = st.columns([1, 1])
    if f"temp_thumb_{idx}" not in st.session_state:
        with col1:
            if st.button("👍", key=f"up_{idx}"):
                st.session_state[f"temp_thumb_{idx}"] = "up"
        with col2:
            if st.button("👎", key=f"down_{idx}"):
                st.session_state[f"temp_thumb_{idx}"] = "down"

    if f"temp_thumb_{idx}" in st.session_state:
        stars_value = st.select_slider(
            "Give a star rating:",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: "⭐" * x,
            key=f"stars_{idx}"
        )
        if st.button("Submit Rating", key=f"submit_rating_{idx}"):
            thumb = st.session_state[f"temp_thumb_{idx}"]
            ratings[idx] = (thumb, stars_value)
            if thumb == "up":
                chat_data["n_like"] += 1
            else:
                chat_data["n_dislike"] += 1
            save_feedback_to_gsheet(user_msg, bot_msg, f"{thumb} | {stars_value} stars")
            del st.session_state[f"temp_thumb_{idx}"]
            st.markdown(f"{'👍' if thumb == 'up' else '👎'} Rated — {'⭐'*stars_value} ({stars_value} stars)")

# --- Sidebar: Menu
st.sidebar.markdown("### Menu")
if st.sidebar.button("New Chat", use_container_width=True):
    st.session_state.chat_history = {
        "messages": [system_prompt],
        "ratings": {},
        "n_like": 0,
        "n_dislike": 0,
        "added_to_history": False
    }
    st.session_state.current_chat_index = None
    st.rerun()

# --- Sidebar: Chats (tombol + delete sejajar)
st.sidebar.markdown("### Chats")
if st.session_state.all_chats:
    for i, chat in enumerate(st.session_state.all_chats):
        preview = chat["messages"][1]["content"][:40] if len(chat["messages"]) > 1 and chat["messages"][1]["role"] == "user" else "[empty]"
        is_active = st.session_state.current_chat_index == i

        col1, col2 = st.sidebar.columns([8, 1])
        with col1:
            btn_label = preview
            btn_key = f"open_{i}"
            if st.sidebar.button(btn_label, key=btn_key, use_container_width=True):
                st.session_state.chat_history = chat
                st.session_state.current_chat_index = i
                st.rerun()
            if is_active:
                st.markdown(f"<style>button[key='{btn_key}']{{background-color:#666 !important;color:white !important;}}</style>", unsafe_allow_html=True)
        with col2:
            if st.sidebar.button("🗑", key=f"del_{i}"):
                st.session_state.del_confirm_idx = i
                st.rerun()

        if st.session_state.del_confirm_idx == i:
            cc1, cc2 = st.sidebar.columns([1, 1])
            with cc1:
                if st.sidebar.button("Yes", key=f"del_yes_{i}"):
                    st.session_state.all_chats.pop(i)
                    if st.session_state.current_chat_index == i:
                        st.session_state.current_chat_index = None
                        st.session_state.chat_history = {
                            "messages": [system_prompt],
                            "ratings": {},
                            "n_like": 0,
                            "n_dislike": 0,
                            "added_to_history": False
                        }
                    st.session_state.del_confirm_idx = None
                    st.rerun()
            with cc2:
                if st.sidebar.button("Cancel", key=f"del_no_{i}"):
                    st.session_state.del_confirm_idx = None
                    st.rerun()
            st.sidebar.markdown("---")
else:
    st.sidebar.info("No chat history yet.")

# --- Show current chat & ratings
for idx in range(0, (len(st.session_state.chat_history["messages"]) - 1) // 2):
    msg_user = st.session_state.chat_history["messages"][1:][idx * 2]
    msg_bot = st.session_state.chat_history["messages"][1:][idx * 2 + 1]
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
    st.session_state.chat_history["messages"].append({"role": "user", "content": user_input})

    if not st.session_state.chat_history["added_to_history"] and len(st.session_state.chat_history["messages"]) == 2:
        st.session_state.all_chats.append(st.session_state.chat_history)
        st.session_state.chat_history["added_to_history"] = True
        st.session_state.current_chat_index = len(st.session_state.all_chats) - 1

    with st.spinner("Answering..."):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=st.session_state.chat_history["messages"]
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history["messages"].append({"role": "assistant", "content": answer})
        save_feedback_to_gsheet(user_input, answer, "")
    st.rerun()

# --- Reset Conversation
if reset:
    st.session_state.confirm_reset = True
    st.rerun()

if st.session_state.get("confirm_reset", False):
    st.markdown("---")
    st.error("⚠️ Are you sure you want to reset the entire conversation?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, reset", key="confirm_yes"):
            st.session_state.chat_history = {
                "messages": [system_prompt],
                "ratings": {},
                "n_like": 0,
                "n_dislike": 0,
                "added_to_history": False
            }
            keys_to_delete = [k for k in list(st.session_state.keys()) if k.startswith('temp_thumb_') or k.startswith('stars_')]
            for k in keys_to_delete:
                del st.session_state[k]
            st.session_state.confirm_reset = False
            st.rerun()
    with col2:
        if st.button("Cancel", key="confirm_no"):
            st.session_state.confirm_reset = False
            st.rerun()

# --- This Session Stats
st.markdown(f"### This Session Stats\n👍 **{st.session_state.chat_history['n_like']}**   👎 **{st.session_state.chat_history['n_dislike']}**")
