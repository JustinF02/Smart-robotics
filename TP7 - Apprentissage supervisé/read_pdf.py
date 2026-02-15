from pypdf import PdfReader
import sys

filename = '4_Apprentissage_supervise.pdf'

try:
    reader = PdfReader(filename)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
except Exception as e:
    print(f"Error reading PDF: {e}")
