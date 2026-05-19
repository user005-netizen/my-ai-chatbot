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
    .main { background-color: #f8f9fa; }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main .block-container {
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .stChatMessage {
        border-radius: 15px;
        margin: 5px 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1e3a5f, #2196F3);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #2196F3, #1e3a5f);
        transform: translateY(-2px);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #2196F3 100%);
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .login-box {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        max-width: 400px;
        margin: auto;
        margin-top: 5rem;
    }
</style>
""", unsafe_allow_html=True)

# Login System
USERS = {
    "admin": "jivo123",
    "hr": "hr123",
    "manager": "manager123"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding: 2rem;'>
        <h1 style='color:white; font-size:3rem;'>🛢️ JIVO OIL</h1>
        <h3 style='color:white;'>AI Assistant</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Login")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password!")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; color:white; margin-top:1rem;'>
            <small>Demo: admin / jivo123</small>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# Main App (After Login)
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1rem;'>
        <h2>🛢️ JIVO OIL</h2>
        <p>AI Assistant</p>
        <hr style='border-color:rgba(255,255,255,0.3);'>
        <p>👤 Welcome, <b>{st.session_state.username.upper()}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💬 Chat History")
    if st.session_state.history:
        for i, msg in enumerate(st.session_state.history):
            if isinstance(msg, HumanMessage):
                content = msg.content[:30] + "..." if len(msg.content) > 30 else msg.content
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

# Main Content
st.markdown("""
<div style='text-align:center; padding:1rem 0;'>
    <h1 style='color:#1e3a5f;'>🛢️ JIVO OIL AI Assistant</h1>
    <p style='color:#666;'>Powered by Advanced AI Technology</p>
    <hr>
</div>
""", unsafe_allow_html=True)

# File Upload
with st.expander("📎 Upload File (PDF, CSV, Image, TXT)"):
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "png", "jpg", "jpeg", "txt", "csv"]
    )

file_content = ""
if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8")
        st.success(f"✅ Text file loaded!")
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

# Chat Display
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            content = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🛢️"):
            st.write(msg.content)

# Chat Input
user_input = st.chat_input("Ask me anything about JIVO OIL...")

if user_input:
    lang_map = {"English": "Respond in English.", "Hindi": "Hindi mein jawab do.", "Both": "Respond in both Hindi and English."}
    
    if file_content:
        full_input = f"{lang_map[language]}\n\nFile data:\n{file_content}\n\nUser: {user_input}"
    else:
        full_input = f"{lang_map[language]}\n\nUser: {user_input}"
    
    st.session_state.history.append(HumanMessage(content=full_input))
    
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    
    with st.chat_message("assistant", avatar="🛢️"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)
    
    st.session_state.history.append(AIMessage(content=response.content))
    st.rerun()
