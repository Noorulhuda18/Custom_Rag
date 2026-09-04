from langchain_community.vectorstores import FAISS

def build_vectorstore(documents, embeddings):
    if not documents:
        raise ValueError("No extractable content was found.")
    return FAISS.from_documents(documents, embeddings)
