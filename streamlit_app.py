"""
e-GP Manual Assistant (streamlit_app.py).
Interactive, cited chatbot grounded in the official Bangladesh e-GP Procuring Entity User Manual.
Ready for local execution and Streamlit Community Cloud.
"""
import os
import sys
import requests
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Sync Streamlit Cloud secrets into environment variables
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, str):
                os.environ.setdefault(k, v)
except Exception:
    pass

from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.services.faiss_service import faiss_service

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="e-GP Manual Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .status-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 15px;
        font-size: 0.88rem;
        color: #166534;
    }
    .source-box {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 12px;
        background-color: #e0f2fe;
        color: #0369a1;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Initialize Chat Messages in Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hey there! 👋 I'm **Proca**, your friendly e-GP Manual Assistant.\n\n"
                "I've read the entire **e-GP Procuring Entity User Manual (543 pages)** so you don't have to! "
                "Ask me anything about:\n\n"
                "- 🔑 Account setup & login\n"
                "- 📋 Annual Procurement Plan (APP)\n"
                "- 📢 Tender creation & evaluation\n"
                "- 🔄 Workflow approvals\n"
                "- 📑 Contract management\n\n"
                "Or pick a quick question from the sidebar to get started! 😊"
            ),
            "sources": []
        }
    ]

# 4. Automatic Backend Detection (Supports FastAPI or direct local mode)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
backend_online = False
total_chunks = 0

try:
    r = requests.get(f"{BACKEND_URL}/api/chat/health", timeout=1.2)
    if r.status_code == 200:
        backend_online = True
        total_chunks = r.json().get("total_chunks", 0)
except Exception:
    backend_online = False

if not backend_online:
    retrieval_service.load_index_if_needed()
    total_chunks = len(faiss_service.metadata)

# 5. Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/procurement.png", width=56)
    st.title("e-GP Guide")

    st.markdown(f"""
    <div class="status-card">
        <strong>🟢 System Ready</strong><br/>
        📖 Manual: Procuring Entity User<br/>
        📑 Verified Chunks: <strong>{total_chunks or 1188}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💡 Quick Questions")
    sample_questions = [
        ("🔑 How to open / create a PE account?", "tell me how to open an account"),
        ("🚪 How does a user log in to e-GP?", "How does a Procuring Entity user login to the e-GP portal?"),
        ("📋 Annual Procurement Plan (APP) guide", "What is the procedure for Annual Procurement Plan (APP) preparation?"),
        ("🔄 How to view Approved Workflow?", "how to view approved workflow"),
        ("⚖️ Proposal evaluation procedure", "What are the steps for technical and financial proposal evaluation?"),
    ]

    for label, query_text in sample_questions:
        if st.button(label, use_container_width=True):
            st.session_state.pending_question = query_text

    st.markdown("---")
    st.markdown("### 📷 Upload Screenshot (Optional)")
    uploaded_image = st.file_uploader(
        "Have an e-GP portal screenshot or error?",
        type=["png", "jpg", "jpeg"],
        help="Upload an image to search visual manual sections."
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Query Image", use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# 6. Main Header
st.markdown('<div class="main-title">📋 e-GP Manual Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Instant, cited guidance from the official electronic Government Procurement manuals.</div>', unsafe_allow_html=True)

# Helper: resolve image path to absolute
def resolve_image_path(img_path: str) -> str:
    """Convert relative image path to absolute using ROOT_DIR."""
    if not img_path:
        return ""
    # Already absolute
    if os.path.isabs(img_path):
        return img_path
    # Normalize Windows backslashes
    img_path = img_path.replace("\\", "/")
    return os.path.join(ROOT_DIR, img_path)

def render_sources(sources: list):
    """Render source citation boxes with page screenshots."""
    # Deduplicate by page number (keep first occurrence)
    seen_pages = set()
    unique_sources = []
    for s in sources:
        pg = s.get("page")
        if pg not in seen_pages:
            seen_pages.add(pg)
            unique_sources.append(s)

    for s in unique_sources:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="source-box">
                <span class="badge">📄 {s['source']}</span><br/>
                <span class="badge">Page {s['page']}</span>
                <p style="margin-top: 6px; font-style: italic; font-size:0.82rem;">"{s.get('snippet', '')[:180]}..."</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            img_path = resolve_image_path(s.get("image_path", ""))
            if img_path and os.path.exists(img_path):
                st.image(img_path, caption=f"📖 Page {s['page']}", use_container_width=True)
            else:
                st.info(f"📄 Page {s['page']} — screenshot not available locally.")

# 7. Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 View Official Manual Pages & Screenshots ({len(message['sources'])} citations)"):
                render_sources(message["sources"])

# 8. User Input & Query Handling
user_prompt = st.chat_input("Ask any question about e-GP (e.g., account setup, login, APP, tender submission, evaluation)...")
if "pending_question" in st.session_state and st.session_state.pending_question:
    user_prompt = st.session_state.pending_question
    st.session_state.pending_question = None

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching official e-GP manual..."):
            answer = ""
            sources = []

            # Try FastAPI backend first
            used_backend = False
            if backend_online:
                try:
                    payload = {"question": user_prompt, "top_k": 4}
                    resp = requests.post(f"{BACKEND_URL}/api/chat", json=payload, timeout=15)
                    if resp.status_code == 200:
                        data = resp.json()
                        answer = data.get("answer", "")
                        sources = data.get("sources", [])
                        used_backend = True
                except Exception:
                    used_backend = False

            # Direct fallback
            if not used_backend:
                img_bytes = uploaded_image.getvalue() if uploaded_image else None
                context, raw_sources = retrieval_service.retrieve(user_prompt, top_k=4, image=img_bytes)
                answer = llm_service.generate_answer(user_prompt, context, image=img_bytes)
                sources = raw_sources

            st.markdown(answer)
            if sources:
                with st.expander(f"📚 View Official Manual Pages & Screenshots ({len(sources)} citations)"):
                    render_sources(sources)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
