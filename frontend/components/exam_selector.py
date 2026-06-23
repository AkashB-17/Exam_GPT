import streamlit as st


# Exam config with icons and colors
EXAM_OPTIONS = [
    {"display": "GATE — Computer Science (CS)", "id": "gate_cs", "icon": "💻", "color": "#818cf8"},
    {"display": "GATE — Electronics & Communication (ECE)", "id": "gate_ece", "icon": "⚡", "color": "#818cf8"},
    {"display": "CAT — MBA Entrance", "id": "cat", "icon": "📊", "color": "#f472b6"},
    {"display": "UPSC — Civil Services (GS)", "id": "upsc_gs", "icon": "🏛️", "color": "#fbbf24"},
    {"display": "IELTS — English Proficiency", "id": "ielts", "icon": "📝", "color": "#34d399"},
    {"display": "GRE — Graduate Admissions", "id": "gre", "icon": "🎓", "color": "#fb923c"},
]


def render_exam_selector():
    """Render the exam selector with icons."""
    exam_displays = [f"{e['icon']}  {e['display']}" for e in EXAM_OPTIONS]
    exam_id_map = {f"{e['icon']}  {e['display']}": e["id"] for e in EXAM_OPTIONS}

    # Find current selection index
    default_idx = 0
    for i, e in enumerate(EXAM_OPTIONS):
        if e["id"] == st.session_state.selected_exam:
            default_idx = i
            break

    selected_display = st.selectbox(
        "🎯 Select Target Exam",
        options=exam_displays,
        index=default_idx,
        help="Choose the competitive exam you're preparing for"
    )

    st.session_state.selected_exam = exam_id_map[selected_display]
