import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

# ---------------- Configurações iniciais ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------------- Função de login ----------------
def login_action():
    user = username_entry.get()
    pwd = password_entry.get()
    
    if user == "admin" and pwd == "1234":
        messagebox.showinfo("Login", "Login bem-sucedido!")
        app.destroy()
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos!")

# ---------------- Janela principal ----------------
app = ctk.CTk()
app.title("Login - Sistema de Gestão Documental")
app.geometry("800x500")
app.resizable(False, False)

# ---------------- Frame principal dividido ----------------
main_frame = ctk.CTkFrame(app, fg_color="transparent")
main_frame.pack(fill="both", expand=True)

# ---------------- Lado esquerdo (imagem) ----------------
left_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=400)
left_frame.pack(side="left", fill="both")

# Carregar imagem diretamente no frame da esquerda
try:
    image = Image.open("img.loginApp.jpg")
    image = image.resize((360, 460))
    photo = ImageTk.PhotoImage(image)
    label_image = ctk.CTkLabel(left_frame, image=photo, text="")
    label_image.pack(fill="both", expand=True, padx=20, pady=20)
except Exception as e:
    ctk.CTkLabel(left_frame, text=f"Imagem\nNão encontrada\n{e}", font=("Arial", 20), justify="center").pack(expand=True)

# ---------------- Lado direito (informações) ----------------
right_frame = ctk.CTkFrame(main_frame, fg_color="transparent", width=400)
right_frame.pack(side="left", fill="both", expand=True)

# Ícone ou logo
ctk.CTkLabel(right_frame, text="🏢", font=("Arial", 45)).pack(pady=(50,15))
ctk.CTkLabel(right_frame, text="Sistema de Gestão Documental", font=("Arial", 16, "bold")).pack(pady=(0,30))

# Campos de usuário e senha centralizados
username_entry = ctk.CTkEntry(right_frame, placeholder_text="Usuário", height=45, width=300, corner_radius=10)
username_entry.pack(pady=(0,20))

password_entry = ctk.CTkEntry(right_frame, placeholder_text="Senha", height=45, width=300, corner_radius=10, show="*")
password_entry.pack(pady=(0,30))

# Botão de login
login_button = ctk.CTkButton(right_frame, text="Login", width=250, height=45, corner_radius=10, command=login_action)
login_button.pack(pady=(0,20))

# ---------------- Inicia aplicação ----------------
app.mainloop()
