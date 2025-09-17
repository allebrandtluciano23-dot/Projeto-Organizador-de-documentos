import os
from .reader import read_pdf, extract_title
from .extractor import extract_metadata
from .database import save_to_db, create_db
from .KeywordMatcher import Matching

# Caminho do banco de dados (por exemplo na raiz do projeto)
db_path = os.path.join(os.getcwd(), "documentos.db")

# Garante que o banco existe
create_db(db_path)

def process_document(pdf_path: str):
    # Lê o texto do PDF
    FirstPageText, full_text = read_pdf(pdf_path)

    # Tenta classificar com palavras-chave
    DestinationFolder, title = Matching(FirstPageText)
    if DestinationFolder == "SemPasta":
        title = extract_title(pdf_path)

    # Extrai metadados do texto completo
    metadata = extract_metadata(full_text, title)
    metadata["folder"] = DestinationFolder

    # Salva no banco
    save_to_db(metadata, pdf_path, db_path, full_text=full_text)

    return metadata
