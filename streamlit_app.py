import streamlit as st
from supabase import create_client
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os
import pypdf
import pandas as pd

# Config
SUPABASE_URL = "https://icfcetgzwumpdcfzahcx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImljZmNldGd6d3VtcGRjZnphaGN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyNTA5MzUsImV4cCI6MjA5NDgyNjkzNX0.KIBajkD_sQ-fq_Rwe4_zy86pEWHozXiMM6bydZ9jPDg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="JIVO Wellness AI", page_icon="🌿", layout="wide")

st.markdown("""
<style>
st.markdown("""
<style>
.stApp { background: #f9fafb; }
.main .block-container {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border: 1px solid #e8f5e9;
}
[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #e8f5e9;
}
[data-testid="stSidebar"] * { color: #1b5e20 !important; }
.stButton > button {
    background: white !important;
    color: #2e7d32 !important;
    border: 1.5px solid #2e7d32 !important;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #2e7d32 !important;
    color: white !important;
}
.stTextInput > div > input, .stSelectbox > div {
    border-color: #c8e6c9 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)
</style>
""", unsafe_allow_html=True)

# Session state init
for key in ["logged_in", "user_id", "user_email", "access_token", "history"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "history" else None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def load_chat_history(user_id):
    try:
        res = supabase.table("chat_history").select("*").eq("user_id", user_id).order("created_at").execute()
        history = []
        for row in res.data:
            if row["role"] == "user":
                history.append(HumanMessage(content=row["content"]))
            else:
                history.append(AIMessage(content=row["content"]))
        return history
    except:
        return []

def save_message(user_id, role, content):
    try:
        supabase.table("chat_history").insert({
            "user_id": user_id,
            "role": role,
            "content": content
        }).execute()
    except:
        pass

def load_products():
    try:
        res = supabase.table("products").select("*").order("category").execute()
        return res.data
    except:
        return []

# ── LOGIN / SIGNUP PAGE ──────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding:2rem 0;'>
        <h1 style='color:#1b5e20; font-size:3rem;'>🌿 JIVO Wellness</h1>
        <p style='color:#555; font-size:1.1rem;'>AI Assistant — Purity For Charity</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            st.markdown("### Welcome back!")
            email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            if st.button("Login", use_container_width=True, key="login_btn"):
                if email and password:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.logged_in = True
                        st.session_state.user_id = res.user.id
                        st.session_state.user_email = res.user.email
                        st.session_state.access_token = res.session.access_token
                        st.session_state.history = load_chat_history(res.user.id)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")
                else:
                    st.warning("Please fill in all fields!")

        with tab2:
            st.markdown("### Create account")
            new_email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Min 6 characters")
            new_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2", placeholder="Repeat password")
            if st.button("Sign Up", use_container_width=True, key="signup_btn"):
                if new_email and new_pass and new_pass2:
                    if new_pass != new_pass2:
                        st.error("Passwords do not match!")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters!")
                    else:
                        try:
                            res = supabase.auth.sign_up({"email": new_email, "password": new_pass})
                            st.success("Account created! Please check your email to verify your account, then login.")
                        except Exception as e:
                            st.error(f"Signup failed: {str(e)}")
                else:
                    st.warning("Please fill in all fields!")
    st.stop()

# ── MAIN APP (after login) ────────────────────────────────────────────
llm = ChatGroq(model="llama-3.3-70b-versatile")
products = load_products()

products_text = ""
for p in products:
    products_text += f"- {p['name']}: Rs.{p['price']} — {p['description']} (Category: {p['category']})\n"

system_prompt = f"""You are JIVO Wellness AI Assistant — a professional corporate AI for JIVO Wellness company.

COMPANY KNOWLEDGE BASE:
=== ABOUT JIVO ===
- Full Name: JIVO Wellness | Tagline: Purity For Charity
- India's Largest Seller of Cold Press Canola Oil
- India's First Patented Wheatgrass Products
- 15+ years in wellness | ISO & Sedex Certified
- Address: J3/190, Nehru Market, Rajouri Garden, New Delhi 110027
- Email: Info@jivo.in | Toll Free: 1800 137 4433
- Shop: shop.jivo.in

=== LIVE PRODUCT PRICES ===
{products_text}

=== CSR ===
- 40,000+ meals during COVID-19
- Free Oxygen Concentrators to patients
- 70,000+ children nourished
- Rural school construction

STRICT RULES:
- ONLY answer questions related to JIVO Wellness, its products, prices, employees, and operations.
- For product/price queries use the LIVE PRODUCT PRICES above.
- Always mention shop.jivo.in for purchases.
- If unrelated question asked, say: I can only assist with JIVO Wellness related queries.
- Be professional, warm and helpful."""

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1rem 0;'>
        <h2>🌿 JIVO Wellness</h2>
        <p style='font-size:0.85rem; opacity:0.8;'>AI Assistant</p>
        <hr style='border-color:rgba(255,255,255,0.2);'>
        <p style='font-size:0.85rem;'>Logged in as:<br><b>{st.session_state.user_email}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💬 Chat History")
    if st.session_state.history:
        for msg in st.session_state.history:
            if isinstance(msg, HumanMessage):
                preview = msg.content[:35] + "..." if len(msg.content) > 35 else msg.content
                st.markdown(f"<small>🗨️ {preview}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small>No messages yet</small>", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            supabase.table("chat_history").delete().eq("user_id", st.session_state.user_id).execute()
            st.session_state.history = []
            st.rerun()
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            supabase.auth.sign_out()
            for key in ["logged_in", "user_id", "user_email", "access_token", "history"]:
                st.session_state[key] = [] if key == "history" else None
            st.session_state.logged_in = False
            st.rerun()

    language = st.selectbox("🌐 Language", ["English", "Hindi", "Both"])

    st.markdown("---")
    st.markdown("### 🛍️ Our Products")
    for p in products:
        st.markdown(f"<small><b>{p['name']}</b><br>Rs. {p['price']}</small>", unsafe_allow_html=True)
        st.markdown("---")

# Main area
st.markdown("""
<div style='text-align:center; background:linear-gradient(90deg,#1b5e20,#2e7d32); color:white; padding:1.2rem; border-radius:15px; margin-bottom:1.5rem;'>
    <h2 style='margin:0;'>🌿 JIVO Wellness AI Assistant</h2>
    <p style='margin:0; opacity:0.85; font-size:0.9rem;'>Powered by Advanced AI — Purity For Charity</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📎 Upload File (PDF, CSV, Image, TXT)"):
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "txt", "csv"])

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
        st.success(f"PDF loaded: {len(reader.pages)} pages")
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        file_content = df.to_string(index=False)
        st.dataframe(df.head(10))
        st.success(f"CSV loaded: {len(df)} rows")

lang_map = {
    "English": "Respond in English only.",
    "Hindi": "Sirf Hindi mein jawab do.",
    "Both": "Respond in both Hindi and English."
}

# Display chat history
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            content = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🌿"):
            st.write(msg.content)

# Chat input
user_input = st.chat_input("Ask about JIVO products, prices, wellness tips...")

if user_input:
    if file_content:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nFile data:\n{file_content}\n\nUser: {user_input}"
    else:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nUser: {user_input}"

    st.session_state.history.append(HumanMessage(content=full_input))
    save_message(st.session_state.user_id, "user", user_input)

    with st.chat_message("user", avatar="👤"):
        st.write(user_input)

    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)

    st.session_state.history.append(AIMessage(content=response.content))
    save_message(st.session_state.user_id, "assistant", response.content)
    st.rerun()
