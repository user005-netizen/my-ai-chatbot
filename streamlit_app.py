import streamlit as st
from supabase import create_client
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os
import pypdf
import pandas as pd

SUPABASE_URL = "https://icfcetgzwumpdcfzahcx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImljZmNldGd6d3VtcGRjZnphaGN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyNTA5MzUsImV4cCI6MjA5NDgyNjkzNX0.KIBajkD_sQ-fq_Rwe4_zy86pEWHozXiMM6bydZ9jPDg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="JIVO Wellness AI", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp { background: #f0f7f0; }

.main .block-container {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 2px 20px rgba(46,125,50,0.08);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3c1a 0%, #2d5a2d 100%) !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #c8e6c9 !important; }

.stButton > button {
    background: transparent !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: white !important;
}

.product-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    border: 1px solid #c8e6c9;
    border-left: 4px solid #2e7d32;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}
.product-card:hover {
    background: linear-gradient(135deg, #e8f5e9, #dcedc8);
    transform: translateX(3px);
    box-shadow: 0 2px 8px rgba(46,125,50,0.2);
}
.product-name {
    font-weight: 600;
    font-size: 0.82rem;
    color: #1b5e20;
    margin-bottom: 2px;
}
.product-price {
    font-size: 0.9rem;
    font-weight: 700;
    color: #2e7d32;
}
.product-cat {
    font-size: 0.7rem;
    color: #66bb6a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stChatMessage {
    background: #f9fdf9 !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.3) !important;
    color: white !important;
    border-radius: 8px !important;
}

div[data-testid="stExpander"] {
    background: #f9fdf9;
    border: 1px solid #c8e6c9;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

for key in ["logged_in", "user_id", "user_email", "access_token", "history", "selected_product"]:
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

if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding:3rem 0 1rem 0;'>
        <div style='display:inline-block; background:linear-gradient(135deg,#1b5e20,#2e7d32);
        padding:16px 32px; border-radius:16px; margin-bottom:1.5rem;'>
            <h1 style='color:white; margin:0; font-size:2rem; font-weight:700; letter-spacing:2px;'>JIVO WELLNESS</h1>
            <p style='color:#a5d6a7; margin:4px 0 0 0; font-size:0.9rem; letter-spacing:1px;'>PURITY FOR CHARITY</p>
        </div>
        <p style='color:#555; font-size:1rem;'>Your Personal Wellness AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            email = st.text_input("Email Address", key="login_email", placeholder="your@email.com")
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
            new_email = st.text_input("Email Address", key="signup_email", placeholder="your@email.com")
            new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Min 6 characters")
            new_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2", placeholder="Repeat password")
            if st.button("Create Account", use_container_width=True, key="signup_btn"):
                if new_email and new_pass and new_pass2:
                    if new_pass != new_pass2:
                        st.error("Passwords do not match!")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters!")
                    else:
                        try:
                            res = supabase.auth.sign_up({"email": new_email, "password": new_pass})
                            st.success("Account created! Check your email to verify, then login.")
                        except Exception as e:
                            st.error(f"Signup failed: {str(e)}")
                else:
                    st.warning("Please fill in all fields!")
    st.stop()

llm = ChatGroq(model="llama-3.3-70b-versatile")
products = load_products()

products_text = ""
for p in products:
    products_text += f"- {p['name']}: Rs.{p['price']} - {p['description']} (Category: {p['category']})\n"

system_prompt = f"""You are JIVO Wellness AI Assistant - a professional corporate AI for JIVO Wellness company.

COMPANY KNOWLEDGE BASE:
=== ABOUT JIVO ===
- Full Name: JIVO Wellness | Tagline: Purity For Charity
- India's Largest Seller of Cold Press Canola Oil
- India's First Patented Wheatgrass Products
- 15+ years in wellness | ISO and Sedex Certified
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

with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:1.5rem 0 1rem 0;'>
        <div style='background:rgba(255,255,255,0.1); border-radius:12px; padding:12px; margin-bottom:12px;'>
            <div style='font-size:1.3rem; font-weight:700; letter-spacing:2px; color:white;'>JIVO WELLNESS</div>
            <div style='font-size:0.7rem; color:#a5d6a7; letter-spacing:1px;'>PURITY FOR CHARITY</div>
        </div>
        <div style='font-size:0.75rem; color:#a5d6a7;'>Logged in as</div>
        <div style='font-size:0.85rem; font-weight:600; color:white;'>{st.session_state.user_email}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            supabase.table("chat_history").delete().eq("user_id", st.session_state.user_id).execute()
            st.session_state.history = []
            st.rerun()
    with col2:
        if st.button("Logout", use_container_width=True):
            supabase.auth.sign_out()
            for key in ["logged_in", "user_id", "user_email", "access_token", "history"]:
                st.session_state[key] = [] if key == "history" else None
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    language = st.selectbox("Language", ["English", "Hindi", "Both"])

    st.markdown("""
    <div style='margin-top:16px; margin-bottom:8px; font-size:0.8rem; font-weight:600;
    color:#a5d6a7; text-transform:uppercase; letter-spacing:1px;'>Our Products</div>
    """, unsafe_allow_html=True)

    category_icons = {
        "Edible Oil": "🫙",
        "Olive Oil": "🫒",
        "Ghee": "🥛",
        "Health Drinks": "🥤",
        "Nutraceuticals": "💊",
        "Seeds": "🌱",
        "Beverages": "☕",
        "Honey": "🍯",
        "Snacks": "🥜"
    }

    for p in products:
        icon = category_icons.get(p['category'], "🌿")
        if st.button(f"{icon} {p['name']} - Rs.{p['price']}", key=f"prod_{p['id']}", use_container_width=True):
            st.session_state.selected_product = p['name']
            st.rerun()

# Main area
st.markdown("""
<div style='background:linear-gradient(135deg, #1b5e20, #2e7d32);
border-radius:16px; padding:1.5rem 2rem; margin-bottom:1.5rem;
display:flex; align-items:center; justify-content:space-between;'>
    <div>
        <div style='font-size:1.4rem; font-weight:700; color:white; letter-spacing:1px;'>JIVO Wellness AI Assistant</div>
        <div style='font-size:0.85rem; color:#a5d6a7; margin-top:4px;'>Powered by Advanced AI - Purity For Charity</div>
    </div>
    <div style='text-align:right;'>
        <div style='font-size:0.75rem; color:#a5d6a7;'>India No.1</div>
        <div style='font-size:0.8rem; color:white; font-weight:500;'>Cold Press Canola Oil</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.selected_product:
    product_name = st.session_state.selected_product
    matched = [p for p in products if p['name'] == product_name]
    if matched:
        p = matched[0]
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border:1.5px solid #a5d6a7;
        border-left:5px solid #2e7d32; border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:1rem;'>
            <div style='font-size:1rem; font-weight:700; color:#1b5e20; margin-bottom:6px;'>{p['name']}</div>
            <div style='font-size:1.3rem; font-weight:800; color:#2e7d32; margin-bottom:6px;'>Rs. {p['price']}</div>
            <div style='font-size:0.85rem; color:#555; margin-bottom:4px;'>{p['description']}</div>
            <div style='font-size:0.75rem; color:#66bb6a; text-transform:uppercase; letter-spacing:0.5px;'>{p['category']}</div>
            <div style='margin-top:8px; font-size:0.8rem; color:#2e7d32;'>Buy at: shop.jivo.in</div>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Close", key="close_product"):
        st.session_state.selected_product = None
        st.rerun()

with st.expander("Upload File (PDF, CSV, Image, TXT)"):
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

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            content = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🌿"):
            st.write(msg.content)

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
