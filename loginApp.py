import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

# ---------------- Configurações iniciais ----------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - Sistema de Gestão Documental")
        self.geometry("800x500")
        self.resizable(False, False)

        # Define a cor de fundo da tela principal
        self.configure(fg_color="#F5F5F5")  # mesma cor de fundo da página (pode mudar)

        # ---------------- Frame principal ----------------
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)  # Espaço até a borda

        # ---------------- Lado esquerdo (imagem) ----------------
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))  # espaço à direita

        try:
            img_path = os.path.join(os.path.dirname(__file__), "imgLoginApp.png")
            ctk_image = ctk.CTkImage(light_image=Image.open(img_path), size=(400, 400))
            label_image = ctk.CTkLabel(left_frame, image=ctk_image, text="")
            label_image.pack(expand=True)
        except Exception as e:
            ctk.CTkLabel(
                left_frame,
                text=f"Imagem não encontrada\n{e}",
                font=("Arial", 16),
                justify="center"
            ).pack(expand=True)

        # ---------------- Lado direito (formulário) ----------------
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))  # espaço à esquerda

        ctk.CTkLabel(right_frame, text="Login", font=("Arial", 22, "bold")).pack(pady=(40, 30))

        self.username_entry = ctk.CTkEntry(
            right_frame, placeholder_text="Usuário", width=280, height=40, corner_radius=8
        )
        self.username_entry.pack(pady=(0, 20))

        self.password_entry = ctk.CTkEntry(
            right_frame, placeholder_text="Senha", width=280, height=40, corner_radius=8, show="*"
        )
        self.password_entry.pack(pady=(0, 30))

        login_button = ctk.CTkButton(
            right_frame, text="Entrar", width=200, height=40, corner_radius=8, command=self.login_action
        )
        login_button.pack()

    def login_action(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if user == "admin" and pwd == "1234":
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.destroy()
            # Aqui você poderia abrir a MainApp()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")


# ---------------- Inicia aplicação ----------------
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
