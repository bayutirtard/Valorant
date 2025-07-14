import streamlit as st
from groq import Groq

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot MLBB", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends")

# Inisialisasi klien Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
    ]

# Tampilkan riwayat chat (skip system message)
for msg in st.session_state.chat_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑 Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# Spacer sebelum input
st.markdown("<br>", unsafe_allow_html=True)

# Kolom input dan tombol reset dalam satu baris
col1, col2 = st.columns([6, 1])
previous_length = len(st.session_state.chat_history)  # Simpan panjang sebelumnya

# Input pengguna
with col1:
    user_input = st.text_input("💬 Ketik pertanyaan kamu lalu tekan Enter", label_visibility="collapsed")

# Tombol reset
with col2:
    if st.button("🔁 Reset"):
        st.session_state.chat_history = [
            {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
        ]
        st.rerun()

# Jika ada input baru (Enter ditekan), dan bukan karena rerun/reset
if user_input and len(st.session_state.chat_history) == previous_length:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    st.rerun()
