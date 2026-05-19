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
    html, body, .stApp {
        background-color: #f0f2f5 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .main .block-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.07);
        margin-top: 1rem;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1.5px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] label { color: #1a3a5c !important; }
    .stButton > button {
        background: linear-gradient(90deg, #1a3a5c, #2979ff);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(41,121,255,0.25);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1.5px solid #d0d7e3;
        padding: 0.6rem 1rem;
        background: #f8fafc;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2979ff;
        box-shadow: 0 0 0 3px rgba(41,121,255,0.12);
    }
    .stChatMessage {
        background: #f8fafc !important;
        border-radius: 14px !important;
        border: 1px solid #e8edf4 !important;
        margin: 6px 0 !important;
    }
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1.5px solid #d0d7e3;
        background: #f8fafc;
    }
    .login-wrapper {
        min-height: 100vh;
        background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 50%, #e8f5e9 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    .login-card {
        background: white;
        padding: 3rem 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        width: 100%;
        max-width: 400px;
    }
    .chat-header {
        background: linear-gradient(90deg, #1a3a5c 0%, #2979ff 100%);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .sidebar-logo {
        background: linear-gradient(135deg, #1a3a5c, #2979ff);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .history-item {
        background: #f0f4ff;
        border-left: 3px solid #2979ff;
        padding: 6px 10px;
        border-radius: 6px;
        margin: 4px 0;
        font-size: 0.8rem;
        color: #1a3a5c !important;
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
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:2rem;'>
            <div style='font-size:3.5rem;'>🛢️</div>
            <h1 style='color:#1a3a5c; margin:0.3rem 0; font-size:2.2rem;'>JIVO OIL</h1>
            <p style='color:#64748b; margin:0; font-size:1rem;'>AI Assistant Platform</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div style='background:white; padding:2.5rem; border-radius:20px; 
                        box-shadow:0 8px 40px rgba(0,0,0,0.12);'>
            """, unsafe_allow_html=True)
            st.markdown("#### 🔐 Secure Login")
            st.markdown("<hr style='border:1px solid #e2e8f0; margin:0.8rem 0;'>", unsafe_allow_html=True)
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Login", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div class='sidebar-logo'>
        <div style='font-size:2rem;'>🛢️</div>
        <h3 style='margin:0.3rem 0; color:white;'>JIVO OIL</h3>
        <p style='margin:0; font-size:0.85rem; opacity:0.85; color:white;'>AI Assistant</p>
    </div>
    <div style='background:#f0f4ff; border-radius:10px; padding:10px 14px; margin:0.8rem 0;'>
        <p style='margin:0; font-size:0.9rem;'>👤 Logged in as <b>{st.session_state.username.upper()}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**💬 Recent Chats**")
    if st.session_state.history:
        shown = 0
        for msg in st.session_state.history:
            if isinstance(msg, HumanMessage) and shown < 6:
                raw = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
                preview = raw[:38] + "..." if len(raw) > 38 else raw
                st.markdown(f"<div class='history-item'>🗨️ {preview}</div>", unsafe_allow_html=True)
                shown += 1
    else:
        st.markdown("<small style='color:#94a3b8;'>No chats yet</small>", unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #e2e8f0;'>", unsafe_allow_html=True)

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

    st.markdown("<br>", unsafe_allow_html=True)
    language = st.selectbox("🌐 Language", ["English", "Hindi", "Both"])

# Main Area
st.markdown("""
<div class='chat-header'>
    <h2 style='margin:0; color:white;'>🛢️ JIVO OIL AI Assistant</h2>
    <p style='margin:0.3rem 0 0; opacity:0.88; color:white; font-size:0.9rem;'>
        Your intelligent company assistant — employees, hierarchy & more
    </p>
</div>
""", unsafe_allow_html=True)

with st.expander("📎 Attach File (PDF, CSV, Excel, Image, TXT)"):
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "txt", "csv", "xlsx"])

file_content = ""
if uploaded_file:
    if uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode("utf-8")
        st.success("✅ Text file ready!")
    elif uploaded_file.type in ["image/png", "image/jpeg"]:
        st.image(uploaded_file, width=280)
        file_content = "User uploaded image: " + uploaded_file.name
        st.success("✅ Image ready!")
    elif uploaded_file.type == "application/pdf":
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            file_content += page.extract_text()
        st.success(f"✅ PDF ready — {len(reader.pages)} pages")
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_content = df.to_string(index=False)
        st.dataframe(df.head(8), use_container_width=True)
        st.success(f"✅ CSV ready — {len(df)} records")
    elifelif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        file_content = df.head(80).to_string(index=False)
        st.dataframe(df.head(8), use_container_width=True)
        st.success(f"✅ Excel ready — {len(df)} records")

llm = ChatGroq(model="llama-3.3-70b-versatile")

system_prompt = """You are JIVO OIL AI Assistant — a professional corporate AI for JIVO OIL company. You help with employee data, hierarchy, HR reports, and any uploaded company files. Always analyze uploaded data and answer questions about it. Be professional and helpful."""

STRICT RULES:
- ONLY answer questions about JIVO OIL: its employees, hierarchy, departments, products, edible oils, operations, HR data, and company matters.
- If asked anything unrelated to JIVO OIL, reply: "I can only assist with JIVO OIL related queries. Please ask about our company, employees, or products."
- Use uploaded file data when available to give accurate answers.
- Be professional, concise, and helpful."""

lang_map = {
    "English": "Respond in English only.",
    "Hindi": "Sirf Hindi mein jawab do.",
    "Both": "Respond in both Hindi and English."
}

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            display = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(display)
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
        with st.spinner("Processing..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)
    st.session_state.history.append(AIMessage(content=response.content))
    st.rerun()
