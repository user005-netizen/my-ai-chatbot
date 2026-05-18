import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

st.title("My AI Chatbot")
st.write("Powered by LangChain + Groq")

llm = ChatGroq(model="llama-3.3-70b-versatile")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)
    response = llm.invoke(st.session_state.history)
    st.session_state.history.append(AIMessage(content=response.content))
    st.chat_message("assistant").write(response.content)