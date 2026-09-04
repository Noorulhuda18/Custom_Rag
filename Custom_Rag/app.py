import os
import streamlit as st

from src.config import APP_NAME, SUPPORTED_EXTENSIONS
from src.document_processor import process_uploaded_files
from src.rag_chain import answer_question
from src.utils import format_size, file_icon

APP_DISPLAY_NAME = "NexaRAG"

def inject_css():
    st.markdown("""<style>
    .stApp { background:#e9f0f3; color:#14283d; }
    header[data-testid="stHeader"] { background:#14283d !important; }
    [data-testid="stToolbar"] { color:#ffffff; }
    section[data-testid="stSidebar"] { background:#10263b; border-right:1px solid #24435e; }
    section[data-testid="stSidebar"] > div { background:#10263b; padding:1rem .9rem 2rem; }
    section[data-testid="stSidebar"] * { color:#edf5f7; }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] small { color:#a9c2ce !important; }
    .block-container { max-width:1200px; padding-top:2rem; padding-bottom:3rem; }
    h1,h2,h3 { color:#14283d; letter-spacing:-.02em; }
    .eyebrow { color:#0c8c86; font-size:.72rem; font-weight:800; letter-spacing:.14em; margin-bottom:.6rem; }
    .onboarding-icon { font-size:3.5rem; margin-top:7vh; }
    .hero { background:#ffffff; border:1px solid #d3e0e4; border-radius:20px; padding:2.4rem; margin:1.5rem 0; box-shadow:0 14px 34px rgba(20,53,68,.1); }
    .hero h2 { font-size:2.2rem; margin:.2rem 0; }
    .hero p { color:#587080; font-size:1.05rem; }
    .doc-card { background:#18354d; border:1px solid #2b526d; border-radius:13px; padding:.75rem; margin:.5rem 0; color:#ffffff; }
    .doc-card small { color:#b7ccd5; }
    .source-card { background:#f6fafb; border:1px solid #d3e0e4; border-radius:12px; padding:.7rem; margin:.4rem 0; }
    .empty-card { background:#ffffff; border:1px solid #d3e0e4; border-radius:14px; padding:1.1rem; min-height:118px; box-shadow:0 8px 22px rgba(20,53,68,.07); }
    .empty-card strong { color:#14283d; display:block; margin-bottom:.4rem; }
    .empty-card span { color:#587080; font-size:.9rem; line-height:1.45; }
    .sidebar-panel { background:#18354d; border:1px solid #2b526d; border-radius:12px; padding:.8rem; margin:.7rem 0; }
    .sidebar-panel strong { color:#ffffff; display:block; margin-bottom:.35rem; }
    .sidebar-panel span { color:#b7ccd5; font-size:.84rem; line-height:1.5; }
    .stButton>button { border-radius:10px; border:1px solid #bfd1d7; background:#ffffff; color:#16344a; font-weight:700; }
    .stButton>button:hover { border-color:#0c8c86; color:#08746f; }
    .stButton>button[kind="primary"] { background:#0c8c86; color:white; border:0; }
    section[data-testid="stSidebar"] .stButton>button { background:#e7f4f2; color:#12384a; border:0; }
    section[data-testid="stSidebar"] .stButton>button:hover { background:#ffffff; color:#08746f; }
    [data-testid="stFileUploader"] { background:#d5eeec !important; border:2px dashed #4faaa7 !important; border-radius:14px; padding:.45rem !important; color:#14354a !important; }
    [data-testid="stFileUploaderDropzone"] { background:#d5eeec !important; border:0 !important; min-height:112px !important; }
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] section { color:#173f53 !important; }
    [data-testid="stFileUploader"] button { background:#0c716f !important; color:#ffffff !important; border:0 !important; box-shadow:none !important; font-weight:700 !important; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] { background:#18354d; border:1px solid #2b526d; border-radius:12px; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] svg { fill:#b7ccd5; }
    [data-testid="stMetric"] { background:#ffffff; border:1px solid #d3e0e4; border-radius:14px; padding:1rem; box-shadow:0 5px 16px rgba(20,53,68,.05); }
    [data-testid="stMetricLabel"] { color:#587080; }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small { color:#a9c2ce; }
    [data-testid="stChatMessage"] { border-radius:16px; }
    .ui-version { position:fixed; right:1rem; bottom:.7rem; z-index:9999; background:#244b7d; color:#fff; padding:.35rem .65rem; border-radius:999px; font-size:.72rem; font-weight:700; box-shadow:0 4px 12px rgba(20,35,60,.2); }
    </style>""", unsafe_allow_html=True)


