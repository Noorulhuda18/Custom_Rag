# DocuMind AI — Intelligent Document Assistant
#Demo 
https://customrag-jpbsqvv5s6gakcuxcnngma.streamlit.app/
A Streamlit + LangChain + OpenAI + FAISS RAG application for asking grounded questions about PDFs, Word files, spreadsheets, presentations, text, web/data files, and images.

## Features

- Session-based OpenAI API key
- Multi-document RAG
- FAISS vector search
- OpenAI `text-embedding-3-small`
- PDF page metadata
- Excel sheet-aware extraction using pandas
- PowerPoint slide metadata
- OCR for images
- OCR fallback for poorly extracted/scanned PDF pages
- Source previews
- Configurable model, temperature, chunk size, overlap, and Top-K
- Follow-up conversation context
- Premium Streamlit UI
- Friendly processing and error handling

## Supported formats

PDF, DOC, DOCX, TXT, MD, RTF, XLS, XLSX, CSV, TSV, PPT, PPTX, PNG, JPG, JPEG, WEBP, TIFF, BMP, HTML, XML, JSON.

## Architecture

`Upload → Parser/OCR → Clean/Split → OpenAI Embeddings → FAISS → Similarity Retrieval → Grounded Chat Answer → Sources`

## Installation

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

The Python package `pytesseract` is only a wrapper. Install the Tesseract OCR engine separately and make sure it is available on PATH.

Windows: install Tesseract OCR and restart the terminal after installation.

### 4. Run

```bash
streamlit run app.py
```

Open the local Streamlit URL and enter your own OpenAI API key.

## Security

- API keys are requested at runtime.
- The application stores the key only in `st.session_state`.
- Keys are not written to project files.
- Do not commit API keys to GitHub.
- `.env` and Streamlit secrets are ignored by `.gitignore`.

## GitHub

Create a repository, then:

```bash
git init
git add .
git commit -m "Initial DocuMind AI project"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Never replace `YOUR_REPOSITORY_URL` with a repository URL containing credentials or tokens.

## Streamlit deployment

Upload the repository to GitHub and deploy it through Streamlit Community Cloud. The application will show the API-key onboarding screen at runtime, so a personal OpenAI key does not need to be committed to the repository.

## Troubleshooting

### Tesseract not found
Install the Tesseract OCR engine and add its installation directory to PATH.

### PDF cannot be read
Make sure the PDF is not corrupted or password protected. Scanned pages may require a working Tesseract installation.

### Excel parsing fails
Verify that the workbook is not corrupted and that the required spreadsheet engine is installed.

### OpenAI errors
Check that the API key is valid and has access to the selected model and embeddings endpoint.

### FAISS installation problems on Windows
Use a compatible 64-bit Python version and recreate the virtual environment before reinstalling dependencies.

## Important note

The application is designed for document-grounded answers, but retrieval quality depends on the quality of extracted text, chunking, embeddings, and the uploaded documents. Always verify important information against the original source.
