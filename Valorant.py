import streamlit as st
from groq import Groq

# --- Streamlit config & title
st.set_page_config(page_title="Chatbot Valorant", page_icon="🎮")
st.title("Chatbot Valorant")

# --- Init Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Load markdown (asli atau dummy dulu)
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

# --- Fungsi Copy ke Clipboard
def copy_and_rating_buttons(text, idx):
    col1, col2, col3 = st.columns([0.1, 0.1, 0.1])
    with col1:
        st.components.v1.html(f"""
        <button id="copyBtn{idx}" style="
            margin-top:2px;
            margin-bottom:2px;
            padding:5px 18px;
            border-radius:8px;
            border:none;
            background:#262730;
            color:#FFD700;
            font-weight:bold;
            font-size:14px;
            box-shadow:0 2px 8px #0002;
            cursor:pointer;">
            📋
        </button>
        <span id="copiedMsg{idx}" style="color:#32CD32; margin-left:8px; display:none; font-size:14px;">Copied!</span>
        <script>
        const btn = document.getElementById('copyBtn{idx}');
        const msg = document.getElementById('copiedMsg{idx}');
        if(btn) {{
            btn.onclick = function() {{
                navigator.clipboard.writeText(`{text.replace("`", "\\`")}`);
                if(msg) {{
                    msg.style.display = "inline";
                    setTimeout(function(){{msg.style.display="none"}}, 1200);
                }}
            }};
        }}
        </script>
        """, height=38)
    with col2:
        if st.button("👍", key=f"up_{idx}"):
            st.session_state[f"rate_{idx}"] = "up"
            st.success("Terima kasih atas ratingnya!")
    with col3:
        if st.button("👎", key=f"down_{idx}"):
            st.session_state[f"rate_{idx}"] = "down"
            st.info("Terima kasih atas feedbacknya!")

# --- Render chat (sama seperti sebelumnya)
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
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# --- Reset chat
if reset:
    st.session_state.chat_history = [system_prompt]
    st.rerun()

# --- Tampilkan chat + fitur Copy & Rating (untuk setiap jawaban bot)
for idx, msg in enumerate(st.session_state.chat_history[1:]):  # skip system prompt
    render_chat(msg["role"], msg["content"])
    if msg["role"] == "assistant":
        copy_and_rating_buttons(msg.get("raw_markdown", msg["content"]), idx)
    st.markdown("---")



























