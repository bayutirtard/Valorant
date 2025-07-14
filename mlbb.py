import streamlit as st
from groq import Groq

st.set_page_config(page_title="Chatbot MLBB", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends")

# Inisialisasi klien Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi memori obrolan
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
    ]

# Tampilkan riwayat obrolan (lewati sistem prompt)
for msg in st.session_state.chat_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑 Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# Spacer untuk estetika
st.markdown("<br>", unsafe_allow_html=True)

# Input dan tombol reset di baris yang sama
col1, col2 = st.columns([6, 1])  # kolom input lebih besar dari tombol reset

with col1:
    user_input = st.text_input("💬 Ketik pertanyaan kamu lalu tekan Enter", label_visibility="collapsed")

with col2:
    if st.button("🔁 Reset"):
        st.session_state.chat_history = [
            {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
        ]
        st.rerun()

# Proses saat input diberikan
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    st.rerun()
