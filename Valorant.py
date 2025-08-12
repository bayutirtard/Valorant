import streamlit as st
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# ======= Simpan ke Google Sheets =======
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

# ======= Config =======
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ======= Load Data =======
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
        "You are a Valorant expert. Only answer based on the data below. "
        "Don't guess, don't use outside knowledge. "
        "If not found, say: \"Sorry, that information is not available in the current database.\" "
        "Use ONLY the following data:\n\n" + markdown_data
    )
}

# ======= State Init =======
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {
        "messages": [system_prompt],
        "ratings": {},
        "n_like": 0,
        "n_dislike": 0,
        "title": None,
        "added_to_history": False
    }
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = None
if "menu_open" not in st.session_state:
    st.session_state.menu_open = None
if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = None
if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = None

# ======= Render Chat Bubble =======
def render_chat_bubble(i, chat):
    preview = chat.get("title") or (
        chat["messages"][1]["content"][:40] if len(chat["messages"]) > 1 else "[empty]"
    )

    col1, col2 = st.sidebar.columns([8, 1])
    with col1:
        if st.button(preview, key=f"open_{i}", use_container_width=True):
            st.session_state.chat_history = chat
            st.session_state.current_chat_index = i
            st.rerun()

    with col2:
        if st.button("⋮", key=f"menu_{i}"):
            st.session_state.menu_open = i if st.session_state.menu_open != i else None
            st.session_state.rename_mode = None
            st.session_state.delete_confirm = None
            st.rerun()

    # Popup menu menempel di bawah ⋮
    if st.session_state.menu_open == i:
        with st.sidebar.container():
            st.markdown('<div class="menu-box">', unsafe_allow_html=True)
            if st.button("Rename", key=f"renamebtn_{i}", use_container_width=True):
                st.session_state.rename_mode = i
                st.session_state.delete_confirm = None
                st.rerun()
            if st.button("Delete", key=f"deletebtn_{i}", use_container_width=True):
                st.session_state.delete_confirm = i
                st.session_state.rename_mode = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Mode Rename
    if st.session_state.rename_mode == i:
        with st.sidebar.container():
            new_title = st.text_input("Title", value=preview, key=f"rename_{i}")
            if st.button("Save", key=f"savename_{i}"):
                chat["title"] = new_title
                st.session_state.menu_open = None
                st.session_state.rename_mode = None
                st.rerun()
            if st.button("Cancel", key=f"cancelrename_{i}"):
                st.session_state.rename_mode = None

    # Mode Delete
    if st.session_state.delete_confirm == i:
        with st.sidebar.container():
            st.error("Delete this chat?")
            if st.button("Yes, Delete", key=f"yesdelete_{i}"):
                st.session_state.all_chats.pop(i)
                if st.session_state.current_chat_index == i:
                    st.session_state.current_chat_index = None
                    st.session_state.chat_history = {
                        "messages": [system_prompt],
                        "ratings": {},
                        "n_like": 0,
                        "n_dislike": 0,
                        "title": None,
                        "added_to_history": False
                    }
                st.session_state.menu_open = None
                st.session_state.delete_confirm = None
                st.rerun()
            if st.button("Cancel", key=f"canceldelete_{i}"):
                st.session_state.delete_confirm = None

# ======= Sidebar Menu =======
st.sidebar.markdown("### Menu")
if st.sidebar.button("New Chat", use_container_width=True):
    st.session_state.chat_history = {
        "messages": [system_prompt],
        "ratings": {},
        "n_like": 0,
        "n_dislike": 0,
        "title": None,
        "added_to_history": False
    }
    st.session_state.current_chat_index = None
    st.session_state.menu_open = None
    st.rerun()

# ======= Sidebar Chats =======
st.sidebar.markdown("### Chats")
if st.session_state.all_chats:
    for i, chat in enumerate(st.session_state.all_chats):
        render_chat_bubble(i, chat)
else:
    st.sidebar.info("No chat history yet.")

# ======= Main Chat Rendering =======
def render_chat(role, content):
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)

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
            st.rerun()

for idx in range(0, (len(st.session_state.chat_history["messages"]) - 1) // 2):
    msg_user = st.session_state.chat_history["messages"][1:][idx * 2]
    msg_bot = st.session_state.chat_history["messages"][1:][idx * 2 + 1]
    render_chat(msg_user["role"], msg_user["content"])
    render_chat(msg_bot["role"], msg_bot["content"])
    rating_buttons(idx)
    st.markdown("---")

# ======= Input Form =======
st.markdown("<br>", unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.text_input("Type your question here", key="input_text", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Send")
    with col3:
        reset = st.form_submit_button("Reset")

if submit and user_input:
    st.session_state.chat_history["messages"].append({"role": "user", "content": user_input})
    if not st.session_state.chat_history["added_to_history"] and len(st.session_state.chat_history["messages"]) == 2:
        st.session_state.chat_history["title"] = user_input[:40]
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

if reset:
    st.session_state.confirm_reset_all = True
    st.rerun()

if st.session_state.get("confirm_reset_all", False):
    st.markdown("---")
    st.error("Are you sure you want to reset and delete all chats in this session?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, reset all", key="confirm_yes_all"):
            st.session_state.all_chats.clear()
            st.session_state.chat_history = {
                "messages": [system_prompt],
                "ratings": {},
                "n_like": 0,
                "n_dislike": 0,
                "title": None,
                "added_to_history": False
            }
            st.session_state.current_chat_index = None
            st.session_state.confirm_reset_all = False
            st.rerun()
    with col2:
        if st.button("Cancel", key="confirm_no_all"):
            st.session_state.confirm_reset_all = False
            st.rerun()

# ======= Stats =======
st.markdown(f"### This Session Stats\n👍 **{st.session_state.chat_history['n_like']}**   👎 **{st.session_state.chat_history['n_dislike']}**")





