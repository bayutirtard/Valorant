import streamlit as st
from groq import Groq

# --- Streamlit config & title
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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [system_prompt]

# ---- Fungsi Copy Button (HTML/JS tetap stylish)
def copy_to_clipboard_button(text, idx):
    st.components.v1.html(f"""
    <button id="copyBtn{idx}" style="
        margin:2px 8px 2px 0;
        padding:5px 14px;
        border-radius:7px;
        border:1.5px solid #FFD700;
        background:#393a41;
        color:#FFD700;
        font-weight:bold;
        font-size:14px;
        box-shadow:0 2px 8px #0002;
        cursor:pointer;">
        📋
    </button>
    <span id="copiedMsg{idx}" style="color:#32CD32; margin-left:7px; display:none; font-size:13px;">Copied!</span>
    <script>
    const btn = document.getElementById('copyBtn{idx}');
    const msg = document.getElementById('copiedMsg{idx}');
    if(btn) {{
        btn.onclick = function() {{
            navigator.clipboard.writeText(`{text.replace("`", "\\`")}`);
            if(msg) {{
                msg.style.display = "inline";
                setTimeout(function(){{msg.style.display="none"}}, 1000);
            }}
        }};
    }}
    </script>
    """, height=36)

# ---- Fungsi Streamlit Rating Button
def rating_buttons(idx):
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("👍", key=f"up_{idx}"):
            st.session_state[f"rate_{idx}"] = "up"
            st.success("Terima kasih atas ratingnya!")
    with col2:
        if st.button("👎", key=f"down_{idx}"):
            st.session_state[f"rate_{idx}"] = "down"
            st.info("Terima kasih atas feedbacknya!")

# ---- Render chat
def render_chat(role, content):
    if role == "user":
        st.markdown(f"**You:** {content}")
    elif role == "assistant":
        st.markdown("**Bot:**")
        st.markdown(content)

# --- Form input chat
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

# --- Proses kirim chat
if submit and st.session_state.get("input_text", ""):
    user_input = st.session_state["input_text"]
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.spinner("Answering..."):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        # raw_markdown untuk copy
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "raw_markdown": answer
        })
    st.rerun()

# --- Reset chat
if reset:
    st.session_state.chat_history = [system_prompt]
    st.rerun()

# --- Tampilkan chat + tombol Copy/Like/Dislike
for idx, msg in enumerate(st.session_state.chat_history[1:]):  # skip system prompt
    render_chat(msg["role"], msg["content"])
    if msg["role"] == "assistant":
        col1, col2 = st.columns([2, 3])
        with col1:
            copy_to_clipboard_button(msg.get("raw_markdown", msg["content"]), idx)
        with col2:
            rating_buttons(idx)
    st.markdown("---")

# ---- Statistik total Like/Dislike
n_like = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "up")
n_dislike = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "down")
st.markdown(f"### Statistik Feedback Sesi Ini:  \n👍 **{n_like}** &nbsp;&nbsp;&nbsp; 👎 **{n_dislike}**")



