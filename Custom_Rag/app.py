import os
import streamlit as st

from src.config import APP_NAME, SUPPORTED_EXTENSIONS
from src.document_processor import process_uploaded_files
from src.rag_chain import answer_question
from src.ui import inject_css, render_header, render_sidebar, render_sources, render_empty_state

st.set_page_config(page_title=APP_NAME, page_icon="📚", layout="wide")
inject_css()

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
    st.title("DocuMind AI")
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

    uploaded = st.file_uploader(
        "Drop files here",
        type=[x.lstrip(".") for x in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        help="PDF, Word, Excel, PowerPoint, text, web/data files and images."
    )

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

    if st.button("Clear Documents", use_container_width=True):
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
