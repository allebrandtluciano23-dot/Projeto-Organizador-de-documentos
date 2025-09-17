import re

def extract_metadata(text: str, title: str):
    """Extração de data e organização do texto."""
    metadata = {}
    metadata["title"] = title

    # Procura datas no formato dd/mm/yyyy
    date_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    metadata["date"] = date_match.group(1) if date_match else None

    # Procura por palavras como "Prefeitura", "Ministério", "Empresa", "Instituto"
    org_match = re.search(r"\b(Prefeitura|Ministério|Empresa|Instituto)\b", text, re.IGNORECASE)
    metadata["organization"] = org_match.group(1) if org_match else None

    return metadata
