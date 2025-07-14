import streamlit as st
from groq import Groq

# API Key dari secrets.toml atau bisa hardcode untuk uji coba
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="MLBB Chatbot AI Gratis", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends (Gratis via Groq LLaMA3)")

st.markdown("Tanyakan apa saja tentang hero, counter, meta, atau build di Mobile Legends!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ketik pertanyaan kamu di sini 👇")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("Menjawab..."):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Kamu adalah pakar Mobile Legends. Jawab pertanyaan user dengan bahasa yang mudah dipahami, jelas, dan relevan."}
            ] + st.session_state.chat_history,
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

st.markdown("---")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**👤 Kamu:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {msg['content']}")
