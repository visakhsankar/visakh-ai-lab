import tempfile

from pypdf import PdfReader


def extract_text(uploaded_file) -> str:
    """Extract plain text from a PDF or TXT uploaded file."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return _from_pdf(uploaded_file)
    if name.endswith(".txt"):
        uploaded_file.seek(0)
        return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""


def _from_pdf(uploaded_file) -> str:
    uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    reader = PdfReader(tmp_path)
    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
    return "\n".join(pages)
