import customtkinter as ctk
from tkinter import filedialog, messagebox
import uuid
import os
import shutil
from datetime import datetime
import platform
import subprocess

ctk.set_appearance_mode("light")

# Mapeamento de secretarias para cores, para manter a consistência
SECRETARIA_CORES = {
    "Educação": "#a5d8ff",
    "Obras": "#ffd8a5",
    "Finanças": "#a5ffb0",
    "Saúde": "#d8a5ff",
    "Administração": "#ffc7c7"
}


class AddDocumentDialog(ctk.CTkToplevel):
    """
    Janela de diálogo aprimorada para adicionar um novo documento ou editar um existente.
    """

    def __init__(self, parent, existing_data=None):
        super().__init__(parent)

        self.transient(parent)
        self.grab_set()
        self.result = None

        # Configura a janela para Adicionar ou Editar
        if existing_data and 'secretaria' in existing_data:  # Modo Edição
            self.title("Editar Documento")
            default_name = existing_data.get('nome', '')
            default_secretaria = existing_data.get('secretaria')
        else:  # Modo Adição
            self.title("Adicionar Novo Documento")
            default_name = existing_data.get(
                'nome', '') if existing_data else ''
            default_secretaria = list(SECRETARIA_CORES.keys())[0]

        self.geometry("400x250")
        self.resizable(False, False)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Nome do Documento:",
                     font=("Arial", 12)).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(main_frame, width=350, height=35)
        self.name_entry.insert(0, default_name)
        self.name_entry.pack(pady=(5, 15))

        ctk.CTkLabel(main_frame, text="Secretaria:",
                     font=("Arial", 12)).pack(anchor="w")
        self.secretaria_menu = ctk.CTkOptionMenu(
            main_frame, values=list(SECRETARIA_CORES.keys()), height=35)
        self.secretaria_menu.set(default_secretaria)
        self.secretaria_menu.pack(pady=5, fill="x")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20, fill="x")

        ctk.CTkButton(button_frame, text="Salvar", command=self.save).pack(
            side="right", padx=(10, 0))
        ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel,
                      fg_color="#e9ecef", text_color="black").pack(side="right")

    def save(self):
        doc_name = self.name_entry.get().strip()
        if not doc_name:
            messagebox.showerror(
                "Erro", "O nome do documento não pode estar vazio.", parent=self)
            return
        self.result = {"nome": doc_name,
                       "secretaria": self.secretaria_menu.get()}
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestão Documental")
        self.geometry("1200x700")

        self.documents = []
        self.filter_widgets = {"secretarias": {}, "tipos": {}}

        self.setup_ui()
        self.apply_filters()

    def setup_ui(self):
        # ... (Toda a configuração da UI permanece a mesma do passo anterior) ...
        # --- Estrutura de Frames ---
        header_frame = ctk.CTkFrame(
            self, height=50, corner_radius=3, fg_color="#f8f9fa")
        header_frame.pack(side="top", fill="x", padx=20, pady=10)
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(fill="x", padx=20, pady=(15, 0))
        search_frame = ctk.CTkFrame(self, corner_radius=5, fg_color="#f8f9fa")
        search_frame.pack(fill="x", padx=20, pady=15)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        filter_frame = ctk.CTkFrame(
            content_frame, width=300, fg_color="#f8f9fa", corner_radius=5)
        filter_frame.pack(side="left", fill="y", padx=(0, 10))
        documents_outer_frame = ctk.CTkFrame(
            content_frame, fg_color="#f8f9fa", corner_radius=5)
        documents_outer_frame.pack(side="left", fill="both", expand=True)

        # Cabeçalho
        ctk.CTkLabel(header_frame, text="🏢", font=(
            "Arial", 20)).pack(side="left", padx=(15, 10))
        ctk.CTkLabel(header_frame, text="Sistema de Gestão Documental",
                     font=("Arial", 16)).pack(side="left")
        # Seção de Título e Botão Adicionar
        left_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        left_frame.pack(side="left", anchor="w")
        ctk.CTkLabel(left_frame, text="Documentos Municipais",
                     font=("Arial", 18)).pack(anchor="w")
        ctk.CTkLabel(left_frame, text="Gerencie e organize todos os documentos...", font=(
            "Arial", 12), text_color="#6c757d").pack(anchor="w")
        ctk.CTkButton(section_frame, text="+ Adicionar novo documento",
                      command=self.upload_document).pack(side="right", padx=20, pady=10)
        # Busca
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar documentos por nome, secretaria ou data...", height=40, corner_radius=8)
        self.search_entry.pack(fill="x", padx=15, pady=10)
        self.search_entry.bind(
            "<KeyRelease>", lambda event: self.apply_filters())
        # Painel de Filtros
        ctk.CTkLabel(filter_frame, text="Filtros", font=(
            "Arial", 14)).pack(anchor="w", padx=15, pady=(10, 5))
        # Secretarias
        ctk.CTkLabel(filter_frame, text="Secretarias", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for sec in SECRETARIA_CORES.keys():
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(filter_frame, text=sec, font=(
                "Arial", 11), variable=var, onvalue=sec, offvalue="off", command=self.apply_filters)
            cb.pack(anchor="w", padx=25, pady=2)
            self.filter_widgets["secretarias"][sec] = var
        # Tipo de Documento
        ctk.CTkLabel(filter_frame, text="Tipo de Documento", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for tipo in ["Relatório", "Contrato", "Licitação", "Planilha", "Protocolo", "Projeto"]:
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(filter_frame, text=tipo, font=(
                "Arial", 11), variable=var, onvalue=tipo, offvalue="off", command=self.apply_filters)
            cb.pack(anchor="w", padx=25, pady=2)
            self.filter_widgets["tipos"][tipo] = var
        # Período
        ctk.CTkLabel(filter_frame, text="Período", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        self.date_start_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="Data inicial (dd/mm/aaaa)")
        self.date_start_entry.pack(fill="x", padx=15, pady=5)
        self.date_end_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="Data final (dd/mm/aaaa)")
        self.date_end_entry.pack(fill="x", padx=15, pady=5)
        self.date_start_entry.bind(
            "<KeyRelease>", lambda event: self.apply_filters())
        self.date_end_entry.bind(
            "<KeyRelease>", lambda event: self.apply_filters())
        # Botão Limpar
        ctk.CTkButton(filter_frame, text="Limpar filtros", fg_color="#e9ecef",
                      text_color="black", command=self.clear_filters).pack(fill="x", padx=15, pady=10)
        # Lista de Documentos
        ctk.CTkLabel(documents_outer_frame, text="Lista de Documentos", font=(
            "Arial", 14)).pack(anchor="w", padx=15, pady=10)
        self.documents_list_frame = ctk.CTkScrollableFrame(
            documents_outer_frame, fg_color="transparent")
        self.documents_list_frame.pack(
            fill="both", expand=True, padx=15, pady=(0, 10))

    # --- Lógica dos Botões de Ação ---

    def view_action(self, doc_path):
        if not os.path.exists(doc_path):
            messagebox.showerror(
                "Erro", "Arquivo não encontrado. Pode ter sido movido ou excluído.")
            return

        try:
            current_os = platform.system()
            if current_os == "Windows":
                os.startfile(doc_path)
            elif current_os == "Darwin":  # macOS
                subprocess.run(["open", doc_path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", doc_path], check=True)
        except Exception as e:
            messagebox.showerror(
                "Erro ao Abrir", f"Não foi possível abrir o arquivo.\n{e}")

    def edit_action(self, doc_to_edit):
        dialog = AddDocumentDialog(self, existing_data=doc_to_edit)
        self.wait_window(dialog)

        if dialog.result:
            # Encontra o documento original na lista pelo ID e o atualiza
            for i, doc in enumerate(self.documents):
                if doc['id'] == doc_to_edit['id']:
                    self.documents[i]['nome'] = dialog.result['nome']
                    self.documents[i]['secretaria'] = dialog.result['secretaria']
                    self.documents[i]['cor'] = SECRETARIA_CORES.get(
                        dialog.result['secretaria'])
                    break
            self.apply_filters()

    def delete_action(self, doc_to_delete):
        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Você tem certeza que deseja apagar o documento:\n\n'{doc_to_delete['nome']}'?\n\nEsta ação não pode ser desfeita.",
            icon='warning'
        )

        if confirm:
            # Remove o arquivo do disco
            try:
                if os.path.exists(doc_to_delete['path']):
                    os.remove(doc_to_delete['path'])
            except OSError as e:
                messagebox.showerror(
                    "Erro de Exclusão", f"Não foi possível apagar o arquivo.\n{e}")
                return

            # Remove o registro da lista de documentos
            self.documents.remove(doc_to_delete)
            self.apply_filters()  # Atualiza a UI

    # --- Lógica de Exibição e Filtros ---

    def display_documents(self, documents_to_display):
        for widget in self.documents_list_frame.winfo_children():
            widget.destroy()

        for doc in documents_to_display:
            row_frame = ctk.CTkFrame(
                self.documents_list_frame, fg_color="#ffffff", corner_radius=5)
            row_frame.pack(fill="x", pady=5)

            file_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            file_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
            ctk.CTkLabel(file_frame, text="📄", font=(
                "Arial", 14)).pack(side="left", padx=(0, 5))

            text_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(text_frame, text=doc["nome"], font=(
                "Arial", 11, "bold")).pack(anchor="w")
            ctk.CTkLabel(text_frame, text=doc["arquivo"], font=(
                "Arial", 10), text_color="#6c757d").pack(anchor="w")

            ctk.CTkLabel(row_frame, text=doc["data"], width=100, anchor="w").pack(
                side="left", padx=5)
            ctk.CTkLabel(row_frame, text=doc["secretaria"], width=110, anchor="center", fg_color=doc["cor"],
                         corner_radius=10, text_color="#343a40").pack(side="left", padx=5, pady=5)

            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", padx=5)
            # Comandos atualizados para chamar as novas funções
            ctk.CTkButton(actions_frame, text="👁️", width=25, height=25,
                          command=lambda p=doc['path']: self.view_action(p)).pack(side="left", padx=2)
            ctk.CTkButton(actions_frame, text="✏️", width=25, height=25,
                          command=lambda d=doc: self.edit_action(d)).pack(side="left", padx=2)
            ctk.CTkButton(actions_frame, text="🗑️", width=25, height=25,
                          command=lambda d=doc: self.delete_action(d)).pack(side="left", padx=2)

    def apply_filters(self):
        # ... (Função de filtro permanece a mesma) ...
        filtered_list = self.documents[:]
        search_term = self.search_entry.get().lower()
        if search_term:
            filtered_list = [doc for doc in filtered_list if search_term in doc["nome"].lower(
            ) or search_term in doc["secretaria"].lower() or search_term in doc["data"]]
        selected_secretarias = [var.get(
        ) for var in self.filter_widgets["secretarias"].values() if var.get() != "off"]
        if selected_secretarias:
            filtered_list = [
                doc for doc in filtered_list if doc["secretaria"] in selected_secretarias]
        selected_tipos = [
            var.get() for var in self.filter_widgets["tipos"].values() if var.get() != "off"]
        if selected_tipos:
            filtered_list = [doc for doc in filtered_list if any(
                tipo.lower() in doc["nome"].lower() for tipo in selected_tipos)]
        try:
            start_date_str = self.date_start_entry.get()
            end_date_str = self.date_end_entry.get()
            start_date = datetime.strptime(
                start_date_str, "%d/%m/%Y") if start_date_str else None
            end_date = datetime.strptime(
                end_date_str, "%d/%m/%Y") if end_date_str else None
            if start_date:
                filtered_list = [doc for doc in filtered_list if datetime.strptime(
                    doc["data"], "%d/%m/%Y") >= start_date]
            if end_date:
                filtered_list = [doc for doc in filtered_list if datetime.strptime(
                    doc["data"], "%d/%m/%Y") <= end_date]
        except ValueError:
            pass
        self.display_documents(filtered_list)

    def clear_filters(self):
        # ... (Função de limpar filtros permanece a mesma) ...
        self.search_entry.delete(0, "end")
        self.date_start_entry.delete(0, "end")
        self.date_end_entry.delete(0, "end")
        for group in self.filter_widgets.values():
            for var in group.values():
                var.set("off")
        self.apply_filters()

    def upload_document(self):
        # ... (Função de upload permanece a mesma, mas chama o diálogo de forma diferente) ...
        upload_dir = "documentos_municipais"
        os.makedirs(upload_dir, exist_ok=True)
        filepaths = filedialog.askopenfilenames(
            title="Selecione os documentos", filetypes=[("Documentos", "*.pdf *.png")])
        if not filepaths:
            return
        for filepath in filepaths:
            filename = os.path.basename(filepath)
            default_doc_name = os.path.splitext(
                filename)[0].replace("_", " ").title()

            dialog = AddDocumentDialog(
                self, existing_data={'nome': default_doc_name})
            self.wait_window(dialog)

            if dialog.result:
                doc_details = dialog.result
                unique_id = str(uuid.uuid4())
                file_extension = os.path.splitext(filename)[1]
                new_filename = f"{unique_id}{file_extension}"
                destination_path = os.path.join(upload_dir, new_filename)
                shutil.copy(filepath, destination_path)
                new_doc = {"id": unique_id, "nome": doc_details["nome"], "arquivo": filename, "path": destination_path, "data": datetime.now(
                ).strftime("%d/%m/%Y"), "secretaria": doc_details["secretaria"], "cor": SECRETARIA_CORES.get(doc_details["secretaria"], "#808080")}
                self.documents.append(new_doc)
        self.apply_filters()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
