import os
import streamlit as st

from src.config import APP_NAME, SUPPORTED_EXTENSIONS
from src.document_processor import process_uploaded_files
from src.rag_chain import answer_question
from src.utils import format_size, file_icon

APP_DISPLAY_NAME = "NexaRAG"

def inject_css():
    st.markdown("""<style>
    .stApp { background:#0b1724; color:#e8f1f5; }
    header[data-testid="stHeader"] { background:#07111c !important; }
    [data-testid="stToolbar"] { color:#ffffff; }
    section[data-testid="stSidebar"] { background:#081722; border-right:1px solid #234258; }
    section[data-testid="stSidebar"] > div { background:#081722; padding:1rem .9rem 2rem; }
    section[data-testid="stSidebar"] * { color:#edf5f7; }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] small { color:#a9c2ce !important; }
    .block-container { max-width:1200px; padding-top:2rem; padding-bottom:3rem; }
    h1,h2,h3,h4,h5,h6 { color:#f2f8fa; letter-spacing:-.02em; }
    .eyebrow { color:#0c8c86; font-size:.72rem; font-weight:800; letter-spacing:.14em; margin-bottom:.6rem; }
    .onboarding-icon { font-size:3.5rem; margin-top:7vh; }
    .hero { background:#142b3d; border:1px solid #2c5065; border-radius:20px; padding:2.4rem; margin:1.5rem 0; box-shadow:0 14px 34px rgba(0,0,0,.25); }
    .hero h2 { font-size:2.2rem; margin:.2rem 0; }
    .hero p { color:#b6cbd4; font-size:1.05rem; }
    .doc-card { background:#142f45; border:1px solid #315970; border-radius:13px; padding:.75rem; margin:.5rem 0; color:#f2f8fa; }
    .doc-card small { color:#b7ccd5; }
    .source-card { background:#142b3d; border:1px solid #31566b; border-radius:12px; padding:.7rem; margin:.4rem 0; color:#e8f1f5; }
    .empty-card { background:#142b3d; border:1px solid #31566b; border-radius:14px; padding:1.1rem; min-height:138px; box-shadow:0 8px 22px rgba(0,0,0,.2); }
    .empty-card strong { color:#f2f8fa; display:block; margin-bottom:.4rem; }
    .empty-card span { color:#b6cbd4; font-size:.9rem; line-height:1.45; }
    .sidebar-panel { background:#142f45; border:1px solid #315970; border-radius:12px; padding:.8rem; margin:.7rem 0; }
    .sidebar-panel strong { color:#ffffff; display:block; margin-bottom:.35rem; }
    .sidebar-panel span { color:#b7ccd5; font-size:.84rem; line-height:1.5; }
    .stButton>button { border-radius:10px; border:1px solid #42677c; background:#19384d; color:#edf6f8; font-weight:700; }
    .stButton>button:hover { border-color:#34c4b5; color:#ffffff; background:#21475d; }
    .stButton>button[kind="primary"] { background:#0c8c86; color:white; border:0; }
    section[data-testid="stSidebar"] .stButton>button { background:#17384d; color:#edf6f8; border:1px solid #315970; }
    section[data-testid="stSidebar"] .stButton>button:hover { background:#ffffff; color:#08746f; }
    [data-testid="stFileUploader"] { background:#1b4a5d !important; border:2px solid #4bd5c5 !important; border-radius:18px; padding:.7rem !important; color:#ffffff !important; box-shadow:0 10px 24px rgba(0,0,0,.22); }
    [data-testid="stFileUploaderDropzone"] { background:#1b4a5d !important; border:0 !important; min-height:112px !important; }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] * { color:#dceff1 !important; }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button { color:#ffffff !important; }
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] section, [data-testid="stFileUploader"] p { color:#ffffff !important; opacity:1 !important; }
    [data-testid="stFileUploader"] button { background:#4bd5c5 !important; color:#08202d !important; border:0 !important; box-shadow:none !important; font-weight:800 !important; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] { background:#102b40; border:1px solid #315970; border-radius:12px; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] svg { fill:#b7ccd5; }
    [data-testid="stMetric"] { background:#142b3d; border:1px solid #31566b; border-radius:14px; padding:1rem; box-shadow:0 5px 16px rgba(0,0,0,.2); }
    [data-testid="stMetricLabel"] { color:#b6cbd4; }
    [data-testid="stMetricValue"] { color:#f2f8fa; }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div { background:#142f45; border-color:#42677c; color:#56b9e8; }
    [data-baseweb="select"] *, [data-baseweb="input"] *, [data-baseweb="textarea"] * { color:#f2f8fa !important; }
    section[data-testid="stSidebar"] [data-baseweb="select"] *, section[data-testid="stSidebar"] [data-baseweb="select"] input { color:#0b1724 !important; }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"],
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div > div { background:#163c52 !important; border:1px solid #4bd5c5 !important; color:#ffffff !important; }
    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-baseweb="select"] div,
    section[data-testid="stSidebar"] [data-baseweb="select"] input { background:#163c52 !important; color:#ffffff !important; }
    [data-baseweb="select"] svg { fill:#b9d2da !important; }
    [data-baseweb="select"] [role="combobox"] { background:#142f45 !important; color:#f2f8fa !important; }
    [data-baseweb="select"] [role="combobox"] span { color:#ffffff !important; }
    section[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"] span { color:#ffffff !important; }
    [data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="menu"] ul { background:#e8f0f3 !important; border:1px solid #6d9caf !important; }
    [role="listbox"] { background:#e8f0f3 !important; }
    [role="option"], [data-baseweb="menu"] li { background:#e8f0f3 !important; color:#0b1724 !important; }
    [role="option"] *, [data-baseweb="menu"] li * { color:#0b1724 !important; }
    [role="option"]:hover, [role="option"][aria-selected="true"], [data-baseweb="menu"] li:hover { background:#c8e0e8 !important; color:#0b1724 !important; }
    [role="option"]:hover *, [role="option"][aria-selected="true"] *, [data-baseweb="menu"] li:hover * { color:#0b1724 !important; }
    [data-testid="stExpander"] p, [data-testid="stExpander"] label { color:#e8f1f5; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary:focus { background:#102b40 !important; color:#e8f1f5 !important; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary span { color:#e8f1f5 !important; }
    [data-testid="stSlider"] [data-testid="stMarkdownContainer"] p { color:#d3e4e9; }
    [data-testid="stChatInput"] { background:#142f45; border-color:#42677c; }
    [data-testid="stChatInput"] textarea { color:#f2f8fa !important; }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small { color:#a9c2ce; }
    [data-testid="stChatMessage"] { border-radius:16px; }
    .brand-lockup { display:flex; align-items:center; gap:.7rem; margin:.2rem 0 1.4rem; }
    .brand-mark { width:42px; height:42px; border-radius:12px; display:grid; place-items:center; background:#0c8c86; color:#ffffff; font-size:1.35rem; box-shadow:0 7px 16px rgba(12,140,134,.22); }
    .brand-name { color:#f2f8fa; font-size:1.55rem; font-weight:800; letter-spacing:-.03em; }
    .workspace-card { background:#dbe9ed; border:1px solid #8eabb6; border-radius:16px; padding:1.15rem; min-height:138px; margin:0 .35rem 1rem; box-shadow:0 8px 20px rgba(0,0,0,.18); }
    .workspace-card .card-icon { color:#087c79; font-size:1.5rem; margin-bottom:.65rem; }
    .workspace-card strong { color:#102d42; display:block; margin-bottom:.35rem; }
    .workspace-card span { color:#38596b; font-size:.88rem; line-height:1.45; }
    .upload-panel { max-width:760px; margin:2rem auto 0; background:#102b40; border:1px solid #315970; border-radius:16px; padding:.8rem 1rem .7rem; box-shadow:0 10px 26px rgba(0,0,0,.2); }
    .upload-panel h3 { margin:0 0 .15rem; color:#f2f8fa; font-size:1rem; }
    .upload-panel p { margin:0 0 .55rem; color:#b6cbd4; font-size:.85rem; }
    .main-uploader { max-width:760px; margin:0 auto; }
    .main-uploader [data-testid="stFileUploader"] { background:#1b4a5d !important; border:2px solid #4bd5c5 !important; border-radius:18px; min-height:112px; padding:.7rem !important; box-shadow:0 10px 24px rgba(0,0,0,.22); }
    .main-uploader [data-testid="stFileUploaderDropzone"] { background:#1b4a5d !important; min-height:102px !important; }
    .main-uploader [data-testid="stFileUploader"] *, .main-uploader [data-testid="stFileUploader"] p,
    .main-uploader [data-testid="stFileUploader"] span, .main-uploader [data-testid="stFileUploader"] small,
    .main-uploader [data-testid="stFileUploader"] label { color:#ffffff !important; opacity:1 !important; }
    .main-uploader [data-testid="stFileUploader"] button { background:#0c8c86 !important; color:#ffffff !important; }
    .ui-version { position:fixed; right:1rem; bottom:.7rem; z-index:9999; background:#244b7d; color:#fff; padding:.35rem .65rem; border-radius:999px; font-size:.72rem; font-weight:700; box-shadow:0 4px 12px rgba(20,35,60,.2); }
    </style>""", unsafe_allow_html=True)


