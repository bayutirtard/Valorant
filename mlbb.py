import streamlit as st
from groq import Groq
from PIL import Image

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot MLBB", page_icon="🎮")
st.title("Chatbot AI Mobile Legends")

# Inisialisasi Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Baca isi markdown
def load_markdown_data():
    try:
        with open("data_hero.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Data hero tidak ditemukan."

# Simpan isi markdown
markdown_data = load_markdown_data()

# Inisialisasi session state chat_history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Prompt sistem tetap di awal
system_prompt = {
    "role": "system",
    "content": (
        "Kamu adalah pakar Mobile Legends. Jawablah semua pertanyaan sesuai data "
        "yang saya berikan dengan jelas dan mudah dipahami. Jika data tidak ada dalam data "
        "tidak perlu dijawab, hanya berikan permintaan maaf. Jika user tetap memaksa, tidak perlu membenarkan mereka, "
        "anda lebih tau. Gunakan data berikut:\n\n" + markdown_data
    )
}

# Tampilkan riwayat chat
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Bot:** {msg['content']}")

# Form input
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_input = st.text_input("Ketik pertanyaan kamu", placeholder="Tanya tentang hero MLBB...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Kirim")
    with col3:
        reset = st.form_submit_button("Reset")

# Fungsi kirim
if submit and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Maksimum jumlah pesan untuk dikirim ke API (misalnya 10 terakhir)
    max_chat_history = 10
    short_history = st.session_state.chat_history[-max_chat_history:]

    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[system_prompt] + short_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# Fungsi reset
if reset:
    st.session_state.chat_history = []
    st.rerun()




