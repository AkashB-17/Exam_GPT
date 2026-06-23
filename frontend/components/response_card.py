import streamlit as st
from frontend.utils import api_client


MODULE_BADGES = {
    "solver": {
        "label": "⚡ Step-by-Step Solver",
        "css_class": "badge-solver",
    },
    "explainer": {
        "label": "💡 Concept Explainer",
        "css_class": "badge-explainer",
    },
    "writing_feedback": {
        "label": "✍️ Writing Feedback & Scoring",
        "css_class": "badge-writing",
    },
}


def _render_confidence_meter(confidence: float):
    """Render a visual confidence meter bar."""
    pct = int(confidence * 100)

    if confidence >= 0.7:
        color = "#34d399"
        label_color = "#34d399"
    elif confidence >= 0.4:
        color = "#fbbf24"
        label_color = "#fbbf24"
    else:
        color = "#f87171"
        label_color = "#f87171"

    st.markdown(f"""
    <div class="confidence-container">
        <span style="font-size: 0.78rem; color: #64748b;">Confidence</span>
        <div class="confidence-bar-bg">
            <div class="confidence-bar-fill" style="width: {pct}%; background: {color};"></div>
        </div>
        <span class="confidence-label" style="color: {label_color};">{pct}%</span>
    </div>
    """, unsafe_allow_html=True)


def _render_citations(citations: list):
    """Render PYQ citations in styled cards."""
    if not citations:
        return

    with st.expander(f"📚 Related Previous Year Questions ({len(citations)} found)", expanded=False):
        for citation in citations:
            exam_label = citation.get('exam', '').upper().replace('_', ' ')
            year = citation.get('year', '')
            subject = citation.get('subject', '')
            question_text = citation.get('question_text', '')
            answer = citation.get('answer', '')

            st.markdown(f"""
            <div class="citation-card">
                <div class="citation-header">{exam_label} {year} — {subject}</div>
                <div class="citation-question">{question_text}</div>
                {"<div class='citation-answer'><strong>Answer:</strong> " + answer + "</div>" if answer else ""}
            </div>
            """, unsafe_allow_html=True)


def _render_feedback_buttons(query_id: str):
    """Render feedback thumbs up/down buttons."""
    st.markdown("---")
    st.markdown("**Was this helpful?**")
    col1, col2, col3 = st.columns([1, 1, 10])
    with col1:
        if st.button("👍", key="thumb_up", help="This answer was helpful"):
            if query_id:
                api_client.submit_feedback(query_id, 1)
                st.toast("✅ Thanks for the positive feedback!", icon="👍")
            else:
                st.toast("⚠️ Could not record feedback", icon="⚠️")
    with col2:
        if st.button("👎", key="thumb_down", help="This answer needs improvement"):
            if query_id:
                api_client.submit_feedback(query_id, -1)
                st.toast("📝 Thanks! We'll work on improving.", icon="👎")
            else:
                st.toast("⚠️ Could not record feedback", icon="⚠️")


def render_response_card():
    """Render the AI response with module badge, confidence meter, citations, and feedback."""
    response = st.session_state.current_response
    if not response:
        return

    st.markdown("---")

    # Module badge
    module = response.get("module_used", "explainer")
    badge_info = MODULE_BADGES.get(module, MODULE_BADGES["explainer"])

    st.markdown(
        f'<div class="module-badge {badge_info["css_class"]}">{badge_info["label"]}</div>',
        unsafe_allow_html=True
    )

    # Confidence meter
    confidence = response.get("confidence", 0.5)
    _render_confidence_meter(confidence)

    # AI Answer
    st.markdown("### 🤖 AI Answer")

    answer_text = response.get("answer", "")
    st.markdown(answer_text)

    # Citations
    citations = response.get("citations", [])
    _render_citations(citations)

    # Feedback
    query_id = response.get("query_id", "")
    _render_feedback_buttons(query_id)
