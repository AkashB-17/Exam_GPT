"""
Document Upload Component — Lets users upload PDFs/TXT files for RAG.
"""
import streamlit as st
from frontend.utils import api_client


EXAM_NAMES = {
    "gate_cs": "GATE — CS",
    "gate_ece": "GATE — ECE",
    "cat": "CAT",
    "upsc_gs": "UPSC GS",
    "ielts": "IELTS",
    "gre": "GRE",
}


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def render_document_upload():
    """Render the document upload section with uploader and document list."""

    st.markdown("### 📄 Upload Your Study Material")
    st.markdown(
        '<p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">'
        'Upload PDFs or text files — they\'ll be chunked, embedded, and used alongside PYQs '
        'when answering your questions (RAG).'
        '</p>',
        unsafe_allow_html=True
    )

    # --- Upload Section ---
    with st.container():
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "md"],
            help="Supported: PDF, TXT, Markdown. Max 200 MB.",
            key="doc_uploader"
        )

        # Exam selector for the document
        exam_for_doc = st.selectbox(
            "Associate with exam",
            options=list(EXAM_NAMES.keys()),
            format_func=lambda x: EXAM_NAMES.get(x, x),
            index=list(EXAM_NAMES.keys()).index(st.session_state.get("selected_exam", "gate_cs")),
            key="doc_exam_select",
            help="The document will be indexed under this exam's knowledge base"
        )

        if st.button("📤 Upload & Index", key="upload_btn", use_container_width=True, disabled=uploaded_file is None):
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                filename = uploaded_file.name

                with st.spinner(f"📄 Processing '{filename}'... Extracting text, chunking, and embedding..."):
                    result = api_client.upload_document(exam_for_doc, file_bytes, filename)

                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success(
                        f"✅ **{result['filename']}** indexed successfully!\n\n"
                        f"**{result['num_chunks']}** chunks added to "
                        f"**{EXAM_NAMES.get(exam_for_doc, exam_for_doc)}** knowledge base."
                    )
                    st.rerun()

    st.markdown("---")

    # --- Uploaded Documents List ---
    _render_document_list()


def _render_document_list():
    """Render the list of uploaded documents with delete buttons."""
    st.markdown("##### 📚 Your Uploaded Documents")

    docs = api_client.list_documents()

    if not docs:
        st.markdown(
            '<div style="text-align: center; padding: 2rem 1rem; color: #64748b; font-size: 0.9rem;">'
            '<div style="font-size: 2rem; margin-bottom: 0.5rem;">📂</div>'
            'No documents uploaded yet.<br/>'
            '<span style="font-size: 0.8rem;">Upload PDFs or text files to enhance AI answers with your own material.</span>'
            '</div>',
            unsafe_allow_html=True
        )
        return

    for doc in docs:
        status_icon = "✅" if doc["status"] == "indexed" else "⏳" if doc["status"] == "processing" else "❌"
        exam_label = EXAM_NAMES.get(doc["exam"], doc["exam"])
        size_label = _format_size(doc.get("file_size", 0))

        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f'<div class="glass-card" style="padding: 1rem; margin-bottom: 0.5rem;">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<div>'
                f'<strong>{status_icon} {doc["filename"]}</strong><br/>'
                f'<span style="font-size: 0.78rem; color: #64748b;">'
                f'{exam_label} • {doc.get("num_chunks", 0)} chunks • {size_label}'
                f'</span>'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            if st.button("🗑️", key=f"del_{doc['id']}", help=f"Delete {doc['filename']}"):
                with st.spinner("Deleting..."):
                    result = api_client.delete_document(doc["id"])
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.toast(f"🗑️ Deleted '{doc['filename']}'", icon="✅")
                    st.rerun()

        if doc["status"] == "error" and doc.get("error_message"):
            st.caption(f"⚠️ Error: {doc['error_message']}")
