APP_NAME = "DocuMind AI"

SUPPORTED_EXTENSIONS = [
    ".pdf", ".doc", ".docx", ".txt", ".md", ".rtf",
    ".xls", ".xlsx", ".csv", ".tsv",
    ".ppt", ".pptx",
    ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp",
    ".html", ".htm", ".xml", ".json",
]

DEFAULT_SETTINGS = {
    "model": "gpt-4o-mini",
    "temperature": 0.0,
    "chunk_size": 1000,
    "chunk_overlap": 150,
    "top_k": 4,
}
