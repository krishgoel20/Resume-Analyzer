from pypdf import PdfReader
from docx import Document
import io

def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(uploaded_file) -> str:
    doc = Document(uploaded_file)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text

def extract_text(uploaded_file) -> str:
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a .pdf or .docx file.")