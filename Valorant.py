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

# ======= CSS =======
st.markdown("""
<style>
.chat-bubble {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #2f2f2f;
    padding: 8px 10px;
    border-radius: 8px;
    margin-bottom: 4px;
    cursor: pointer;
}
.chat-bubble:hover {
    background-color: #444;
}
.chat-bubble.active {
    background-color: #555;
}
.chat-title {
    color: white;
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}
.chat-menu {
    color: #bbb;
    padding-left: 8px;
    cursor: pointer;
}
.chat-menu:hover {
    color: white;
}
.menu-box {
    background-color: #2f2f2f;
    border-radius: 6px;
    padding: 6px;
    margin-top: 2px;
}
.menu-item {
    padding: 4px 6px;
    color: white;
    cursor: pointer;
    border-radius: 4px;
}
.menu-item:hover {
    background-color: #444;
}
</style>
""", unsafe_allow_html=True)

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

# ======= Chat Bubble Rendering =======
def render_chat_bubble(i, chat):
    preview = chat.get("title") or (
        chat["messages"][1]["content"][:40] if len(chat["messages"]) > 1 else "[empty]"
    )
    is_active = st.session_state.current_chat_index == i
    bubble_class = "chat-bubble active" if is_active else "chat-bubble"

    # Bubble HTML
    st.markdown(
        f"""
        <div class="{bubble_class}" onclick="window.parent.postMessage({{'type': 'open_chat', 'index': {i}}}, '*')">
            <div class="chat-title">{preview}</div>
            <div class="chat-menu" onclick="window.parent.postMessage({{'type': 'menu_click', 'index': {i}}}, '*')">⋮</div>
        </div>
        """, unsafe_allow_html=True
    )

    # Menu
    if st.session_state.menu_open == i:
        with st.container():
            st.markdown('<div class="menu-box">', unsafe_allow_html=True)
            # Rename
            new_title = st.text_input("Rename chat", value=preview, key=f"rename_{i}")
            if st.button("Save", key=f"save_name_{i}"):
                chat["title"] = new_title
                st.session_state.menu_open = None
                st.rerun()
            # Delete
            if st.button("Delete", key=f"delete_{i}"):
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
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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

# ======= Stats =======
st.markdown(f"### This Session Stats\n👍 **{st.session_state.chat_history['n_like']}**   👎 **{st.session_state.chat_history['n_dislike']}**")
