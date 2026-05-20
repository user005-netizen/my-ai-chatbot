import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
import os
import pypdf
import pandas as pd

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

st.set_page_config(
    page_title="JIVO AI Assistant",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
<style>
    /* Main background - light grey */
    .stApp {
        background-color: #f0f4f0;
    }
    /* Main content area */
    .main .block-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.07);
        margin-top: 1rem;
    }
    /* Sidebar - white with green accent */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 3px solid #e8f5e9;
    }
    [data-testid="stSidebar"] * {
        color: #1b5e20 !important;
    }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #2e7d32, #43a047);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46,125,50,0.3);
    }
    /* Login card */
    .login-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.10);
        max-width: 420px;
        margin: 3rem auto;
        border-top: 5px solid #2e7d32;
    }
    /* Chat header banner */
    .chat-header {
        background: linear-gradient(90deg, #1b5e20, #43a047);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: #f9fbe7 !important;
        border-radius: 12px;
        border: 1px solid #e8f5e9;
        margin: 4px 0;
    }
    /* Selectbox */
    .stSelectbox label { color: #1b5e20 !important; font-weight: 600; }
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Credentials
USERS = {"aiuser": "ai@1234"}

# Session state init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = []

# ── LOGIN PAGE ──
if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding:2rem 0;'>
        <div style='background:linear-gradient(135deg,#2e7d32,#66bb6a);
                    width:80px;height:80px;border-radius:50%;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:2.5rem;margin-bottom:1rem;
                    box-shadow:0 4px 20px rgba(46,125,50,0.3);'>
            🌿
        </div>
        <h1 style='color:#1b5e20;font-size:2.5rem;margin:0;font-weight:700;'>JIVO</h1>
        <p style='color:#555;font-size:1rem;margin-top:0.3rem;'>AI Assistant Platform</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔐 Secure Login")
        st.markdown("<hr style='border-color:#e8f5e9;margin:0.5rem 0 1rem;'>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Login →", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
        <div style='background:linear-gradient(135deg,#2e7d32,#66bb6a);
                    width:55px;height:55px;border-radius:50%;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:1.6rem;box-shadow:0 3px 10px rgba(46,125,50,0.25);'>
            🌿
        </div>
        <h3 style='color:#1b5e20;margin:0.5rem 0 0;font-weight:700;'>JIVO</h3>
        <p style='color:#555;font-size:0.8rem;margin:0;'>AI Assistant</p>
        <hr style='border-color:#e8f5e9;margin:0.8rem 0;'>
        <p style='color:#2e7d32;font-size:0.85rem;'>👤 <b>{st.session_state.username.upper()}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**💬 Recent Chats**")
    if st.session_state.history:
        user_msgs = [m for m in st.session_state.history if isinstance(m, HumanMessage)]
        for msg in user_msgs[-5:]:
            raw = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            short = raw[:32] + "..." if len(raw) > 32 else raw
            st.markdown(f"<div style='background:#f1f8e9;padding:5px 8px;border-radius:6px;margin:3px 0;font-size:0.78rem;color:#1b5e20;'>💬 {short}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color:#888;'>No messages yet</small>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#e8f5e9;'>", unsafe_allow_html=True)
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

# ── MAIN ──
st.markdown("""
<div class='chat-header'>
    <h2 style='margin:0;font-size:1.5rem;'>🌿 JIVO AI Assistant</h2>
    <p style='margin:0.3rem 0 0;opacity:0.9;font-size:0.9rem;'>Your intelligent company assistant</p>
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

system_prompt = """You are JIVO Wellness AI Assistant — a professional corporate AI for JIVO Wellness company.

COMPANY KNOWLEDGE BASE:
=== ABOUT JIVO ===
- Full Name: JIVO Wellness
- Tagline: Purity For Charity
- Experience: 15+ years in wellness industry
- India's Largest Seller of Cold Press Canola Oil
- India's First Patented Wheatgrass Products
- Certifications: ISO Certified, Sedex Certified
- Address: J3/190, Nehru Market, Rajouri Garden, New Delhi 110027
- Email: Info@jivo.in | Toll Free: 1800 137 4433
- Shop: shop.jivo.in

=== PRODUCTS ===
1. COLD PRESS CANOLA OIL — Lowest bad fat, highest good fat (93% unsaturated), rich in Omega-3, MUFA-rich, high smoke point, Vitamin A and D fortified.
2. EXTRA VIRGIN OLIVE OIL — MUFA-rich, maintains cholesterol, natural antioxidants, rich in Vitamin E.
3. EXTRA LIGHT OLIVE OIL — Higher smoke point, perfect for frying and baking, MUFA-rich.
4. POMACE OLIVE OIL — Available on shop.jivo.in
5. WHEATGRASS JUICE — India's first patented wheatgrass product. Himalayan fields, two flavors: Ginger and Cola. Nutrients equal to 2kg vegetables, boosts immunity, aids digestion.
6. IMMUNITY BOOSTER — Blend of wheatgrass, amla, ginger. Rich in Vitamins A,C,D,E,K and B-complex.
7. MUESLI MUNCH — Millets, nuts, oats, amaranth, almonds, raisins with jaggery and cinnamon. 100% natural, rich in fibre and proteins.
8. A2 DESI GHEE — 100% pure traditional method, Omega-3, Vitamins A,D,E,K, sugar free, gluten free.
9. MUSTARD OIL — Available on shop.jivo.in
10. SUNFLOWER OIL — Available on shop.jivo.in
11. SOYABEAN OIL — Available on shop.jivo.in
12. NATURAL MINERALS water — Available on shop.jivo.in

=== CSR ACTIVITIES ===
- 40,000+ meals served during COVID-19
- Immunity boosters distributed to COVID-19 warriors
- Free Oxygen Concentrators to COVID-19 patients
- Rural Education — construction of rural schools
- Nourishment of 70,000+ children and families

=== CONTACT ===
- Website: jivo.in | Shop: shop.jivo.in
- Facebook: facebook.com/jivowellness
- Instagram: instagram.com/jivowellness

STRICT RULES:
- ONLY answer questions related to JIVO Wellness company, its products, employees, hierarchy, and operations.
- Use the knowledge base above to give accurate real answers about JIVO products and company.
- For purchase queries always mention shop.jivo.in
- If someone asks about competitors or unrelated topics say: I can only assist with JIVO Wellness related queries.
- Be professional, warm, and helpful."""

lang_map = {
    "English": "Respond in English only.",
    "Hindi": "Sirf Hindi mein jawab do.",
    "Both": "Respond in both Hindi and English."
}

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            raw = msg.content.split("User: ")[-1] if "User: " in msg.content else msg.content
            st.write(raw)
    else:
        with st.chat_message("assistant", avatar="🌿"):
            st.write(msg.content)

user_input = st.chat_input("Ask about JIVO employees, hierarchy, products...")

if user_input:
    if file_content:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nFile data:\n{file_content}\n\nUser: {user_input}"
    else:
        full_input = f"{system_prompt}\n{lang_map[language]}\n\nUser: {user_input}"

    st.session_state.history.append(HumanMessage(content=full_input))
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.history)
            st.write(response.content)
    st.session_state.history.append(AIMessage(content=response.content))
    st.rerun()
