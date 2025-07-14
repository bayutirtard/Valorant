import streamlit as st
from groq import Groq

# Konfigurasi halaman
st.set_page_config(page_title="Chatbot MLBB", page_icon="🎮")
st.title("Chatbot AI Mobile Legends")

# Inisialisasi klien Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inisialisasi riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
    ]

# Tampilkan riwayat obrolan
for msg in st.session_state.chat_history[1:]:  # skip system
    if msg["role"] == "user":
        st.markdown(f"**Kamu:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**Bot:** {msg['content']}")

# Spacer sebelum input
st.markdown("<br>", unsafe_allow_html=True)

# Form input dan tombol
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        user_input = st.text_input(
    label="Ketik pertanyaan kamu", 
    placeholder="Ketik pertanyaan kamu...", 
    label_visibility="collapsed"
        )

    with col2:
        submit = st.form_submit_button("Kirim")
    
    with col3:
        reset = st.form_submit_button("Reset")

# Jika submit ditekan dan ada input
if submit and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=st.session_state.chat_history
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    st.rerun()

# Jika reset ditekan
if reset:
    st.session_state.chat_history = [
        {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawablah dengan jelas dan mudah dipahami."}
    ]
    st.rerun()
