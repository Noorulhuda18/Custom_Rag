import streamlit as st
from .config import DEFAULT_SETTINGS
from .utils import format_size, file_icon

def inject_css():
    st.markdown("""<style>
    .stApp { background:#f7f8fc; color:#172033; }
    [data-testid="stHeader"] { background:transparent; }
    section[data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #e8eaf0; }
    .block-container { max-width:1200px; padding-top:2rem; }
    h1,h2,h3 { color:#172033; letter-spacing:-.02em; }
    .eyebrow { color:#6257d9; font-size:.72rem; font-weight:800; letter-spacing:.14em; margin-bottom:.6rem; }
    .onboarding-icon { font-size:3.5rem; margin-top:7vh; }
    .hero { background:#fff; border:1px solid #e7e9f0; border-radius:20px; padding:2rem; margin:1.5rem 0; box-shadow:0 8px 28px rgba(25,30,50,.05); }
    .hero h2 { font-size:2.2rem; margin:.2rem 0; }
    .hero p { color:#687085; font-size:1.05rem; }
    .metric-card { background:#fff; border:1px solid #e7e9f0; border-radius:16px; padding:1rem; }
    .doc-card { background:#fafbfe; border:1px solid #e8eaf0; border-radius:13px; padding:.75rem; margin:.5rem 0; }
    .source-card { background:#fafbfe; border:1px solid #e7e9f0; border-radius:12px; padding:.7rem; margin:.4rem 0; }
    .stButton>button { border-radius:10px; border:1px solid #dfe2eb; font-weight:600; }
    .stButton>button[kind="primary"] { background:#5b50d6; color:white; border:0; }
    [data-testid="stFileUploader"] { background:#fff; border:2px dashed #d9dceb; border-radius:16px; padding:.5rem; }
    [data-testid="stChatMessage"] { border-radius:16px; }
    </style>""", unsafe_allow_html=True)

def render_header():
    a,b,c = st.columns([4,2,1])
    with a: st.markdown("## 📚 DocuMind AI")
    with b: st.caption("Workspace")
    with c:
        if st.button("New Session"):
            st.session_state.messages = []
            st.rerun()

def render_sidebar():
    st.markdown("### Your Documents")
    st.caption("Files currently available to AI")
    st.divider()
    st.markdown("**DOCUMENT LIBRARY**")

    settings = st.session_state.settings
    with st.expander("⚙ Settings"):
        settings["model"] = st.selectbox("AI Model", ["gpt-4o-mini","gpt-4.1-mini","gpt-4o"], index=["gpt-4o-mini","gpt-4.1-mini","gpt-4o"].index(settings["model"]))
        settings["temperature"] = st.slider("Temperature", 0.0, 1.0, settings["temperature"], 0.1)
        settings["chunk_size"] = st.slider("Chunk size", 500, 2000, settings["chunk_size"], 100)
        settings["chunk_overlap"] = st.slider("Chunk overlap", 0, 400, settings["chunk_overlap"], 50)
        settings["top_k"] = st.slider("Retrieved chunks", 2, 10, settings["top_k"])

    for d in st.session_state.documents:
        st.markdown(
            f'<div class="doc-card">{file_icon(d["name"])} <b>{d["name"]}</b><br>'
            f'<small>{d["type"]} • {format_size(d["size"])}<br>✓ Indexed • {d["chunks"]} chunks</small></div>',
            unsafe_allow_html=True
        )

def render_sources(sources):
    with st.expander(f"Sources ({len(sources)})"):
        for s in sources:
            location = ""
            if s.get("page") is not None: location = f"Page {s['page']}"
            elif s.get("sheet"): location = f"Sheet: {s['sheet']}"
            elif s.get("slide") is not None: location = f"Slide {s['slide']}"
            ocr = " • OCR extracted" if s.get("ocr") else ""
            st.markdown(
                f'<div class="source-card"><b>{file_icon(s["filename"])} {s["filename"]}</b>'
                f'<br><small>{location}{ocr}</small><br>{s["preview"]}</div>',
                unsafe_allow_html=True
            )

def render_empty_state():
    st.markdown('<div class="hero" style="text-align:center;margin-top:5rem;">'
                '<div style="font-size:3.5rem;">📚</div><h2>Ask your documents anything.</h2>'
                '<p>Upload one or more files and start exploring your information.</p></div>',
                unsafe_allow_html=True)
