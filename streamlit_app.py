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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, .stApp {
        background-color: #eef1f5 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .main .block-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    }
    [data-testid="stSidebar"] {
        background-color: #f7f9fc !important;
        border-right: 2px solid #dce3ed;
    }
    [data-testid="stSidebar"] * { color: #1a3a5c !important; }
    .stButton > button {
        background: linear-gradient(90deg, #1a3a5c, #2979ff);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(41,121,255,0.3);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1.5px solid #d0d7e3;
        background: #f8fafc;
        padding: 0.6rem 1rem;
    }
    .stChatMessage {
        background: #f4f6fa !important;
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        margin: 6px 0 !important;
    }
    .chat-header {
        background: linear-gradient(90deg, #1a3a5c 0%, #2979ff 100%);
        padding: 1.2rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .history-item {
        background: #e8f0fe;
        border-left: 3px solid #2979ff;
        padding: 6px 10px;
        border-radius: 6px;
        margin: 4px 0;
        font-size: 0.8rem;
    }
    .sidebar-brand {
        background: #ffffff;
        border: 2px solid #dce3ed;
        border-radius: 14px;
        text-align: center;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .user-badge {
        background: #e8f0fe;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 0.5rem 0 1rem 0;
    }

    /* LOGIN PAGE */
    .login-page-bg {
        min-height: 100vh;
        background: linear-gradient(135deg, #0f2044 0%, #1a3a5c 40%, #1565c0 70%, #2979ff 100%);
    }
    .login-card {
        background: white;
        border-radius: 24px;
        padding: 3rem 2.5rem;
        box-shadow: 0 25px 60px rgba(0,0,0,0.25);
    }
    .oil-drop {
        width: 90px;
        height: 90px;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        margin: 0 auto;
        box-shadow: 0 8px 25px rgba(255,107,53,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .oil-drop-inner {
        transform: rotate(45deg);
        font-size: 2.2rem;
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
    <div style='
        position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: -1;
        background: linear-gradient(135deg, #0f2044 0%, #1a3a5c 40%, #1565c0 75%, #2979ff 100%);
    '></div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; margin-bottom:2rem;'>
            <div style='
                width:90px; height:90px;
                background: linear-gradient(135deg, #ff6b35, #f7931e);
                border-radius: 50% 50% 50% 0;
                transform: rotate(-45deg);
                margin: 0 auto 1rem auto;
                box-shadow: 0 8px 30px rgba(255,107,53,0.5);
                display: flex; align-items: center; justify-content: center;
            '>
                <span style='transform:rotate(45deg); font-size:2.5rem;'>🛢️</span>
            </div>
            <h1 style='
                color: white;
                font-size: 2.8rem;
                font-weight: 700;
                margin: 0.5rem 0 0.2rem 0;
                text-shadow: 0 2px 10px rgba(0,0,0,0.3);
                letter-spacing: 3px;
            '>JIVO OIL</h1>
            <p style='
                color: rgba(255,255,255,0.75);
                font-size: 1rem;
                margin: 0;
                letter-spacing: 2px;
                text-transform: uppercase;
            '>AI Assistant Platform</p>
            <div style='
                width: 60px; height: 3px;
                background: linear-gradient(90deg, #ff6b35, #f7931e);
                margin: 1rem auto;
                border-radius: 2px;
            '></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='
            background: white;
            border-radius: 20px;
            padding: 2.5rem 2rem;
            box-shadow: 0 25px 60px rgba(0,0,0,0.3);
        '>
            <h3 style='color:#1a3a5c; margin:0 0 0.3rem 0; font-weight:600;'>Welcome Back</h3>
            <p style='color:#64748b; margin:0 0 1.5rem 0; font-size:0.9rem;'>Sign in to your account</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            username = st.text_input("Username", placeholder="Enter your username", key="lu",
                                     label_visibility="collapsed")
            st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="lp",
                                     label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

        st.markdown("""
        <div style='text-align:center; margin-top:1.5rem;'>
            <p style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>
                🔒 Secured access · JIVO OIL Internal Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("""
    <div class='sidebar-brand'>
        <div style='font-size:2rem;'>🛢️</div>
        <h3 style='margin:0.3rem 0; color:#1a3a5c; font-weight:700;'>JIVO OIL</h3>
        <p style='margin:0; font-size:0.8rem; color:#64748b; letter-spacing:1px;'>AI ASSISTANT</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='user-badge'>
        <p style='margin:0; font-size:0.9rem; color:#1a3a5c;'>
            👤 Logged in as <b>{st.session_state.username.upper()}</b>
        </p>
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

    st.markdown("<hr style='border:1px solid #dce3ed;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    with c2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.history = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    language = st.selectbox("🌐 Language", ["English", "Hindi", "Both"])

st.markdown("""
<div class='chat-header'>
    <h2 style='margin:0; color:white; font-weight:700;'>🛢️ JIVO OIL AI Assistant</h2>
    <p style='margin:0.3rem 0 0; opacity:0.85; color:white; font-size:0.9rem;'>
        Your intelligent company assistant — employees, hierarchy and more
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
        st.success("✅ PDF ready — " + str(len(reader.pages)) + " pages")
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_content = df.head(80).to_string(index=False)
        st.dataframe(df.head(8), use_container_width=True)
        st.success("✅ CSV ready — " + str(len(df)) + " records")
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        file_content = df.head(80).to_string(index=False)
        st.dataframe(df.head(8), use_container_width=True)
        st.success("✅ Excel ready — " + str(len(df)) + " records")

llm = ChatGroq(model="llama-3.3-70b-versatile")

system_prompt = "You are JIVO OIL AI Assistant. Help with employee data, hierarchy, HR reports, and any uploaded company files. Always analyze uploaded data and answer questions about it. Be professional and helpful."

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
        full_input = system_prompt + "\n" + lang_map[language] + "\n\nFile data:\n" + file_content + "\n\nUser: " + user_input
    else:
        full_input = system_prompt + "\n" + lang_map[language] + "\n\nUser: " + user_input

    st.session_state.history.append(HumanMessage(content=full_input))
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    with st.chat_message("assistant", avatar="🛢️"):
        with st.spinner("Processing..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)
    st.session_state.history.append(AIMessage(content=response.content))
    st.rerun()
