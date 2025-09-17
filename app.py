import customtkinter as ctk


ctk.set_appearance_mode("light")

# Funções dos botões de ação


def view_action(doc_name):
    print(f"Ver detalhes de: {doc_name}")


def edit_action(doc_name):
    print(f"Editar documento: {doc_name}")


def delete_action(doc_name):
    print(f"Excluir documento: {doc_name}")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestão Documental")
        self.geometry("1200x700")

        # Exemplo de documentos
        documents = [
            {"nome": "Relatório Anual Educação 2023", "arquivo": "relatorio_educacao_2023.pdf",
             "data": "15/01/2024", "secretaria": "Educação", "cor": "#a5d8ff"},
            {"nome": "Contrato Obras Públicas", "arquivo": "contrato_obras_001.docx",
             "data": "12/01/2024", "secretaria": "Obras", "cor": "#ffd8a5"},
            {"nome": "Planilha Orçamentária 2024", "arquivo": "orcamento_2024.xlsx",
             "data": "10/01/2024", "secretaria": "Finanças", "cor": "#a5ffb0"},
            {"nome": "Protocolo Saúde Pública", "arquivo": "protocolo_saude_001.pdf",
             "data": "08/01/2024", "secretaria": "Saúde", "cor": "#d8a5ff"},
            {"nome": "Ata da Reunião Conselho Municipal", "arquivo": "ata_conselho_2024.pdf",
             "data": "05/01/2024", "secretaria": "Administração", "cor": "#ffc7c7"},
            {"nome": "Licitação Coleta de Lixo", "arquivo": "licitacao_lixo_001.docx",
             "data": "03/01/2024", "secretaria": "Obras", "cor": "#ffd8a5"},
            {"nome": "Relatório Financeiro Semestral", "arquivo": "relatorio_financeiro_s1.pdf",
             "data": "28/12/2023", "secretaria": "Finanças", "cor": "#a5ffb0"},
            {"nome": "Projeto de Lei - Educação Inclusiva", "arquivo": "pl_educacao_inclusiva.docx",
             "data": "22/12/2023", "secretaria": "Educação", "cor": "#a5d8ff"},
            {"nome": "Protocolo Vacinação COVID-19", "arquivo": "protocolo_vacinacao.pdf",
             "data": "18/12/2023", "secretaria": "Saúde", "cor": "#d8a5ff"},
            {"nome": "Contrato Prestação de Serviços TI", "arquivo": "contrato_ti_2023.docx",
             "data": "15/12/2023", "secretaria": "Administração", "cor": "#ffc7c7"},
            {"nome": "Plano Diretor Urbano", "arquivo": "plano_diretor_urbano.pdf",
             "data": "10/12/2023", "secretaria": "Obras", "cor": "#ffd8a5"},
            {"nome": "Relatório de Licitações 2023", "arquivo": "relatorio_licitacoes_2023.xlsx",
             "data": "05/12/2023", "secretaria": "Finanças", "cor": "#a5ffb0"},
            {"nome": "Protocolo Atendimento Social", "arquivo": "protocolo_social.pdf",
             "data": "02/12/2023", "secretaria": "Administração", "cor": "#ffc7c7"},
            {"nome": "Projeto de Lei Saúde Mental", "arquivo": "pl_saude_mental.docx",
             "data": "28/11/2023", "secretaria": "Saúde", "cor": "#d8a5ff"},
            {"nome": "Relatório de Obras Concluídas", "arquivo": "relatorio_obras_2023.pdf",
             "data": "25/11/2023", "secretaria": "Obras", "cor": "#ffd8a5"},
        ]

        # ---------------- Cabeçalho Superior ----------------
        header_frame = ctk.CTkFrame(
            self, height=50, corner_radius=3, fg_color="#f8f9fa")
        header_frame.pack(side="top", fill="x", padx=20, pady=10)

        ctk.CTkLabel(header_frame, text="🏢", font=(
            "Arial", 20)).pack(side="left", padx=(15, 10))
        ctk.CTkLabel(header_frame, text="Sistema de Gestão Documental",
                     font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(header_frame, text="⚙️").pack(side="right")
        ctk.CTkButton(header_frame, text="Admin municipal", fg_color="transparent",
                      hover=False, text_color="black").pack(side="right", padx=10)

        # ---------------- Linha com título à esquerda e botão à direita ----------------
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(fill="x", padx=20, pady=(15, 0))

        left_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        left_frame.pack(side="left", anchor="w")
        ctk.CTkLabel(left_frame, text="Documentos Municipais",
                     font=("Arial", 18)).pack(anchor="w")
        ctk.CTkLabel(left_frame, text="Gerencie e organize todos os documentos das secretarias", font=(
            "Arial", 12), text_color="#6c757d").pack(anchor="w")

        ctk.CTkButton(
            section_frame, text="+ Adicionar novo documento").pack(side="right", padx=20, pady=10)

        # ---------------- Campo de busca ----------------
        search_frame = ctk.CTkFrame(self, corner_radius=5, fg_color="#f8f9fa")
        search_frame.pack(fill="x", padx=20, pady=15)

        search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar documentos por nome, secretaria ou data...", height=40, width=1100, corner_radius=8)
        search_entry.pack(fill="x", padx=15, pady=10)

        # ---------------- Frame principal (filtros + documentos) ----------------
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # ---------------- Filtros à esquerda ----------------
        filter_frame = ctk.CTkFrame(
            content_frame, width=300, fg_color="#f8f9fa", corner_radius=5)
        filter_frame.pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(filter_frame, text="Filtros", font=(
            "Arial", 14)).pack(anchor="w", padx=15, pady=(10, 5))

        ctk.CTkLabel(filter_frame, text="Secretarias", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for sec in ["Educação", "Saúde", "Finanças", "Obras", "Administração"]:
            ctk.CTkCheckBox(filter_frame, text=sec, font=(
                "Arial", 11), border_width=2).pack(anchor="w", padx=25, pady=2)

        ctk.CTkLabel(filter_frame, text="Tipo de Documento", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for tipo in ["Relatórios", "Contratos", "Licitações"]:
            ctk.CTkCheckBox(filter_frame, text=tipo, font=(
                "Arial", 11), border_width=2).pack(anchor="w", padx=25, pady=2)

        ctk.CTkLabel(filter_frame, text="Período", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkEntry(
            filter_frame, placeholder_text="Data inicial (dd/mm/aaaa)").pack(fill="x", padx=15, pady=5)
        ctk.CTkEntry(
            filter_frame, placeholder_text="Data final (dd/mm/aaaa)").pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(filter_frame, text="Limpar filtros", fg_color="#e9ecef",
                      text_color="black").pack(fill="x", padx=15, pady=10)

        # ---------------- Lista de documentos ----------------
        documents_frame = ctk.CTkFrame(
            content_frame, fg_color="#f8f9fa", corner_radius=5)
        documents_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(documents_frame, text="Lista de Documentos",
                     font=("Arial", 14)).pack(anchor="w", padx=15, pady=10)

        documents_list_frame = ctk.CTkScrollableFrame(
            documents_frame, fg_color="transparent")
        documents_list_frame.pack(
            fill="both", expand=True, padx=15, pady=(0, 10))

        for doc in documents:
            row_frame = ctk.CTkFrame(
                documents_list_frame, fg_color="#ffffff", corner_radius=5)
            row_frame.pack(fill="x", pady=5)

            file_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            file_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
            ctk.CTkLabel(file_frame, text="📄").pack(side="left", padx=(0, 5))
            ctk.CTkLabel(file_frame, text=doc["nome"], font=(
                "Arial", 11, "bold")).pack(anchor="w")
            ctk.CTkLabel(file_frame, text=doc["arquivo"], font=(
                "Arial", 10), text_color="#6c757d").pack(anchor="w")

            ctk.CTkLabel(row_frame, text=doc["data"], width=120, anchor="w").pack(
                side="left", padx=5)

            ctk.CTkLabel(row_frame, text=doc["secretaria"], width=120, anchor="center", fg_color=doc["cor"],
                         corner_radius=10, text_color="white").pack(side="left", padx=5, pady=5)

            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", padx=5)
            ctk.CTkButton(actions_frame, text="👁️", width=25, height=25,
                          command=lambda d=doc["nome"]: view_action(d)).pack(side="left", padx=2)
            ctk.CTkButton(actions_frame, text="✏️", width=25, height=25,
                          command=lambda d=doc["nome"]: edit_action(d)).pack(side="left", padx=2)
            ctk.CTkButton(actions_frame, text="🗑️", width=25, height=25,
                          command=lambda d=doc["nome"]: delete_action(d)).pack(side="left", padx=2)


# Este bloco permite que você execute app.py de forma independente para testes
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
