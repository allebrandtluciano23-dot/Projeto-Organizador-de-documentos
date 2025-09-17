import fitz  # PyMuPDF

def read_pdf(pdf_path):
    """Lê todo o texto do PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    FirstPageText = doc[0].get_text()
    for page in doc:
        text += page.get_text() + "\n"
    return FirstPageText, text

def extract_title(pdf_path):
    """Tenta extrair título: metadados → maior fonte → primeira linha"""
    doc = fitz.open(pdf_path)
    page = doc[0]

    title = doc.metadata.get("title", None)
    if title:
        return title

    blocks = page.get_text("dict")["blocks"]
    lines = []
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if text:
                        lines.append((s["size"], text))
    if lines:
        lines.sort(reverse=True)
        return lines[0][1]

    text = page.get_text()
    first_line = text.split("\n")[0].strip() if text else "Sem título"
    return first_line
