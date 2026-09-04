from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from .prompts import RAG_PROMPT

def _format_doc(doc):
    m = doc.metadata
    parts = [m.get("filename", m.get("source", "Unknown"))]
    if m.get("page") is not None: parts.append(f"Page {m['page']}")
    if m.get("sheet"): parts.append(f"Sheet {m['sheet']}")
    if m.get("slide") is not None: parts.append(f"Slide {m['slide']}")
    if m.get("OCR"): parts.append("OCR")
    return f"[Source: {' — '.join(parts)}]\n{doc.page_content}"

def answer_question(question, vectorstore, settings, api_key, history=None):
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings["top_k"]})
    retrieved = retriever.invoke(question)
    context = "\n\n".join(_format_doc(d) for d in retrieved)

    history_text = ""
    if history:
        recent = history[-6:]
        history_text = "\nRecent conversation for reference resolution:\n" + "\n".join(
            f"{m['role']}: {m['content']}" for m in recent
        )

    prompt = RAG_PROMPT.format_messages(
        context=context + history_text,
        question=question,
    )
    llm = ChatOpenAI(
        model=settings["model"],
        temperature=settings["temperature"],
        api_key=api_key,
    )
    answer = (llm | StrOutputParser()).invoke(prompt)

    sources = []
    seen = set()
    for d in retrieved:
        m = d.metadata
        key = (m.get("filename"), m.get("page"), m.get("sheet"), m.get("slide"))
        if key in seen: continue
        seen.add(key)
        sources.append({
            "filename": m.get("filename", m.get("source", "Unknown")),
            "file_type": m.get("file_type", ""),
            "page": m.get("page"),
            "sheet": m.get("sheet"),
            "slide": m.get("slide"),
            "ocr": bool(m.get("OCR")),
            "preview": d.page_content[:500],
        })
    return answer, sources
