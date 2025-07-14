import streamlit as st
from groq import Groq

st.set_page_config(page_title="Chatbot MLBB", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi memori obrolan
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
    ]

# Tombol reset
with st.sidebar:
    if st.button("🔁 Reset Chat"):
        st.session_state.chat_history = [
            {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
        ]
        st.rerun()

# Tampilkan riwayat obrolan
for msg in st.session_state.chat_history[1:]:  # skip system
    if msg["role"] == "user":
        st.markdown(f"**🧑 Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# Kolom input DITEMPATKAN DI BAWAH
user_input = st.text_input("💬 Ketik pertanyaan kamu lalu tekan Enter")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    st.rerun()  # agar input kosong setelah dijawab dan langsung tampil
