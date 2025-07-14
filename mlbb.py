import streamlit as st
from groq import Groq

# Konfigurasi Streamlit
st.set_page_config(page_title="Chatbot MLBB AI Gratis", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends")
st.markdown("Tanyakan apa saja tentang hero, counter, build, dan strategi MLBB!")

# Inisialisasi Groq API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi memori obrolan
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah pertanyaan user secara relevan dan ramah. Gunakan bahasa yang mudah dimengerti."}
    ]

# Input dari user
user_input = st.text_input("📨 Ketik pertanyaan kamu:")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("🤖 Bot sedang mengetik..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

# Tombol reset
if st.button("🔁 Reset Chat"):
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah pertanyaan user secara relevan dan ramah. Gunakan bahasa yang mudah dimengerti."}
    ]
    st.rerun()


# Tampilkan riwayat obrolan (tanpa system message)
for msg in st.session_state.chat_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑 Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")
