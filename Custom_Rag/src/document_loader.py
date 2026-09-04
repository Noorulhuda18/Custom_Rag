import json
import os
import tempfile
from pathlib import Path

import pandas as pd
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader, BSHTMLLoader,
)
from langchain_core.documents import Document

from .ocr import ocr_image

def _save(uploaded):
    ext = Path(uploaded.name).suffix.lower()
    f = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    f.write(uploaded.getvalue())
    f.close()
    return f.name

def _base_meta(name, ext):
    return {"source": name, "filename": name, "file_type": ext.lstrip(".").upper()}

def load_file(uploaded):
    name = uploaded.name
    ext = Path(name).suffix.lower()
    path = _save(uploaded)
    base = _base_meta(name, ext)
    try:
        if ext == ".pdf":
            docs = PyPDFLoader(path).load()
            for i, d in enumerate(docs):
                d.metadata.update(base)
                d.metadata["page"] = i + 1
            # OCR fallback for pages with little/no extracted text
            for i, d in enumerate(docs):
                if len(d.page_content.strip()) < 30:
                    try:
                        import fitz
                        page = fitz.open(path)[i]
                        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                        img = pix.tobytes("png")
                        ocr_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                        ocr_tmp.write(img); ocr_tmp.close()
                        try:
                            text = ocr_image(ocr_tmp.name)
                        finally:
                            os.unlink(ocr_tmp.name)
                        if text:
                            d.page_content = text
                            d.metadata["OCR"] = True
                    except Exception:
                        pass
            return docs

        if ext in {".docx", ".doc"}:
            docs = UnstructuredWordDocumentLoader(path).load()
            for d in docs: d.metadata.update(base)
            return docs

        if ext in {".pptx", ".ppt"}:
            docs = UnstructuredPowerPointLoader(path).load()
            for i, d in enumerate(docs):
                d.metadata.update(base); d.metadata["slide"] = i + 1
            return docs

        if ext in {".xlsx", ".xls", ".csv", ".tsv"}:
            if ext in {".csv", ".tsv"}:
                df = pd.read_csv(path, sep="\t" if ext == ".tsv" else ",")
                sheet = Path(name).stem
                text = df.to_csv(index=True)
                return [Document(
                    page_content=f"Sheet: {sheet}\n{text}",
                    metadata={**base, "sheet": sheet, "rows": len(df)}
                )]
            book = pd.ExcelFile(path)
            result = []
            for sheet in book.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet)
                text = df.to_csv(index=True)
                result.append(Document(
                    page_content=f"Workbook: {name}\nSheet: {sheet}\n{text}",
                    metadata={**base, "sheet": sheet, "rows": len(df)}
                ))
            return result

        if ext in {".txt", ".md"}:
            docs = TextLoader(path, encoding="utf-8", autodetect_encoding=True).load()
            for d in docs: d.metadata.update(base)
            return docs

        if ext == ".rtf":
            from striprtf.striprtf import rtf_to_text
            raw = Path(path).read_text(encoding="utf-8", errors="ignore")
            return [Document(page_content=rtf_to_text(raw), metadata=base)]

        if ext in {".html", ".htm"}:
            docs = BSHTMLLoader(path).load()
            for d in docs: d.metadata.update(base)
            return docs

        if ext == ".xml":
            text = Path(path).read_text(encoding="utf-8", errors="ignore")
            return [Document(page_content=text, metadata=base)]

        if ext == ".json":
            raw = Path(path).read_text(encoding="utf-8", errors="ignore")
            data = json.loads(raw)
            return [Document(page_content=json.dumps(data, indent=2, ensure_ascii=False), metadata=base)]

        if ext in {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}:
            text = ocr_image(path)
            return [Document(page_content=text, metadata={**base, "OCR": True})]

        raise ValueError(f"Unsupported file type: {ext}")
    finally:
        try: os.unlink(path)
        except OSError: pass
