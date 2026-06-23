import streamlit as st


EXAM_ICONS = {
    "gate_cs": "💻",
    "gate_ece": "⚡",
    "cat": "📊",
    "upsc_gs": "🏛️",
    "ielts": "📝",
    "gre": "🎓",
}


def render_sidebar():
    """Render the premium sidebar with branding, history, and info."""
    with st.sidebar:
        # Logo / Branding
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.25rem;">🎓</div>
            <div style="
                font-size: 1.3rem;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">ExamGPT India</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">
                AI Tutor • RAG-Powered • PYQ-Grounded
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # --- Recent History ---
        st.markdown("##### 📋 Recent Queries")

        if not st.session_state.history:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 1.5rem 1rem;
                color: #475569;
                font-size: 0.85rem;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
                No queries yet.<br/>
                <span style="font-size: 0.78rem;">Ask a question to get started!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, item in enumerate(st.session_state.history[:8]):
                exam = item.get("exam", "")
                icon = EXAM_ICONS.get(exam, "📄")
                q_text = item["question"][:50] + "..." if len(item["question"]) > 50 else item["question"]
                module = item.get("response", {}).get("module_used", "")

                module_label = ""
                if module == "solver":
                    module_label = "🟢 Solver"
                elif module == "writing_feedback":
                    module_label = "🟣 Writing"
                else:
                    module_label = "🔵 Explainer"

                with st.expander(f"{icon} {q_text}", expanded=False):
                    st.markdown(f"**Exam:** {exam.upper().replace('_', ' ')}")
                    st.markdown(f"**Module:** {module_label}")
                    st.markdown(f"**Q:** {item['question'][:200]}")

        st.markdown("---")

        # --- Tech Stack Info ---
        st.markdown("##### ⚙️ Powered By")
        st.markdown("""
        <div style="font-size: 0.78rem; color: #64748b; line-height: 1.8;">
            🧠 <strong>LLM:</strong> Groq Cloud (Llama 3)<br/>
            🔍 <strong>RAG:</strong> FAISS + Sentence Transformers<br/>
            🗄️ <strong>DB:</strong> SQLite + SQLAlchemy<br/>
            ⚡ <strong>API:</strong> FastAPI<br/>
            🎨 <strong>UI:</strong> Streamlit
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # --- Footer ---
        st.markdown("""
        <div style="text-align: center; font-size: 0.7rem; color: #475569; padding-top: 0.5rem;">
            ExamGPT India v1.0.0<br/>
            Built with ❤️ for Indian students
        </div>
        """, unsafe_allow_html=True)
