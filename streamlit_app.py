import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os
import pypdf
import pandas as pd

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.set_page_config(
    page_title="JIVO OIL AI Assistant",
    page_icon="🛢️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #e8f5e9 100%);
    }
    .main .block-container {
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1565c0 0%, #0d47a1 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton > button {
        background: linear-gradient(90deg, #1565c0, #42a5f5);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(21,101,192,0.4);
    }
    .login-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        max-width: 420px;
        margin: auto;
    }
    .chat-header {
        background: linear-gradient(90deg, #1565c0, #42a5f5);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

USERS = {"aiuser": "ai@1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = []

if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding:2rem 0;'>
       <div style='text-align:center; padding:2rem 0; background: #f5f7fa;'>
        <p style='color:#555; font-size:1.2rem;'>AI Assistant Platform</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Secure Login")
        st.markdown("---")
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Login", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials! Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1rem;'>
        <h2>🛢️ JIVO OIL</h2>
        <p style='font-size:0.9rem;'>AI Assistant</p>
        <hr style='border-color:rgba(255,255,255,0.3);'>
        <p>👤 <b>{st.session_state.username.upper()}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💬 Chat History")
    if st.session_state.history:
        for msg in st.session_state.history:
            if isinstance(msg, HumanMessage):
                content = msg.content.split("User: ")[-1][:35] + "..."
                st.markdown(f"<small>🗨️ {content}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small>No messages yet</small>", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.history = []
            st.rerun()

    language = st.selectbox("🌐 Language", ["English", "Hindi", "Both"])

# Main
st.markdown("""
<div class='chat-header'>
    <h2>🛢️ JIVO OIL AI Assistant</h2>
    <p style='margin:0; opacity:0.9;'>Your intelligent company assistant</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📎 Upload File (PDF, CSV, Image, TXT)"):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "txt", "csv"])

file_content = ""
if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8")
        st.success("✅ Text file loaded!")
    elif uploaded_file.type in ["image/png", "image/jpeg"]:
        st.image(uploaded_file, width=300)
        file_content = "User uploaded image: " + uploaded_file.name
        st.success("✅ Image loaded!")
    elif uploaded_file.type == "application/pdf":
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            file_content += page.extract_text()
        st.success(f"✅ PDF loaded: {len(reader.pages)} pages")
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_content = df.to_string(index=False)
        st.dataframe(df.head(10))
        st.success(f"✅ CSV loaded: {len(df)} rows")

llm = ChatGroq(model="llama-3.3-70b-versatile")

system_prompt = """You are JIVO OIL AI Assistant - a professional corporate AI.
STRICT RULES:
- ONLY answer questions related to JIVO OIL company, its employees, hierarchy, products, operations, and HR matters.
- If someone asks anything NOT related to JIVO OIL, respond: 'I can only assist with JIVO OIL related queries. Please ask about our company, employees, or operations.'
- Be professional, helpful and concise.
- If file data is provided, use it to answer questions accurately."""

lang_map = {
    "English": "Respond in English only.",
    "Hindi": "Sirf Hindi mein jawab do.",
    "Both": "Respond in both Hindi and English."
}

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            content = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🛢️"):
            st.write(msg.content)

user_input = st.chat_input("Ask about JIVO OIL employees, hierarchy, products...")

if user_input:
    if file_content:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nFile data:\n{file_content}\n\nUser: {user_input}"
    else:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nUser: {user_input}"

    st.session_state.history.append(HumanMessage(content=full_input))
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    with st.chat_message("assistant", avatar="🛢️"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)
    st.session_state.history.append(AIMessage(content=response.content))
    st.rerun()
