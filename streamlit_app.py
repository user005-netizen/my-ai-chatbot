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

st.set_page_config(page_title="JIVO Wellness AI", page_icon="https://jivo.in/wp-content/uploads/2021/07/jivo-logo-300x300.png", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }

.stApp {
    background: #fafdf7;
    background-image:
        radial-gradient(circle at 10% 20%, rgba(76,175,80,0.06) 0%, transparent 50%),
        radial-gradient(circle at 90% 80%, rgba(139,195,74,0.05) 0%, transparent 50%);
}

.main .block-container {
    background: transparent;
    padding: 1.5rem 2rem;
    max-width: 100%;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #e8f5e9 !important;
    box-shadow: 4px 0 20px rgba(46,125,50,0.06) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* BUTTONS */
.stButton > button {
    background: white !important;
    color: #2e7d32 !important;
    border: 1.5px solid #c8e6c9 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 6px 14px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 1px 4px rgba(46,125,50,0.08) !important;
}
.stButton > button:hover {
    background: #f1f8e9 !important;
    border-color: #81c784 !important;
    box-shadow: 0 3px 12px rgba(46,125,50,0.18) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    background: #e8f5e9 !important;
    transform: translateY(0px) !important;
    box-shadow: 0 1px 4px rgba(46,125,50,0.15) !important;
}

/* PRODUCT BUTTONS in sidebar */
.product-btn > button {
    background: linear-gradient(135deg, #f9fdf6, #f1f8e9) !important;
    color: #1b5e20 !important;
    border: 1px solid #dcedc8 !important;
    border-left: 3px solid #66bb6a !important;
    border-radius: 10px !important;
    text-align: left !important;
    font-size: 0.78rem !important;
    padding: 8px 12px !important;
    margin-bottom: 4px !important;
    transition: all 0.2s ease !important;
}
.product-btn > button:hover {
    background: linear-gradient(135deg, #e8f5e9, #dcedc8) !important;
    border-left-color: #2e7d32 !important;
    box-shadow: 0 2px 10px rgba(46,125,50,0.2) !important;
    transform: translateX(4px) !important;
}

/* CHAT */
[data-testid="stChatMessage"] {
    background: white !important;
    border-radius: 14px !important;
    border: 1px solid #f0f7f0 !important;
    box-shadow: 0 2px 8px rgba(46,125,50,0.06) !important;
    margin-bottom: 10px !important;
    padding: 4px !important;
}

/* INPUTS */
.stTextInput > div > input, .stTextAreaInput > div > textarea {
    border: 1.5px solid #c8e6c9 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > input:focus {
    border-color: #66bb6a !important;
    box-shadow: 0 0 0 3px rgba(102,187,106,0.12) !important;
}

[data-testid="stChatInput"] > div {
    border: 1.5px solid #c8e6c9 !important;
    border-radius: 14px !important;
    background: white !important;
}

/* EXPANDER */
div[data-testid="stExpander"] {
    background: white;
    border: 1px solid #e8f5e9;
    border-radius: 12px;
    overflow: hidden;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f8e9;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: #555 !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #2e7d32 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* SELECTBOX */
.stSelectbox > div > div {
    border: 1.5px solid #c8e6c9 !important;
    border-radius: 10px !important;
    background: white !important;
}

/* SUCCESS / ERROR */
.stSuccess { border-radius: 10px !important; }
.stError { border-radius: 10px !important; }

/* PRODUCT DETAIL CARD */
.product-detail-card {
    background: white;
    border: 1px solid #c8e6c9;
    border-top: 4px solid #2e7d32;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(46,125,50,0.1);
    animation: slideIn 0.3s ease;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* CSR BANNER */
.csr-banner {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    color: white;
    margin: 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

# Session init
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

# ── LOGIN PAGE ─────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding:2rem 0 0.5rem 0;'>
        <img src='https://jivo.in/wp-content/uploads/2021/07/siteheader-logo-143x97.png'
             style='height:80px; margin-bottom:0.8rem;' alt='JIVO Logo'>
        <h1 style='font-family:Playfair Display,serif; color:#1b5e20; font-size:2.2rem;
        margin:0; font-weight:700; letter-spacing:1px;'>JIVO Wellness</h1>
        <p style='color:#888; font-size:0.95rem; margin:6px 0 0 0; letter-spacing:2px;
        text-transform:uppercase; font-size:0.75rem;'>AI Assistant &nbsp;|&nbsp; Purity For Charity</p>
    </div>
    """, unsafe_allow_html=True)

    # CSR strip on login page
    st.markdown("""
    <div style='display:flex; gap:12px; justify-content:center; margin:1rem 0; flex-wrap:wrap;'>
        <div style='background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border:1px solid #c8e6c9;
        border-radius:12px; padding:10px 18px; text-align:center; min-width:140px;'>
            <div style='font-size:1.3rem; font-weight:800; color:#2e7d32;'>40,000+</div>
            <div style='font-size:0.72rem; color:#666;'>Meals Served</div>
        </div>
        <div style='background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border:1px solid #c8e6c9;
        border-radius:12px; padding:10px 18px; text-align:center; min-width:140px;'>
            <div style='font-size:1.3rem; font-weight:800; color:#2e7d32;'>70,000+</div>
            <div style='font-size:0.72rem; color:#666;'>Children Nourished</div>
        </div>
        <div style='background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border:1px solid #c8e6c9;
        border-radius:12px; padding:10px 18px; text-align:center; min-width:140px;'>
            <div style='font-size:1.3rem; font-weight:800; color:#2e7d32;'>15+</div>
            <div style='font-size:0.72rem; color:#666;'>Years of Wellness</div>
        </div>
        <div style='background:linear-gradient(135deg,#e8f5e9,#f1f8e9); border:1px solid #c8e6c9;
        border-radius:12px; padding:10px 18px; text-align:center; min-width:140px;'>
            <div style='font-size:1.3rem; font-weight:800; color:#2e7d32;'>ISO</div>
            <div style='font-size:0.72rem; color:#666;'>& Sedex Certified</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style='background:white; border:1px solid #e8f5e9; border-radius:20px;
        padding:2rem; box-shadow:0 8px 40px rgba(46,125,50,0.1); margin-top:0.5rem;'>
        </div>
        """, unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        with tab1:
            email = st.text_input("Email Address", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            if st.button("Login to JIVO AI", use_container_width=True, key="login_btn"):
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
            if st.button("Create My Account", use_container_width=True, key="signup_btn"):
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

    # Baru Sahib / Charity section on login
    st.markdown("""
    <div style='margin-top:2rem; background:linear-gradient(135deg,#1b5e20,#2e7d32);
    border-radius:16px; padding:1.5rem 2rem; text-align:center; color:white;'>
        <div style='font-family:Playfair Display,serif; font-size:1.2rem; font-weight:600;
        margin-bottom:0.5rem;'>Purity For Charity</div>
        <p style='font-size:0.85rem; color:#c8e6c9; margin:0; line-height:1.6;'>
        Since its inception, JIVO has been transforming lives through wellness.<br>
        We channel profits into Rural Education, supporting 70,000+ children and families<br>
        in partnership with <b style='color:white;'>Baru Sahib Association</b>.
        </p>
        <div style='margin-top:1rem; display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;'>
            <div style='text-align:center;'>
                <img src='https://jivo.in/wp-content/uploads/2021/07/MEAK-DISTRIBUTION.jpg'
                style='width:90px; height:65px; object-fit:cover; border-radius:8px; border:2px solid rgba(255,255,255,0.3);'>
                <div style='font-size:0.7rem; color:#a5d6a7; margin-top:4px;'>COVID Meals</div>
            </div>
            <div style='text-align:center;'>
                <img src='https://jivo.in/wp-content/uploads/2021/07/IMMUNITY-BOSSTER-DISTRIBUTION.jpg'
                style='width:90px; height:65px; object-fit:cover; border-radius:8px; border:2px solid rgba(255,255,255,0.3);'>
                <div style='font-size:0.7rem; color:#a5d6a7; margin-top:4px;'>Immunity Drive</div>
            </div>
            <div style='text-align:center;'>
                <img src='https://jivo.in/wp-content/uploads/2021/07/OXYGEN-DISTRIBUTION.jpg'
                style='width:90px; height:65px; object-fit:cover; border-radius:8px; border:2px solid rgba(255,255,255,0.3);'>
                <div style='font-size:0.7rem; color:#a5d6a7; margin-top:4px;'>Oxygen Support</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── MAIN APP ────────────────────────────────────────────────────────
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
- CSR Partner: Baru Sahib Association - Rural Education and Children Nourishment

=== LIVE PRODUCT PRICES ===
{products_text}

=== CSR ===
- 40,000+ meals during COVID-19 (March 2020)
- Immunity boosters to COVID-19 warriors (April 2020)
- Free Oxygen Concentrators to patients (May 2021)
- 70,000+ children and families nourished
- Rural school construction
- Baru Sahib Association partnership

STRICT RULES:
- ONLY answer questions related to JIVO Wellness, its products, prices, employees, and operations.
- For product/price queries use the LIVE PRODUCT PRICES above.
- Always mention shop.jivo.in for purchases.
- If unrelated question asked, say: I can only assist with JIVO Wellness related queries.
- Be professional, warm and helpful."""

# ── SIDEBAR ─────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + brand
    st.markdown(f"""
    <div style='padding:1.5rem 1rem 0.8rem 1rem; border-bottom:1px solid #e8f5e9;'>
        <div style='text-align:center; margin-bottom:1rem;'>
            <img src='https://jivo.in/wp-content/uploads/2021/07/siteheader-logo-143x97.png'
                 style='height:55px;' alt='JIVO Logo'>
        </div>
        <div style='background:linear-gradient(135deg,#f1f8e9,#e8f5e9); border-radius:12px;
        padding:10px 12px; border:1px solid #c8e6c9;'>
            <div style='font-size:0.72rem; color:#888; margin-bottom:2px;'>Signed in as</div>
            <div style='font-size:0.82rem; font-weight:600; color:#1b5e20;
            word-break:break-all;'>{st.session_state.user_email}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            supabase.table("chat_history").delete().eq("user_id", st.session_state.user_id).execute()
            st.session_state.history = []
            st.rerun()
    with col2:
        if st.button("Logout", use_container_width=True):
            supabase.auth.sign_out()
            for key in ["logged_in", "user_id", "user_email", "access_token", "history", "selected_product"]:
                st.session_state[key] = [] if key == "history" else None
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    language = st.selectbox("Language / Bhasha", ["English", "Hindi", "Both"])

    # Products section
    st.markdown("""
    <div style='margin:12px 0 6px 0; padding:0 4px;'>
        <div style='font-size:0.7rem; font-weight:600; color:#888; text-transform:uppercase;
        letter-spacing:1.5px;'>Our Products</div>
    </div>
    """, unsafe_allow_html=True)

    category_icons = {
        "Edible Oil": "🫙", "Olive Oil": "🫒", "Ghee": "🥛",
        "Health Drinks": "🥤", "Nutraceuticals": "💊", "Seeds": "🌱",
        "Beverages": "☕", "Honey": "🍯", "Snacks": "🥜"
    }

    current_category = ""
    for p in products:
        if p['category'] != current_category:
            current_category = p['category']
            icon = category_icons.get(p['category'], "🌿")
            st.markdown(f"""
            <div style='font-size:0.68rem; font-weight:600; color:#a5d6a7; text-transform:uppercase;
            letter-spacing:1px; padding:6px 4px 2px 4px;'>{icon} {p['category']}</div>
            """, unsafe_allow_html=True)

        is_selected = st.session_state.selected_product == p['name']
        btn_style = "product-btn"
        label = f"{'> ' if is_selected else ''}{p['name']}  |  Rs.{p['price']}"

        st.markdown(f"<div class='{btn_style}'>", unsafe_allow_html=True)
        if st.button(label, key=f"prod_{p['id']}", use_container_width=True):
            if st.session_state.selected_product == p['name']:
                st.session_state.selected_product = None
            else:
                st.session_state.selected_product = p['name']
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # CSR strip in sidebar
    st.markdown("""
    <div style='margin-top:16px; background:linear-gradient(135deg,#1b5e20,#2e7d32);
    border-radius:12px; padding:12px; text-align:center;'>
        <div style='font-size:0.72rem; color:#a5d6a7; letter-spacing:1px; margin-bottom:6px;'>PURITY FOR CHARITY</div>
        <img src='https://jivo.in/wp-content/uploads/2021/07/jivo-footer-logo.png'
             style='height:30px; filter:brightness(0) invert(1); opacity:0.8;'>
        <div style='font-size:0.68rem; color:#c8e6c9; margin-top:6px; line-height:1.4;'>
            ISO &amp; Sedex Certified<br>
            Baru Sahib Association Partner
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── MAIN AREA ────────────────────────────────────────────────────────

# Header with logo
st.markdown("""
<div style='background:white; border:1px solid #e8f5e9; border-radius:18px;
padding:1.2rem 1.8rem; margin-bottom:1rem;
box-shadow:0 2px 16px rgba(46,125,50,0.08);
display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;'>
    <div style='display:flex; align-items:center; gap:16px;'>
        <img src='https://jivo.in/wp-content/uploads/2021/07/siteheader-logo-143x97.png'
             style='height:52px;' alt='JIVO'>
        <div>
            <div style='font-family:Playfair Display,serif; font-size:1.25rem; font-weight:700;
            color:#1b5e20; line-height:1.2;'>JIVO Wellness AI Assistant</div>
            <div style='font-size:0.78rem; color:#888; margin-top:3px;'>
                Powered by Advanced AI &nbsp;|&nbsp; Purity For Charity
            </div>
        </div>
    </div>
    <div style='display:flex; gap:8px; flex-wrap:wrap;'>
        <div style='background:#f1f8e9; border:1px solid #c8e6c9; border-radius:20px;
        padding:5px 12px; font-size:0.72rem; font-weight:600; color:#2e7d32;'>
            India No.1 Canola Oil
        </div>
        <div style='background:#fff8e1; border:1px solid #ffe082; border-radius:20px;
        padding:5px 12px; font-size:0.72rem; font-weight:600; color:#f57f17;'>
            ISO Certified
        </div>
        <div style='background:#e8f5e9; border:1px solid #a5d6a7; border-radius:20px;
        padding:5px 12px; font-size:0.72rem; font-weight:600; color:#1b5e20;'>
            Sedex Certified
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CSR Banner (compact, always visible)
st.markdown("""
<div style='background:linear-gradient(135deg,#1b5e20 0%,#2e7d32 60%,#388e3c 100%);
border-radius:14px; padding:1rem 1.5rem; margin-bottom:1rem;
display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;'>
    <div style='color:white;'>
        <div style='font-family:Playfair Display,serif; font-size:1rem; font-weight:600;
        margin-bottom:2px;'>Purity For Charity</div>
        <div style='font-size:0.75rem; color:#a5d6a7;'>
            Baru Sahib Association Partner &nbsp;|&nbsp; Rural Education Initiative
        </div>
    </div>
    <div style='display:flex; gap:10px; align-items:center;'>
        <img src='https://jivo.in/wp-content/uploads/2021/07/MEAK-DISTRIBUTION.jpg'
             style='height:44px; width:60px; object-fit:cover; border-radius:8px;
             border:2px solid rgba(255,255,255,0.25);'>
        <img src='https://jivo.in/wp-content/uploads/2021/07/IMMUNITY-BOSSTER-DISTRIBUTION.jpg'
             style='height:44px; width:60px; object-fit:cover; border-radius:8px;
             border:2px solid rgba(255,255,255,0.25);'>
        <img src='https://jivo.in/wp-content/uploads/2021/07/OXYGEN-DISTRIBUTION.jpg'
             style='height:44px; width:60px; object-fit:cover; border-radius:8px;
             border:2px solid rgba(255,255,255,0.25);'>
        <div style='text-align:right; color:white;'>
            <div style='font-size:1.1rem; font-weight:800;'>70,000+</div>
            <div style='font-size:0.68rem; color:#a5d6a7;'>Lives Touched</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Product detail card (when clicked)
if st.session_state.selected_product:
    matched = [p for p in products if p['name'] == st.session_state.selected_product]
    if matched:
        p = matched[0]
        icon = category_icons.get(p['category'], "🌿")
        st.markdown(f"""
        <div class='product-detail-card'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;'>
                <div style='flex:1;'>
                    <div style='font-size:0.7rem; color:#888; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:4px;'>{icon} {p['category']}</div>
                    <div style='font-family:Playfair Display,serif; font-size:1.15rem;
                    font-weight:700; color:#1b5e20; margin-bottom:8px;'>{p['name']}</div>
                    <div style='font-size:0.88rem; color:#555; line-height:1.6;
                    margin-bottom:10px;'>{p['description']}</div>
                    <div style='display:flex; align-items:center; gap:12px; flex-wrap:wrap;'>
                        <div style='font-size:1.5rem; font-weight:800; color:#2e7d32;'>Rs. {p['price']}</div>
                        <a href='https://shop.jivo.in' target='_blank'
                        style='background:linear-gradient(135deg,#2e7d32,#388e3c); color:white;
                        padding:7px 18px; border-radius:20px; text-decoration:none;
                        font-size:0.8rem; font-weight:600; letter-spacing:0.5px;'>Buy on shop.jivo.in</a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Close Product Details", key="close_prod"):
            st.session_state.selected_product = None
            st.rerun()

# File upload
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

# Chat history display
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            content = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="https://jivo.in/wp-content/uploads/2021/07/jivo-logo-300x300.png"):
            st.write(msg.content)

# Chat input
user_input = st.chat_input("Ask about JIVO products, prices, wellness, CSR...")

if user_input:
    if file_content:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nFile data:\n{file_content}\n\nUser: {user_input}"
    else:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nUser: {user_input}"

    st.session_state.history.append(HumanMessage(content=full_input))
    save_message(st.session_state.user_id, "user", user_input)

    with st.chat_message("user", avatar="👤"):
        st.write(user_input)

    with st.chat_message("assistant", avatar="https://jivo.in/wp-content/uploads/2021/07/jivo-logo-300x300.png"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)

    st.session_state.history.append(AIMessage(content=response.content))
    save_message(st.session_state.user_id, "assistant", response.content)
    st.rerun()
