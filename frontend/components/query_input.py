import streamlit as st
from frontend.utils import api_client


PLACEHOLDER_EXAMPLES = {
    "gate_cs": "E.g., In a system with 3 processes and 4 resource types, is the system in a safe state using Banker's Algorithm?",
    "gate_ece": "E.g., Find the transfer function of a second-order system with damping ratio 0.5 and natural frequency 10 rad/s.",
    "cat": "E.g., A train 150m long passes a pole in 15 seconds. Find the speed of the train in km/hr.",
    "upsc_gs": "E.g., What is the significance of the 73rd Constitutional Amendment Act?",
    "ielts": "E.g., Check my essay: Some people think environmental problems are too big for individuals to solve...",
    "gre": "E.g., If 3x + 5 = 20, what is the value of 6x + 10?",
}


def render_query_input():
    """Render the query input area with contextual placeholder."""
    exam = st.session_state.selected_exam
    placeholder = PLACEHOLDER_EXAMPLES.get(exam, "Type your question here...")

    with st.form(key="query_form", clear_on_submit=False):
        question = st.text_area(
            "📖 Ask your question",
            height=150,
            placeholder=placeholder,
            help="Paste a problem to solve, a concept to explain, or an essay to evaluate"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            submit_button = st.form_submit_button(
                label="🚀 Get Answer",
                use_container_width=True
            )
        with col2:
            pass  # Space for future buttons

        if submit_button:
            if not question.strip():
                st.warning("⚠️ Please enter a question before submitting.")
                return

            if not st.session_state.get("backend_online", True):
                st.error("❌ Backend is offline. Start it with: `uvicorn backend.main:app --port 8000`")
                return

            st.session_state.is_loading = True

            with st.spinner("🔍 Analyzing question and consulting Previous Year Questions..."):
                response = api_client.submit_query(exam, question)

                if "error" in response:
                    st.error(f"❌ {response['error']}")
                    st.session_state.current_response = None
                else:
                    st.session_state.current_response = response

                    # Add to history
                    st.session_state.history.insert(0, {
                        "exam": exam,
                        "question": question,
                        "response": response
                    })

            st.session_state.is_loading = False
            st.rerun()
