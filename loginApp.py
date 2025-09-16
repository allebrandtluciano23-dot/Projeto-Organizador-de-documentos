import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from app import MainApp  # Importa a classe da janela principal

# ---------------- Configurações iniciais ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - Sistema de Gestão Documental")
        self.geometry("800x500")
        self.resizable(False, False)

        # ---------------- Frame principal dividido ----------------
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # ---------------- Lado esquerdo (imagem) ----------------
        left_frame = ctk.CTkFrame(
            main_frame, fg_color="transparent", width=400)
        left_frame.pack(side="left", fill="both")

        try:
            # Use CTkImage para melhor qualidade em telas HiDPI
            ctk_image = ctk.CTkImage(light_image=Image.open(
                "img.loginApp.jpg"), size=(360, 460))
            label_image = ctk.CTkLabel(left_frame, image=ctk_image, text="")
            label_image.pack(fill="both", expand=True, padx=20, pady=20)
        except Exception as e:
            ctk.CTkLabel(left_frame, text=f"Imagem\nNão encontrada\n{e}", font=(
                "Arial", 20), justify="center").pack(expand=True)

        # ---------------- Lado direito (informações) ----------------
        right_frame = ctk.CTkFrame(
            main_frame, fg_color="transparent", width=400)
        right_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(right_frame, text="🏢", font=(
            "Arial", 45)).pack(pady=(50, 15))
        ctk.CTkLabel(right_frame, text="Sistema de Gestão Documental",
                     font=("Arial", 16, "bold")).pack(pady=(0, 30))

        # Campos de usuário e senha
        self.username_entry = ctk.CTkEntry(
            right_frame, placeholder_text="Usuário", height=45, width=300, corner_radius=10)
        self.username_entry.pack(pady=(0, 20))

        self.password_entry = ctk.CTkEntry(
            right_frame, placeholder_text="Senha", height=45, width=300, corner_radius=10, show="*")
        self.password_entry.pack(pady=(0, 30))

        # Botão de login
        login_button = ctk.CTkButton(
            right_frame, text="Login", width=250, height=45, corner_radius=10, command=self.login_action)
        login_button.pack(pady=(0, 20))

    def login_action(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if user == "admin" and pwd == "1234":
            self.destroy()  # Fecha a janela de login
            main_app = MainApp()  # Cria a janela principal
            main_app.mainloop()  # Executa a janela principal
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")


# ---------------- Inicia aplicação de Login ----------------
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
