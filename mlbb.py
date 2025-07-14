import streamlit as st
from groq import Groq

# Setup API key
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Chatbot MLBB Gratis", page_icon="🎮")
st.title("🤖 Chatbot AI Mobile Legends (Gratis via Mistral)")

st.markdown("Tanyakan apa saja tentang hero, build, counter, meta, dan strategi MLBB!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ketik pertanyaan kamu di sini 👇")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("Sedang menjawab..."):
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "Kamu adalah pakar Mobile Legends Bang Bang. Jawablah pertanyaan user secara jelas dan akurat."}
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
