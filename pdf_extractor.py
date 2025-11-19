import pdfplumber

def extract_text(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

def clean_text(text):
    return " ".join(text.split())