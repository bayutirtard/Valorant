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
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Nlis6U5BCx7afjdulH2pRKvJmZG0PpwpBFpoMTN1L4s/edit?usp=sharing")
    ws = sh.sheet1
    ws.append_row([str(datetime.now()), user_q, bot_a, feedback])

# --- Chatbot config
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Load & split markdown
def load_markdown_parts():
    try:
        with open("valorant.md", "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("## ")
        parts = [("## " + p).strip() for p in parts if p.strip()]
        return parts
    except FileNotFoundError:
        return ["Valorant data not found."]

markdown_parts = load_markdown_parts()

# --- Search relevant parts
def search_relevant_parts(query, parts, max_parts=3):
    query_lower = query.lower()
    matched = [p for p in parts if query_lower in p.lower()]
    if not matched:
        matched = parts[:1]
    return matched[:max_parts]

# --- State initialization
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = None
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False
if "del_confirm_idx" not in st.session_state:
    st.session_state.del_confirm_idx = None
if "n_like" not in st.session_state:
    st.session_state.n_like = 0
if "n_dislike" not in st.session_state:
    st.session_state.n_dislike = 0
if "stats_history" not in st.session_state:
    st.session_state.stats_history = []

# --- Render chat
def render_chat(role, content):
    if role == "user":
        st.markdown("**You:**")
        st.markdown(content)
    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)

# --- Rating buttons (once per QA)
def rating_buttons(idx):
    if f"rate_{idx}" in st.session_state:
        if st.session_state[f"rate_{idx}"] == "up":
            st.markdown("👍 **You rated this answer positively.**")
        else:
            st.markdown("👎 **You rated this answer negatively.**")
        return

    col1, col2 = st.columns([1, 1])
    chat_hist = st.session_state.chat_history
    user_msg = None
    bot_msg = None
    msg_i = idx * 2
    if msg_i >= 0 and (msg_i + 1) < len(chat_hist):
        user_msg = chat_hist[msg_i]["content"]
        bot_msg = chat_hist[msg_i + 1]["content"]
    with col1:
        if st.button("👍", key=f"up_{idx}"):
            st.session_state[f"rate_{idx}"] = "up"
            st.session_state.n_like += 1
            st.success("Thanks for your rating!")
            if user_msg and bot_msg:
                save_feedback_to_gsheet(user_msg, bot_msg, "up")
    with col2:
        if st.button("👎", key=f"down_{idx}"):
            st.session_state[f"rate_{idx}"] = "down"
            st.session_state.n_dislike += 1
            st.info("Thanks for your feedback!")
            if user_msg and bot_msg:
                save_feedback_to_gsheet(user_msg, bot_msg, "down")

# --- Sidebar: Menu
st.sidebar.markdown("### Menu")
if st.sidebar.button("New Chat"):
    if st.session_state.chat_history:
        st.session_state.all_chats.append(list(st.session_state.chat_history))
        st.session_state.stats_history.append({
            "like": st.session_state.n_like,
            "dislike": st.session_state.n_dislike
        })
    st.session_state.n_like = 0
    st.session_state.n_dislike = 0
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith('rate_')]
    for k in keys_to_delete:
        del st.session_state[k]
    st.session_state.chat_history = []
    st.session_state.current_chat_index = None
    st.rerun()

# --- Sidebar: History
st.sidebar.markdown("### Chat History")
if st.session_state.all_chats:
    for i, chat in enumerate(st.session_state.all_chats):
        preview = chat[0]["content"][:40] if chat else "[empty]"
        c1, c3 = st.sidebar.columns([8, 2])
        with c1:
            if st.button(preview, key=f"open_{i}", help="Open this chat"):
                st.session_state.chat_history = list(chat)
                st.session_state.current_chat_index = i
                st.rerun()
        with c3:
            if st.button("🗑", key=f"del_{i}", help="Delete this chat"):
                st.session_state.del_confirm_idx = i
                st.rerun()
        if st.session_state.del_confirm_idx == i:
            cc1, cc2 = st.sidebar.columns([1, 1])
            with cc1:
                if st.button("Yes", key=f"del_yes_{i}"):
                    st.session_state.all_chats.pop(i)
                    if st.session_state.current_chat_index == i:
                        st.session_state.current_chat_index = None
                        st.session_state.chat_history = []
                    st.session_state.del_confirm_idx = None
                    st.rerun()
            with cc2:
                if st.button("Cancel", key=f"del_no_{i}"):
                    st.session_state.del_confirm_idx = None
                    st.rerun()
            st.sidebar.markdown("---")
else:
    st.sidebar.info("No chat history yet.")

# --- Display current chat & ratings
for idx in range(0, len(st.session_state.chat_history) // 2):
    msg_user = st.session_state.chat_history[idx * 2]
    msg_bot = st.session_state.chat_history[idx * 2 + 1]
    render_chat(msg_user["role"], msg_user["content"])
    render_chat(msg_bot["role"], msg_bot["content"])
    rating_buttons(idx)
    st.markdown("---")

# --- Input form
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.text_input("Type your question here", key="input_text", placeholder="Type your question here...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Send")
    with col3:
        reset = st.form_submit_button("Reset")

if submit and user_input:
    # Cari bagian markdown yang relevan
    relevant_data = search_relevant_parts(user_input, markdown_parts)
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
            + "\n\n".join(relevant_data)
        )
    }
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Answering..."):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[system_prompt] + st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        save_feedback_to_gsheet(user_input, answer, "")
    st.rerun()

# --- Reset conversation
if reset:
    st.session_state.confirm_reset = True
    st.rerun()

if st.session_state.get("confirm_reset", False):
    st.markdown("---")
    st.error("⚠️ Are you sure you want to reset the entire conversation?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes", key="confirm_yes"):
            st.session_state.chat_history = []
            keys_to_delete = [k for k in st.session_state.keys() if k.startswith('rate_')]
            for k in keys_to_delete:
                del st.session_state[k]
            st.session_state.n_like = 0
            st.session_state.n_dislike = 0
            st.session_state.confirm_reset = False
            st.rerun()
    with col2:
        if st.button("Cancel", key="confirm_no"):
            st.session_state.confirm_reset = False
            st.rerun()

# --- Stats
st.markdown(f"### Current Session Stats\n👍 **{st.session_state.n_like}**   👎 **{st.session_state.n_dislike}**")
if st.session_state.stats_history:
    st.markdown("### Stats History")
    for i, stats in enumerate(st.session_state.stats_history, 1):
        st.markdown(f"Session {i}: 👍 {stats['like']} | 👎 {stats['dislike']}")
