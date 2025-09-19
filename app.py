import customtkinter as ctk
from tkinter import filedialog, messagebox
import uuid
import os
import shutil
from datetime import datetime
import platform
import subprocess
import json
import re
from collections import Counter

# Módulos para análise de documentos e IA
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# --- Configuração ---
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Aviso: A variável de ambiente GEMINI_API_KEY não foi configurada. Funcionalidades de IA desativadas.")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"Erro ao configurar a API Gemini: {e}")

ctk.set_appearance_mode("light")

# --- Constantes de Cores ---
SECRETARIA_CORES = {
    "Educação": "#a5d8ff", "Obras": "#ffd8a5", "Finanças": "#a5ffb0",
    "Saúde": "#d8a5ff", "Administração": "#ffc7c7", "Outro": "#d3d3d3"
}
TIPO_CORES = {
    "Relatório": "#f7aef8", "Contrato": "#b388eb", "Licitação": "#88d8b0",
    "Planilha": "#ffcb77", "Protocolo": "#82c0cc", "Projeto": "#fde4cf", "Outro": "#d3d3d3"
}

# --- Funções Auxiliares ---


def format_bytes(size_bytes):
    if size_bytes == 0:
        return "0 B"
    power = 1024
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size_bytes >= power and n < len(power_labels) - 1:
        size_bytes /= power
        n += 1
    return f"{size_bytes:.2f} {power_labels[n]}"


def extract_text_from_file(filepath):
    text = ""
    try:
        if filepath.lower().endswith('.pdf'):
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text()
        elif filepath.lower().endswith('.png'):
            text = pytesseract.image_to_string(Image.open(filepath))
        return text.strip()
    except Exception as e:
        print(f"Erro ao extrair texto do arquivo {filepath}: {e}")
        return ""


