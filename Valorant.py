import streamlit as st
from groq import Groq
import csv
import io
from datetime import datetime
import requests
import base64

# === Kirim log ke email admin via Brevo API ===
def send_csv_email_via_brevo(subject, body_text, csv_bytes, to_email, from_email, brevo_api_key):
    encoded_file = base64.b64encode(csv_bytes).decode("utf-8")
    data = {
        "sender": {"name": "Valorant Bot", "email": from_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body_text,
        "attachment": [
            {
                "content": encoded_file,
                "name": "chat_feedback_log.csv"
            }
        ]
    }
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json"
        },
        json=data
    )
    return resp.status_code, resp.text

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
    with col2:
        if st.button("👎", key=f"down_{idx}"):
            st.session_state[f"rate_{idx}"] = "down"
            st.info("Terima kasih atas feedbacknya!")

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

# --- Statistik feedback
n_like = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "up")
n_dislike = sum(1 for k,v in st.session_state.items() if k.startswith('rate_') and v == "down")
st.markdown(f"### Statistik Feedback Sesi Ini:  \n👍 **{n_like}** &nbsp;&nbsp;&nbsp; 👎 **{n_dislike}**")

# --- ADMIN BLOK: KIRIM LOG KE EMAIL (CSV DIBUAT DI MEMORY)
st.markdown("---")
st.subheader("Fitur Admin (Akses Terkunci)")

is_admin = False
admin_code = st.text_input("Kode Admin (hanya untuk admin):", type="password")
if admin_code == st.secrets["ADMIN_CODE"]:
    is_admin = True

def generate_csv_from_session():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "user_question", "bot_answer", "feedback"])
    chat_hist = st.session_state.chat_history[1:]
    for idx in range(0, len(chat_hist)//2):
        user_msg = chat_hist[idx*2]["content"]
        bot_msg = chat_hist[idx*2+1]["content"]
        feedback = st.session_state.get(f"rate_{idx}", "")
        writer.writerow([datetime.now().isoformat(), user_msg, bot_msg, feedback])
    return output.getvalue().encode("utf-8")

if is_admin:
    st.success("Mode admin aktif! Anda bisa kirim log ke email.")
    if st.button("Kirim log ke email admin"):
        csv_bytes = generate_csv_from_session()
        status, resp = send_csv_email_via_brevo(
            subject="Log Chatbot Valorant",
            body_text="Terlampir log chat + feedback terbaru.",
            csv_bytes=csv_bytes,
            to_email=st.secrets["EMAIL_TO"],
            from_email=st.secrets["EMAIL_FROM"],
            brevo_api_key=st.secrets["BREVO_API_KEY"]
        )
        if status == 201:
            st.success("Email terkirim!")
        else:
            st.error(f"Gagal mengirim email: {resp}")
else:
    st.info("Masukkan kode admin untuk akses fitur ini.")