def render_header():
    first, second, third = st.columns([4, 2, 1])
    with first:
        st.markdown(f"## 📚 {APP_DISPLAY_NAME}")
    with second:
        st.caption("Workspace")
    with third:
        if st.button("New chat"):
            st.session_state.messages = []
            st.rerun()


def render_sidebar():
    st.markdown("### Workspace")
    st.caption("Your private document intelligence hub")
    st.divider()
    st.markdown("**MODEL**")
    settings = st.session_state.settings
    models = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"]
    settings["model"] = st.selectbox("AI model", models, index=models.index(settings["model"]), label_visibility="collapsed")

    with st.expander("Retrieval settings", expanded=True):
        settings["chunk_size"] = st.slider("Chunk size", 500, 2000, settings["chunk_size"], 100)
        settings["chunk_overlap"] = st.slider("Chunk overlap", 0, 400, settings["chunk_overlap"], 50)
        settings["top_k"] = st.slider("Retrieved chunks", 2, 10, settings["top_k"])
        settings["temperature"] = st.slider("Answer temperature", 0.0, 1.0, settings["temperature"], 0.1)

    st.markdown("**SESSION**")
    session_left, session_right = st.columns(2)
    with session_left:
        if st.button("＋ New chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with session_right:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    if st.button("Change API key", use_container_width=True):
        st.session_state.api_key = ""
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("**DOCUMENT LIBRARY**")

    document_count = len(st.session_state.documents)
    chunk_count = sum(d["chunks"] for d in st.session_state.documents)
    st.markdown(
        f'<div class="doc-card"><b>Workspace snapshot</b><br>'
        f'<small>{document_count} document{"s" if document_count != 1 else ""} · {chunk_count} searchable chunks</small></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-panel"><strong>Quick actions</strong>'
        '<span>Upload files to build your library, then ask questions from the main workspace.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-panel"><strong>Supported content</strong>'
        '<span>PDF, Word, Excel, PowerPoint, text, web files, data files, and images with OCR.</span></div>',
        unsafe_allow_html=True,
    )

    for document in st.session_state.documents:
        st.markdown(
            f'<div class="doc-card">{file_icon(document["name"])} <b>{document["name"]}</b><br>'
            f'<small>{document["type"]} · {format_size(document["size"])}<br>✓ Indexed · {document["chunks"]} chunks</small></div>',
            unsafe_allow_html=True,
        )


def render_sources(sources):
    with st.expander(f"Sources ({len(sources)})"):
        for source in sources:
            location = ""
            if source.get("page") is not None:
                location = f"Page {source['page']}"
            elif source.get("sheet"):
                location = f"Sheet: {source['sheet']}"
            elif source.get("slide") is not None:
                location = f"Slide {source['slide']}"
            ocr = " · OCR extracted" if source.get("ocr") else ""
            st.markdown(
                f'<div class="source-card"><b>{file_icon(source["filename"])} {source["filename"]}</b>'
                f'<br><small>{location}{ocr}</small><br>{source["preview"]}</div>',
                unsafe_allow_html=True,
            )


def render_empty_state():
    st.markdown(
        '<div class="hero" style="text-align:center;margin-top:5rem;">'
        '<div style="font-size:3.5rem;">📚</div><h2>Ask your documents anything.</h2>'
        '<p>Upload one or more files and start exploring your information.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("#### A focused workspace for your files")
    cards = [
        ("Summarize faster", "Turn long reports into clear takeaways and concise briefs."),
        ("Find the details", "Ask for names, dates, figures, risks, or decisions across files."),
        ("Keep context close", "Answers stay grounded in your uploaded documents and sources."),
    ]
    columns = st.columns(3)
    for column, (title, description) in zip(columns, cards):
        with column:
            st.markdown(
                f'<div class="empty-card"><strong>{title}</strong><span>{description}</span></div>',
                unsafe_allow_html=True,
            )

st.set_page_config(page_title=APP_DISPLAY_NAME, page_icon="📚", layout="wide")
inject_css()
st.markdown('<div class="ui-version">NexaRAG · refreshed workspace</div>', unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "documents" not in st.session_state:
    st.session_state.documents = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "chunk_size": 1000,
        "chunk_overlap": 150,
        "top_k": 4,
    }

def api_key_screen():
    st.markdown('<div class="onboarding-icon">📚</div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">AI DOCUMENT INTELLIGENCE</div>', unsafe_allow_html=True)
    st.title(APP_DISPLAY_NAME)
    st.markdown("### Your private AI workspace for understanding documents.")
    st.write("Upload documents, spreadsheets, presentations and images, then ask questions using natural language.")
    key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)
    if st.button("Continue to Workspace →", type="primary", use_container_width=True):
        if not key.strip():
            st.error("Please enter your OpenAI API key.")
            return
        try:
            from langchain_openai import OpenAIEmbeddings
            OpenAIEmbeddings(model="text-embedding-3-small", api_key=key).embed_query("validate")
            st.session_state.api_key = key.strip()
            st.session_state.authenticated = True
            os.environ["OPENAI_API_KEY"] = st.session_state.api_key
            st.rerun()
        except Exception as e:
            st.error("The API key could not be validated. Please check the key and try again.")
    st.caption("Your key is kept only in this Streamlit session and is not written to disk by this application.")

if not st.session_state.authenticated:
    api_key_screen()
    st.stop()

os.environ["OPENAI_API_KEY"] = st.session_state.api_key
render_header()

with st.sidebar:
    uploaded = st.file_uploader(
        "UPLOAD DOCUMENTS",
        type=[x.lstrip(".") for x in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        help="PDF, Word, Excel, PowerPoint, text, web/data files and images."
    )

    st.caption("PDF · DOCX · XLSX · PPTX · TXT · Images")
    render_sidebar()

    if uploaded:
        signatures = [(f.name, f.size) for f in uploaded]
        if signatures != st.session_state.get("upload_signatures"):
            with st.spinner("Processing documents..."):
                try:
                    docs, vectorstore = process_uploaded_files(
                        uploaded,
                        api_key=st.session_state.api_key,
                        chunk_size=st.session_state.settings["chunk_size"],
                        chunk_overlap=st.session_state.settings["chunk_overlap"],
                    )
                    st.session_state.documents = docs
                    st.session_state.vectorstore = vectorstore
                    st.session_state.upload_signatures = signatures
                    st.session_state.messages = []
                    st.success("Documents indexed successfully.")
                except Exception:
                    st.error("Unable to process one or more files. Check that they are not corrupted, password protected, or unsupported.")

    if st.button("Clear document library", use_container_width=True):
        st.session_state.documents = []
        st.session_state.vectorstore = None
        st.session_state.upload_signatures = []
        st.session_state.messages = []
        st.rerun()

if not st.session_state.documents:
    render_empty_state()
    st.stop()

docs = st.session_state.documents
total_chunks = sum(d["chunks"] for d in docs)
total_pages = sum(d["pages"] for d in docs)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Documents", len(docs))
c2.metric("Pages / Units", total_pages)
c3.metric("Chunks", total_chunks)
c4.metric("Status", "Ready ✓")

st.markdown('<div class="hero"><div class="eyebrow">AI DOCUMENT INTELLIGENCE</div><h2>Talk to your documents.</h2><p>Upload your files and get accurate, source-backed answers with AI.</p></div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("#### Try asking")
    suggestions = [
        "Summarize the documents",
        "What are the key findings?",
        "Find the important numbers",
        "Compare these files",
        "What risks are mentioned?",
        "Explain this in simple terms",
    ]
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, use_container_width=True):
            st.session_state.pending_question = suggestion
            st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            render_sources(msg["sources"])

question = st.chat_input("Ask anything about your documents...")
question = question or st.session_state.pop("pending_question", None)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents..."):
            try:
                answer, sources = answer_question(
                    question,
                    st.session_state.vectorstore,
                    st.session_state.settings,
                    st.session_state.api_key,
                    st.session_state.messages[:-1],
                )
                st.markdown(answer)
                render_sources(sources)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })
            except Exception:
                st.error("Something went wrong while answering. Please try again.")
