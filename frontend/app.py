import streamlit as st
import os, sys

# Make sure imports from frontend work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.components import sidebar, exam_selector, query_input, response_card
from frontend.utils.api_client import check_backend_health


def inject_custom_css():
    """Inject custom CSS for a polished, premium look."""
    st.markdown("""
    <style>
    /* ===== Google Font ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== Global ===== */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* ===== Main Container ===== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    /* ===== Header Styling ===== */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
    }

    .exam-pills {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 0.75rem;
        margin-bottom: 1.5rem;
    }

    .exam-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .pill-gate { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .pill-cat { background: rgba(244, 114, 182, 0.15); color: #f472b6; }
    .pill-upsc { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
    .pill-ielts { background: rgba(52, 211, 153, 0.15); color: #34d399; }
    .pill-gre { background: rgba(251, 146, 60, 0.15); color: #fb923c; }

    /* ===== Glassmorphism Cards ===== */
    .glass-card {
        background: rgba(30, 30, 46, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }

    /* ===== Module Badges ===== */
    .module-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 24px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin-bottom: 1rem;
    }

    .badge-solver {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.2), rgba(16, 185, 129, 0.1));
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .badge-explainer {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(59, 130, 246, 0.1));
        color: #60a5fa;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }

    .badge-writing {
        background: linear-gradient(135deg, rgba(192, 132, 252, 0.2), rgba(168, 85, 247, 0.1));
        color: #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.3);
    }

    /* ===== Confidence Meter ===== */
    .confidence-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0.5rem 0 1rem 0;
    }

    .confidence-bar-bg {
        flex-grow: 1;
        height: 6px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 3px;
        overflow: hidden;
    }

    .confidence-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.8s ease;
    }

    .confidence-label {
        font-size: 0.78rem;
        font-weight: 600;
        min-width: 45px;
        text-align: right;
    }

    /* ===== Citation Cards ===== */
    .citation-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .citation-header {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #818cf8;
        margin-bottom: 0.5rem;
    }

    .citation-question {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.5;
    }

    .citation-answer {
        font-size: 0.85rem;
        color: #34d399;
        margin-top: 0.5rem;
        padding-left: 0.75rem;
        border-left: 2px solid rgba(52, 211, 153, 0.4);
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: rgba(15, 15, 26, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ===== Status Banner ===== */
    .status-banner {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        border-radius: 10px;
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .status-online {
        background: rgba(52, 211, 153, 0.1);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.2);
    }

    .status-offline {
        background: rgba(248, 113, 113, 0.1);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.2);
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    .pulse-green {
        background: #34d399;
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4);
    }

    .pulse-red {
        background: #f87171;
        box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.4);
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
        70% { box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
        100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }

    /* ===== How It Works Steps ===== */
    .step-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 0.75rem;
    }

    .step-number {
        min-width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .step-text {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.5;
        padding-top: 3px;
    }

    /* ===== Feedback Buttons ===== */
    .feedback-section {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* ===== Text area styling ===== */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(30, 30, 46, 0.5) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 1rem !important;
    }

    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }

    /* ===== Button styling ===== */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }

    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        width: 100% !important;
    }

    .stFormSubmitButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
    }

    /* ===== Selectbox styling ===== */
    .stSelectbox > div > div {
        border-radius: 10px !important;
    }

    /* ===== Divider ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.5rem 0 !important;
    }

    /* ===== Hide Streamlit branding ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ===== Expander styling ===== */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_state():
    """Initialize Streamlit session state."""
    defaults = {
        "history": [],
        "selected_exam": "gate_cs",
        "current_response": None,
        "is_loading": False,
        "backend_online": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_hero():
    """Render the hero/header section."""
    st.markdown('<p class="hero-title">🎓 ExamGPT India</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">AI-Powered Q&A Platform grounded in real Previous Year Questions</p>',
        unsafe_allow_html=True
    )

    # Exam pills
    st.markdown("""
    <div class="exam-pills">
        <span class="exam-pill pill-gate">GATE CS</span>
        <span class="exam-pill pill-gate">GATE ECE</span>
        <span class="exam-pill pill-cat">CAT</span>
        <span class="exam-pill pill-upsc">UPSC</span>
        <span class="exam-pill pill-ielts">IELTS</span>
        <span class="exam-pill pill-gre">GRE</span>
    </div>
    """, unsafe_allow_html=True)


def render_backend_status():
    """Show backend connection status."""
    is_online = check_backend_health()
    st.session_state.backend_online = is_online

    if is_online:
        st.markdown("""
        <div class="status-banner status-online">
            <div class="pulse-dot pulse-green"></div>
            Backend connected — Ready to answer questions
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-banner status-offline">
            <div class="pulse-dot pulse-red"></div>
            Backend offline — Start it with: uvicorn backend.main:app --port 8000
        </div>
        """, unsafe_allow_html=True)


def render_how_it_works():
    """Show how the system works."""
    with st.expander("💡 How ExamGPT Works", expanded=False):
        st.markdown("""
        <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-text"><strong>Select your exam</strong> — Choose from GATE, CAT, UPSC, IELTS, or GRE</div>
        </div>
        <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-text"><strong>Ask any question</strong> — Paste a problem to solve, a concept to explain, or an essay to evaluate</div>
        </div>
        <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-text"><strong>AI detects the module</strong> — Automatically picks Solver, Explainer, or Writing Feedback</div>
        </div>
        <div class="step-item">
            <div class="step-number">4</div>
            <div class="step-text"><strong>PYQ retrieval (RAG)</strong> — Finds similar Previous Year Questions from our vector database</div>
        </div>
        <div class="step-item">
            <div class="step-number">5</div>
            <div class="step-text"><strong>Structured answer</strong> — Generates an exam-quality response grounded in real PYQs</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="ExamGPT India — AI Exam Tutor",
        layout="wide",
        page_icon="🎓",
        initial_sidebar_state="expanded"
    )

    inject_custom_css()
    initialize_state()

    # Sidebar
    sidebar.render_sidebar()

    # Main content
    render_hero()
    render_backend_status()

    st.markdown("---")

    # How It Works
    render_how_it_works()

    # Exam Selector
    exam_selector.render_exam_selector()

    # Query Input
    query_input.render_query_input()

    # Response Card
    if st.session_state.current_response is not None:
        response_card.render_response_card()


if __name__ == "__main__":
    main()
