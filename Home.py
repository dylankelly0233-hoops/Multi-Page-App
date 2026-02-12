import streamlit as st
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AlphaPoint Sports",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "ALPHAPOINT" LOOK ---
# This CSS mimics the dark, finance-style aesthetic of your PPT
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    .hero-title {
        color: #4EA8DE; /* AlphaPoint Cyan */
        font-size: 3em;
        text-align: center;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        color: #A0A0A0;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 40px;
        font-style: italic;
    }
    /* Cards/Grid Layout */
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF8C00; /* AlphaPoint Orange */
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
# Use columns to center the logo if you have one
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # st.image("assets/logo.png", width=200) # Uncomment if you save the logo
    st.markdown('<h1 class="hero-title">ALPHAPOINT SPORTS</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">"Applying the discipline of finance to quantitative sports wagering."</p>', 
        unsafe_allow_html=True
    )

st.divider()

# --- MISSION STATEMENT ---
st.info("""
**We provide bettors with an edge** through independent, data-driven power ratings 
for all major US professional and collegiate sports.
""")

# --- THE "GRID" DASHBOARD (Recreating PPT Slide 2) ---
st.subheader("📊 Analytics Hub")

# Row 1
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="metric-card">
        <h3>The Research Wire</h3>
        <p>Deep dive blogs & relevant tweets.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #4EA8DE;">
        <h3>Market Mirror Index</h3>
        <p>Tracking sentiment vs sharp money.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #D4AF37;">
        <h3>The SEP Index</h3>
        <p>Sports Equity Performance metrics.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# Row 2
c4, c5, c6 = st.columns(3)
with c4:
    st.markdown("""
    <div class="metric-card">
        <h3>Game Projections</h3>
        <p>Live probability & spread modeling.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to CBB Model 🏀"):
        st.switch_page("pages/4_🎓_College_Basketball.py")

with c5:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #4EA8DE;">
        <h3>Daily Free Pick</h3>
        <p>Our highest confidence play of the day.</p>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #D4AF37;">
        <h3>About The Models</h3>
        <p>Methodology & mathematical framework.</p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR LOGIN SIMULATION ---
st.sidebar.title("🔐 User Access")
status = st.sidebar.radio("Membership Tier", ["Guest", "Subscriber"])

if status == "Guest":
    st.sidebar.warning("You are viewing Public models only.")
else:
    st.sidebar.success("✅ Premium Access Active")
