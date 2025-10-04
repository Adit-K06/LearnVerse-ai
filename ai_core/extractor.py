import pdfplumber

def clean_whitespace(s):
    """Cleans up extra whitespace from a string."""
    return " ".join(s.split())

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return clean_whitespace(text)