import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os
import pypdf

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="Komal AI Assistant", page_icon="🤖", layout="wide")

with st.sidebar:
    st.title("Komal AI Assistant")
    st.markdown("---")
    if "history" not in st.session_state:
        st.session_state.history = []
    st.metric("Total Messages", len(st.session_state.history))
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    language = st.selectbox("Language", ["English", "Hindi", "Both"])
    st.markdown("---")
    st.markdown("Made with love by Komal")

st.title("Komal AI Assistant")
st.markdown("Powered by LangChain + Groq AI")
st.markdown("---")

with st.expander("Upload File (PDF, Image, TXT)"):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "txt"])

file_content = ""
if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8")
        st.success("Text file loaded!")
    elif uploaded_file.type in ["image/png", "image/jpeg"]:
        st.image(uploaded_file, width=300)
        file_content = "User uploaded image: " + uploaded_file.name
        st.success("Image loaded!")
    elif uploaded_file.type == "application/pdf":
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            file_content += page.extract_text()
        st.success("PDF loaded!")

llm = ChatGroq(model="llama-3.3-70b-versatile")

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    else:
        with st.chat_message("assistant"):
            st.write(msg.content)

user_input = st.chat_input("Type your message here...")

if user_input:
    if file_content:
        full_input = "File content:\n" + file_content + "\n\nUser: " + user_input
    else:
        full_input = user_input
    st.session_state.history.append(HumanMessage(content=full_input))
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)
    st.session_state.history.append(AIMessage(content=response.content))