def get_details_from_gemini(text_content):
    default_response = {"categoria": "Outro",
                        "secretaria": "Outro", "data": ""}
    raw_response_text = "API não chamada ou não configurada."
    if not text_content or not api_key:
        return raw_response_text, default_response

    text_content = text_content[:15000]
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Você é um assistente especialista em análise e classificação de documentos para um órgão municipal. Sua tarefa é analisar o texto de um documento e retornar as informações em um formato JSON específico.

    Siga estes passos para sua análise:
    1.  Leia todo o texto fornecido.
    2.  Raciocine sobre o propósito principal do documento. É um relatório financeiro? Um contrato de serviço? Um protocolo de atendimento?
    3.  Com base no seu raciocínio, extraia as seguintes informações: "categoria", "secretaria" e "data".
    4.  Formate sua resposta final APENAS como um objeto JSON. Não inclua texto explicativo antes ou depois do JSON.

    Opções Válidas:
    - "categoria": {', '.join(TIPO_CORES.keys())}
    - "secretaria": {', '.join(SECRETARIA_CORES.keys())}

    Exemplos:
    - Exemplo de Texto 1: "Relatório de Despesas Anual... Secretaria de Finanças... Emitido em 15 de janeiro de 2024..."
      JSON de Saída Esperado 1: {{"categoria": "Relatório", "secretaria": "Finanças", "data": "15/01/2024"}}
    - Exemplo de Texto 2: "Contrato de Prestação de Serviços de Limpeza... CONTRATADA: LimpaTudo Ltda... CONTRATANTE: Secretaria de Administração... Válido a partir de 01/02/2025."
      JSON de Saída Esperado 2: {{"categoria": "Contrato", "secretaria": "Administração", "data": "01/02/2025"}}

    Agora, analise o seguinte texto:
    ---
    {text_content}
    ---
    """
    try:
        response = model.generate_content(prompt)
        raw_response_text = response.text
        json_match = re.search(r'\{.*\}', raw_response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            details = json.loads(json_str)
            details['categoria'] = details.get('categoria', 'Outro')
            details['secretaria'] = details.get('secretaria', 'Outro')
            details['data'] = details.get('data', '')
            return raw_response_text, details
        else:
            return raw_response_text, default_response
    except Exception as e:
        print(f"Erro ao processar resposta da API Gemini: {e}")
        return str(e), default_response

# --- Classes da Interface Gráfica ---


class AddDocumentDialog(ctk.CTkToplevel):

    def __init__(self, parent, existing_data=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.result = None
        is_editing = existing_data and 'id' in existing_data
        self.title(
            "Editar Documento" if is_editing else "Adicionar Novo Documento")
        default_name = existing_data.get('nome', '') if existing_data else ''
        default_secretaria = existing_data.get('secretaria', list(SECRETARIA_CORES.keys())[
                                               0]) if existing_data else list(SECRETARIA_CORES.keys())[0]
        default_data = existing_data.get('data', datetime.today().strftime(
            "%d/%m/%Y")) if existing_data else datetime.today().strftime("%d/%m/%Y")
        default_responsavel = existing_data.get(
            'responsavel', '') if existing_data else ''
        default_privacidade = existing_data.get(
            'privacidade', 'Privado') if existing_data else 'Privado'
        self.geometry("520x650")
        self.resizable(False, False)
        self.configure(fg_color="#f8f9fa")
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=self.title(), font=(
            "Arial", 18, "bold")).pack(pady=(10, 20))
        entry_config = {"width": 450, "height": 40,
                        "font": ("Arial", 12), "corner_radius": 8}
        ctk.CTkLabel(main_frame, text="Nome do Documento:",
                     font=("Arial", 14)).pack(anchor="w", padx=20)
        self.name_entry = ctk.CTkEntry(main_frame, **entry_config)
        self.name_entry.insert(0, default_name)
        self.name_entry.pack(pady=(5, 15), padx=20)
        ctk.CTkLabel(main_frame, text="Secretaria:", font=(
            "Arial", 14)).pack(anchor="w", padx=20)
        self.secretaria_menu = ctk.CTkOptionMenu(main_frame, values=list(
            SECRETARIA_CORES.keys()), height=40, font=("Arial", 12))
        self.secretaria_menu.set(default_secretaria)
        self.secretaria_menu.pack(pady=(5, 15), padx=20, fill="x")
        ctk.CTkLabel(main_frame, text="Data do Documento:",
                     font=("Arial", 14)).pack(anchor="w", padx=20)
        self.date_entry = ctk.CTkEntry(main_frame, **entry_config)
        self.date_entry.insert(0, default_data)
        self.date_entry.pack(pady=(5, 15), padx=20)
        ctk.CTkLabel(main_frame, text="Responsável:", font=(
            "Arial", 14)).pack(anchor="w", padx=20)
        self.responsavel_entry = ctk.CTkEntry(main_frame, **entry_config)
        self.responsavel_entry.insert(0, default_responsavel)
        self.responsavel_entry.pack(pady=(5, 15), padx=20)
        ctk.CTkLabel(main_frame, text="Privacidade:", font=(
            "Arial", 14)).pack(anchor="w", padx=20)
        self.privacidade_menu = ctk.CTkOptionMenu(
            main_frame, values=["Privado", "Público"], height=40, font=("Arial", 12))
        self.privacidade_menu.set(default_privacidade)
        self.privacidade_menu.pack(pady=(5, 15), padx=20, fill="x")
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20, fill="x", padx=20)
        ctk.CTkButton(button_frame, text="Cancelar", command=self.cancel, fg_color="#e9ecef",
                      text_color="black", height=45, corner_radius=10).pack(side="left")
        ctk.CTkButton(button_frame, text="💾 Salvar Documento", command=self.save, height=45,
                      fg_color="#0d6efd", font=("Arial", 12, "bold"), corner_radius=10).pack(side="right")

    def save(self):
        doc_name = self.name_entry.get().strip()
        if not doc_name:
            messagebox.showerror(
                "Erro de Validação", "O nome do documento não pode estar vazio.", parent=self)
            return
        data_doc = self.date_entry.get().strip()
        try:
            datetime.strptime(data_doc, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror(
                "Erro de Validação", "Formato de data inválido. Use dd/mm/aaaa.", parent=self)
            return
        self.result = {"nome": doc_name, "secretaria": self.secretaria_menu.get(
        ), "data": data_doc, "responsavel": self.responsavel_entry.get().strip(), "privacidade": self.privacidade_menu.get()}
        self.destroy()

    def cancel(self): self.result = None; self.destroy()


class MainApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão Documental Inteligente")
        self.geometry("1200x750")
        self.documents = []
        self.filter_widgets = {"secretarias": {},
                               "tipos": {}, "privacidade": {}}
        self.setup_ui()
        self.update_dashboard_stats()

    def setup_ui(self):
        self.tab_view = ctk.CTkTabview(self, anchor="w")
        self.tab_view.pack(expand=True, fill="both", padx=20, pady=10)
        self.dashboard_tab = self.tab_view.add("📊 Dashboard")
        self.documents_tab = self.tab_view.add("📁 Documentos")
        self.setup_dashboard_tab()
        self.setup_documents_tab()

    def setup_dashboard_tab(self):
        self.dashboard_tab.grid_columnconfigure((0, 1), weight=1)
        self.dashboard_tab.grid_rowconfigure(1, weight=1)
        stats_cards_frame = ctk.CTkFrame(
            self.dashboard_tab, fg_color="transparent")
        stats_cards_frame.grid(row=0, column=0, columnspan=2,
                               sticky="ew", padx=10, pady=10)
        stats_cards_frame.grid_columnconfigure((0, 1), weight=1)
        card1 = ctk.CTkFrame(stats_cards_frame, corner_radius=10)
        card1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(card1, text="Documentos Totais", font=(
            "Arial", 14, "bold"), text_color="#888").pack(pady=(15, 5))
        self.total_files_label = ctk.CTkLabel(
            card1, text="0", font=("Arial", 48, "bold"))
        self.total_files_label.pack(pady=5, padx=20)
        ctk.CTkLabel(card1, text="arquivos no sistema", font=(
            "Arial", 12), text_color="#aaa").pack(pady=(5, 15))
        card2 = ctk.CTkFrame(stats_cards_frame, corner_radius=10)
        card2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(card2, text="Espaço Utilizado", font=(
            "Arial", 14, "bold"), text_color="#888").pack(pady=(15, 5))
        self.total_space_label = ctk.CTkLabel(
            card2, text="0 B", font=("Arial", 48, "bold"))
        self.total_space_label.pack(pady=5, padx=20)
        ctk.CTkLabel(card2, text="em disco", font=("Arial", 12),
                     text_color="#aaa").pack(pady=(5, 15))
        summaries_frame = ctk.CTkFrame(
            self.dashboard_tab, fg_color="transparent")
        summaries_frame.grid(row=1, column=0, columnspan=2,
                             sticky="nsew", padx=10, pady=10)
        summaries_frame.grid_columnconfigure((0, 1), weight=1)
        summaries_frame.grid_rowconfigure(0, weight=1)
        secretaria_summary_frame = ctk.CTkFrame(
            summaries_frame, corner_radius=10)
        secretaria_summary_frame.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(secretaria_summary_frame, text="Documentos por Secretaria", font=(
            "Arial", 16, "bold")).pack(pady=10, padx=15, anchor="w")
        self.secretaria_summary_container = ctk.CTkFrame(
            secretaria_summary_frame, fg_color="transparent")
        self.secretaria_summary_container.pack(
            fill="both", expand=True, padx=15, pady=5)
        tipo_summary_frame = ctk.CTkFrame(summaries_frame, corner_radius=10)
        tipo_summary_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(tipo_summary_frame, text="Documentos por Tipo", font=(
            "Arial", 16, "bold")).pack(pady=10, padx=15, anchor="w")
        self.tipo_summary_container = ctk.CTkFrame(
            tipo_summary_frame, fg_color="transparent")
        self.tipo_summary_container.pack(
            fill="both", expand=True, padx=15, pady=5)

    def setup_documents_tab(self):
        header_frame = ctk.CTkFrame(
            self.documents_tab, height=50, corner_radius=3, fg_color="transparent")
        header_frame.pack(side="top", fill="x", padx=0, pady=(0, 10))
        ctk.CTkLabel(header_frame, text="Sistema de Gestão Documental",
                     font=("Arial", 16, "bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="+ Adicionar Novo Documento",
                      command=self.upload_document).pack(side="right")

        search_frame = ctk.CTkFrame(
            self.documents_tab, corner_radius=5, fg_color="transparent")
        search_frame.pack(fill="x", padx=0, pady=5)
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar por nome, tipo, secretaria, data ou responsável...", height=40, corner_radius=8)
        self.search_entry.pack(fill="x", padx=0, pady=0)
        self.search_entry.bind(
            "<KeyRelease>", lambda event: self.apply_filters())

        content_frame = ctk.CTkFrame(
            self.documents_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=10)
        filter_frame = ctk.CTkScrollableFrame(
            content_frame, width=280, fg_color="#f0f0f0", corner_radius=5)
        filter_frame.pack(side="left", fill="y", padx=(0, 10))
        documents_outer_frame = ctk.CTkFrame(
            content_frame, fg_color="transparent", corner_radius=5)
        documents_outer_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(filter_frame, text="Filtros", font=(
            "Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(filter_frame, text="Secretarias", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for sec in SECRETARIA_CORES.keys():
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(filter_frame, text=sec, font=(
                "Arial", 11), variable=var, onvalue=sec, offvalue="off", command=self.apply_filters)
            cb.pack(anchor="w", padx=25, pady=2)
            self.filter_widgets["secretarias"][sec] = var
        ctk.CTkLabel(filter_frame, text="Tipo de Documento", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for tipo in TIPO_CORES.keys():
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(filter_frame, text=tipo, font=(
                "Arial", 11), variable=var, onvalue=tipo, offvalue="off", command=self.apply_filters)
            cb.pack(anchor="w", padx=25, pady=2)
            self.filter_widgets["tipos"][tipo] = var
        ctk.CTkLabel(filter_frame, text="Privacidade", font=(
            "Arial", 12)).pack(anchor="w", padx=15, pady=(10, 0))
        for privacidade_tipo in ["Público", "Privado"]:
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(filter_frame, text=privacidade_tipo, font=(
                "Arial", 11), variable=var, onvalue=privacidade_tipo, offvalue="off", command=self.apply_filters)
            cb.pack(anchor="w", padx=25, pady=2)
            self.filter_widgets["privacidade"][privacidade_tipo] = var
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
        ctk.CTkButton(filter_frame, text="Limpar filtros", fg_color="#e9ecef",
                      text_color="black", command=self.clear_filters).pack(fill="x", padx=15, pady=10)

        self.documents_list_frame = ctk.CTkScrollableFrame(
            documents_outer_frame, fg_color="transparent")
        self.documents_list_frame.pack(
            fill="both", expand=True, padx=0, pady=0)

    def update_dashboard_stats(self):
        total_files = len(self.documents)
        self.total_files_label.configure(text=str(total_files))
        total_bytes = sum(os.path.getsize(
            doc['path']) for doc in self.documents if os.path.exists(doc['path']))
        self.total_space_label.configure(text=format_bytes(total_bytes))
        for widget in self.secretaria_summary_container.winfo_children():
            widget.destroy()
        if self.documents:
            secretaria_counts = Counter(doc['secretaria']
                                        for doc in self.documents)
            for secretaria, count in secretaria_counts.most_common():
                line = ctk.CTkFrame(
                    self.secretaria_summary_container, fg_color="transparent")
                line.pack(fill="x", pady=2)
                ctk.CTkLabel(line, text=f" {secretaria}", fg_color=SECRETARIA_CORES.get(
                    secretaria, "#ccc"), corner_radius=5, anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(line, text=str(count), font=(
                    "Arial", 12, "bold")).pack(side="right")
        for widget in self.tipo_summary_container.winfo_children():
            widget.destroy()
        if self.documents:
            tipo_counts = Counter(doc.get('tipo', 'Outro')
                                  for doc in self.documents)
            for tipo, count in tipo_counts.most_common():
                line = ctk.CTkFrame(
                    self.tipo_summary_container, fg_color="transparent")
                line.pack(fill="x", pady=2)
                ctk.CTkLabel(line, text=f" {tipo}", fg_color=TIPO_CORES.get(
                    tipo, "#ccc"), corner_radius=5, anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(line, text=str(count), font=(
                    "Arial", 12, "bold")).pack(side="right")

    def upload_document(self):
        upload_dir = "documentos_municipais"
        os.makedirs(upload_dir, exist_ok=True)
        filepaths = filedialog.askopenfilenames(
            title="Selecione os documentos", filetypes=[("Documentos", "*.pdf *.png")])
        if not filepaths:
            return
        for filepath in filepaths:
            filename = os.path.basename(filepath)
            file_text = extract_text_from_file(filepath)
            _, ai_details = get_details_from_gemini(file_text)
            base_name = os.path.splitext(filename)[0].replace("_", " ").title()
            dialog_data = {
                'nome': f"{ai_details['categoria']} - {base_name}" if ai_details['categoria'] != "Outro" else base_name,
                'secretaria': ai_details['secretaria'],
                'data': ai_details['data'] if ai_details['data'] else datetime.today().strftime("%d/%m/%Y")
            }
            dialog = AddDocumentDialog(self, existing_data=dialog_data)
            self.wait_window(dialog)
            if dialog.result:
                doc_details = dialog.result
                unique_id = str(uuid.uuid4())
                file_extension = os.path.splitext(filename)[1]
                new_filename = f"{unique_id}{file_extension}"
                destination_path = os.path.join(upload_dir, new_filename)
                shutil.copy(filepath, destination_path)
                new_doc = {
                    "id": unique_id, "nome": doc_details["nome"], "tipo": ai_details["categoria"], "arquivo": filename,
                    "path": destination_path, "data": doc_details["data"], "responsavel": doc_details["responsavel"],
                    "privacidade": doc_details["privacidade"], "secretaria": doc_details["secretaria"],
                    "cor": SECRETARIA_CORES.get(doc_details["secretaria"], "#d3d3d3")
                }
                self.documents.append(new_doc)
        self.apply_filters()
        self.update_dashboard_stats()

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
            ctk.CTkLabel(row_frame, text=doc["data"], width=80, anchor="w").pack(
                side="left", padx=5)
            ctk.CTkLabel(row_frame, text=doc.get("responsavel", ""),
                         width=100, anchor="w").pack(side="left", padx=5)
            doc_tipo = doc.get("tipo", "Outro")
            tipo_cor = TIPO_CORES.get(doc_tipo, TIPO_CORES["Outro"])
            ctk.CTkLabel(row_frame, text=doc_tipo, width=90, anchor="center", fg_color=tipo_cor,
                         corner_radius=10, text_color="#212529").pack(side="left", padx=5, pady=5)
            ctk.CTkLabel(row_frame, text=doc["secretaria"], width=100, anchor="center", fg_color=doc["cor"],
                         corner_radius=10, text_color="#212529").pack(side="left", padx=5, pady=5)
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", padx=5)
            ctk.CTkButton(actions_frame, text="👁️", width=25, height=25,
                          command=lambda p=doc['path']: self.view_action(p)).pack(side="left", padx=2)
            ctk.CTkButton(actions_frame, text="✏️", width=25, height=25,
                          command=lambda d=doc: self.edit_action(d)).pack(side="left", padx=2)
            ctk.CTkButton(actions_frame, text="🗑️", width=25, height=25,
                          command=lambda d=doc: self.delete_action(d)).pack(side="left", padx=2)

    def apply_filters(self):
        filtered_list = self.documents[:]
        search_term = self.search_entry.get().lower()
        if search_term:
            filtered_list = [doc for doc in filtered_list if search_term in doc["nome"].lower() or search_term in doc["secretaria"].lower(
            ) or search_term in doc.get("tipo", "").lower() or search_term in doc["data"].lower() or search_term in doc.get("responsavel", "").lower()]
        selected_secretarias = {var.get(
        ) for var in self.filter_widgets["secretarias"].values() if var.get() != "off"}
        if selected_secretarias:
            filtered_list = [
                doc for doc in filtered_list if doc["secretaria"] in selected_secretarias]
        selected_tipos = {
            var.get() for var in self.filter_widgets["tipos"].values() if var.get() != "off"}
        if selected_tipos:
            filtered_list = [doc for doc in filtered_list if doc.get(
                "tipo") in selected_tipos]
        selected_privacidade = {var.get(
        ) for var in self.filter_widgets["privacidade"].values() if var.get() != "off"}
        if selected_privacidade:
            filtered_list = [doc for doc in filtered_list if doc.get(
                "privacidade") in selected_privacidade]
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
        self.search_entry.delete(0, "end")
        self.date_start_entry.delete(0, "end")
        self.date_end_entry.delete(0, "end")
        for group in self.filter_widgets.values():
            for var in group.values():
                var.set("off")
        self.apply_filters()

    def view_action(self, doc_path):
        if not os.path.exists(doc_path):
            messagebox.showerror("Erro", "Arquivo não encontrado.")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(doc_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", doc_path], check=True)
            else:
                subprocess.run(["xdg-open", doc_path], check=True)
        except Exception as e:
            messagebox.showerror(
                "Erro ao Abrir", f"Não foi possível abrir o arquivo.\n{e}")

    def edit_action(self, doc_to_edit):
        dialog = AddDocumentDialog(self, existing_data=doc_to_edit)
        self.wait_window(dialog)
        if dialog.result:
            for doc in self.documents:
                if doc['id'] == doc_to_edit['id']:
                    doc.update({'nome': dialog.result['nome'], 'secretaria': dialog.result['secretaria'], 'data': dialog.result['data'],
                               'responsavel': dialog.result['responsavel'], 'privacidade': dialog.result['privacidade'], 'cor': SECRETARIA_CORES.get(dialog.result['secretaria'])})
                    break
            self.apply_filters()

    def delete_action(self, doc_to_delete):
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja apagar permanentemente o documento '{doc_to_delete['nome']}'?", icon='warning'):
            try:
                if os.path.exists(doc_to_delete['path']):
                    os.remove(doc_to_delete['path'])
            except OSError as e:
                messagebox.showerror(
                    "Erro de Exclusão", f"Não foi possível apagar o arquivo do disco.\n{e}")
                return
            self.documents.remove(doc_to_delete)
            self.apply_filters()
            self.update_dashboard_stats()


# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
