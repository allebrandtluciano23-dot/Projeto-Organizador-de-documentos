import os
import unicodedata

def contem_palavra(texto: str, palavra: str) -> bool:
    def limpar(txt: str) -> str:
        nfkd = unicodedata.normalize('NFKD', txt)
        sem_acentos = ''.join(c for c in nfkd if not unicodedata.combining(c))
        return ' '.join(sem_acentos.lower().split())
    return limpar(palavra) in limpar(texto)

def Matching(firstpagetext: str):
    base_folder = os.path.join(os.getcwd(), "Tabelas")
    for root, dirs, files in os.walk(base_folder):
        for dir in dirs:
            current_folder = os.path.join(base_folder, dir)
            try:
                with open(os.path.join(current_folder, "keywords.txt"), 'r', encoding="UTF-8") as file:
                    palavras = [linha.strip() for linha in file]
            except FileNotFoundError:
                continue
            for palavra in palavras:
                if contem_palavra(firstpagetext, palavra):
                    return current_folder, palavra
    return "SemPasta", "SemTítulo"
