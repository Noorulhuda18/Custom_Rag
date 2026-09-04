def format_size(size):
    if size < 1024: return f"{size} B"
    if size < 1024**2: return f"{size/1024:.1f} KB"
    if size < 1024**3: return f"{size/1024**2:.1f} MB"
    return f"{size/1024**3:.1f} GB"

def file_icon(filename):
    ext = filename.lower().rsplit(".", 1)[-1]
    return {
        "pdf": "📕", "doc": "📘", "docx": "📘",
        "xls": "📊", "xlsx": "📊", "csv": "📊", "tsv": "📊",
        "ppt": "📙", "pptx": "📙",
        "png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️",
        "webp": "🖼️", "tiff": "🖼️", "bmp": "🖼️",
    }.get(ext, "📄")
