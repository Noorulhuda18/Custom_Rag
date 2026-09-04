from langchain_text_splitters import RecursiveCharacterTextSplitter
from .document_loader import load_file
from .embeddings import create_embeddings
from .vector_store import build_vectorstore

def process_uploaded_files(uploaded_files, api_key, chunk_size=1000, chunk_overlap=150):
    all_docs = []
    summaries = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    for uploaded in uploaded_files:
        docs = load_file(uploaded)
        chunks = splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata["filename"] = uploaded.name
        all_docs.extend(chunks)

        pages = len(set(
            d.metadata.get("page") or d.metadata.get("sheet") or d.metadata.get("slide") or "unit"
            for d in chunks
        ))
        summaries.append({
            "name": uploaded.name,
            "type": uploaded.name.rsplit(".", 1)[-1].upper(),
            "size": uploaded.size,
            "pages": pages,
            "chunks": len(chunks),
        })

    embeddings = create_embeddings(api_key)
    vectorstore = build_vectorstore(all_docs, embeddings)
    return summaries, vectorstore
