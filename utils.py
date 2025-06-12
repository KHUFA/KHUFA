import os
import subprocess
import fitz  # pymupdf
from PIL import Image

def convert_and_get_page_count(path):
    base_name = os.path.splitext(os.path.basename(path))[0]
    pdf_path = f"files/{base_name}.pdf"

    ext = os.path.splitext(path)[-1].lower()

    # DOC, DOCX → PDF через LibreOffice
    if ext in ['.doc', '.docx']:
        libre_path = r"C:\Program Files\LibreOffice\program\soffice.exe"  # проверь этот путь!
        subprocess.run([libre_path, '--headless', '--convert-to', 'pdf', '--outdir', 'files', path], check=True)

    # JPG, PNG → PDF через Pillow
    elif ext in ['.jpg', '.jpeg', '.png']:
        image = Image.open(path)
        image.convert("RGB").save(pdf_path)

    # Если уже PDF — просто возвращаем путь
    elif ext == '.pdf':
        pdf_path = path

    else:
        raise ValueError("Неподдерживаемый тип файла")

    # Считаем страницы
    doc = fitz.open(pdf_path)
    pages = len(doc)
    doc.close()

    return pdf_path, pages