def render_header():
    st.markdown(
        f'<div class="brand-lockup"><div class="brand-mark">✦</div>'
        f'<div class="brand-name">{APP_DISPLAY_NAME}</div></div>',
        unsafe_allow_html=True,
    )


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
        ("✦", "Summarize faster", "Turn long reports into clear takeaways and concise briefs."),
        ("⌕", "Find the details", "Ask for names, dates, figures, risks, or decisions across files."),
        ("↔", "Compare documents", "Surface differences, trends, and agreements across files."),
        ("✓", "Source-backed answers", "See where each answer came from with page and file context."),
        ("▦", "Organize knowledge", "Keep PDFs, spreadsheets, slides, and images in one workspace."),
        ("⌁", "Ask naturally", "Use follow-up questions to explore your documents conversationally."),
    ]
    columns = st.columns(3)
    for index, (icon, title, description) in enumerate(cards):
        column = columns[index % 3]
        with column:
            st.markdown(
                f'<div class="workspace-card"><div class="card-icon">{icon}</div>'
                f'<strong>{title}</strong><span>{description}</span></div>',
                unsafe_allow_html=True,
            )


def render_upload_area():
    st.markdown(
        '<div class="upload-panel"><h3>Add documents</h3>'
        '<p>Upload files to start asking source-backed questions.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="main-uploader">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "UPLOAD DOCUMENTS",
        type=[extension.lstrip(".") for extension in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        help="PDF, Word, Excel, PowerPoint, text, web/data files and images.",
    )
    st.caption("PDF · DOCX · XLSX · PPTX · TXT · Images")
    st.markdown('</div>', unsafe_allow_html=True)
    return uploaded_files


def process_uploads(uploaded_files):
    if not uploaded_files:
        return
    signatures = [(file.name, file.size) for file in uploaded_files]
    if signatures == st.session_state.get("upload_signatures"):
        return
    with st.spinner("Processing documents..."):
        try:
            documents, vectorstore = process_uploaded_files(
                uploaded_files,
                api_key=st.session_state.api_key,
                chunk_size=st.session_state.settings["chunk_size"],
                chunk_overlap=st.session_state.settings["chunk_overlap"],
            )
            st.session_state.documents = documents
            st.session_state.vectorstore = vectorstore
            st.session_state.upload_signatures = signatures
            st.session_state.messages = []
            st.success("Documents indexed successfully.")
        except Exception:
            st.error("Unable to process one or more files. Check that they are not corrupted, password protected, or unsupported.")

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
    render_sidebar()

    if st.button("Clear document library", use_container_width=True):
        st.session_state.documents = []
        st.session_state.vectorstore = None
        st.session_state.upload_signatures = []
        st.session_state.messages = []
        st.rerun()

if not st.session_state.documents:
    render_empty_state()
    process_uploads(render_upload_area())
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

process_uploads(render_upload_area())

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
