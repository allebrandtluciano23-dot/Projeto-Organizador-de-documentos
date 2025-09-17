import sqlite3

def create_db(db_path: str):
    """Cria o banco de dados e a tabela documents, se ainda não existir."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            organization TEXT,
            folder TEXT,
            file_path TEXT,
            text TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(metadata: dict, pdf_path: str, db_path: str, full_text: str = None):
    """Salva um documento no banco de dados."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (title, date, organization, folder, file_path, text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        metadata.get("title"),
        metadata.get("date"),
        metadata.get("organization"),
        metadata.get("folder"),
        pdf_path,
        full_text
    ))
    conn.commit()
    conn.close()
