import os
import sys
import io

# Changer l'encodage de la console en UTF-8
os.system('chcp 65001 > nul')

# Forcer l'encodage de la sortie standard en UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import customtkinter as ctk
from PIL import Image
from data.database import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .config import COLORS
from .homepage import HomePageApp

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Buddy")
        self.geometry("800x600")
        self.db = Database()
        self.load_images()
        self.show_login_screen()
        self.show_pass = False

    def load_images(self):
        """Charge les images de fond et icônes."""
        self.images = {
            "background": ctk.CTkImage(
                light_image=Image.open("img/login_background.png"),
                dark_image=Image.open("img/login_background.png"),
                size=(800, 600)
            ),
            "eye": ctk.CTkImage(
                light_image=Image.open("img/login_eye.png"),
                dark_image=Image.open("img/login_eye.png"),
                size=(25, 25)
            )
        }
    
    def show_login_screen(self):
        """Affiche l'interface de connexion."""
        self.clear_screen()
        self.bg_label = ctk.CTkLabel(self, image=self.images["background"])
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.login_container = ctk.CTkFrame(
            self, fg_color="#07290B", bg_color="#DFD4C1",
            width=450, height=550, corner_radius=20
        )
        self.login_container.place(relx=0.03, rely=0.56, anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.login_container, text="Let's connect !",
            font=("Helvetica", 16), fg_color="transparent", text_color="green"
        )
        self.subtitle_label.pack(pady=(20, 10), padx=20)

        self.email_entry = ctk.CTkEntry(self.login_container, placeholder_text="Email address", placeholder_text_color="#606060", width=350, height=50, fg_color=COLORS["bamboo_light"], text_color="black")
        self.email_entry.pack(pady=10, padx=20)

        self.password_entry = ctk.CTkEntry(self.login_container, placeholder_text="Password", placeholder_text_color="#606060", width=350, height=50, fg_color=COLORS["bamboo_light"], show="*", text_color="black")
        self.password_entry.pack(pady=10, padx=20)

        self.show_pass_button = ctk.CTkButton(
            self.login_container, image=self.images["eye"], 
            width=30, height=30, text="", fg_color="transparent",
            hover_color=COLORS["bamboo_dark"], 
            command=self.toggle_password_visibility
        )
        self.show_pass_button.pack(pady=5, padx=20)


        self.login_button = ctk.CTkButton(
            self.login_container, text="Log In", width=350, height=50,
            corner_radius=10, fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=self.login
        )
        self.login_button.pack(pady=20, padx=20)

        self.register_label = ctk.CTkLabel(
            self.login_container, text="No account? Create one!",
            font=("Helvetica", 13), text_color="green"
        )
        self.register_label.pack(pady=10, padx=20)

        self.register_label.bind("<Enter>", lambda e: self.register_label.configure(font=("Helvetica", 15)))
        self.register_label.bind("<Leave>", lambda e: self.register_label.configure(font=("Helvetica", 13)))


        self.register_button = ctk.CTkButton(
            self.login_container, text="Sign Up", width=150, height=30,
            corner_radius=10, fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=self.show_register_screen
        )
        self.register_button.pack(pady=10, padx=20)

    def toggle_password_visibility(self):
        """Affiche ou masque le mot de passe."""
        if hasattr(self, 'show_pass') and self.show_pass:
            self.password_entry.configure(show="*")
        else:
            self.password_entry.configure(show="")
        self.show_pass = not self.show_pass


    def login(self):
        """Gestion de la connexion utilisateur."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        success, message, user_data = self.db.login_user(email, password)
        if success:
            self.destroy()  # Ferme la fenêtre de login
            home_app = HomePageApp(user_data)  # Lance la page d'accueil
            home_app.mainloop()
        else:
            print("Échec de connexion: ", message)
    
    def show_register_screen(self):
        """Affiche l'écran d'inscription."""
        self.clear_screen()
        self.bg_label = ctk.CTkLabel(self, image=self.images["background"])
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.register_container = ctk.CTkFrame(
            self, fg_color="#07290B", bg_color="#DFD4C1",
            width=450, height=550, corner_radius=20
        )
        self.register_container.place(relx=0.03, rely=0.56, anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.register_container, text="Create Your Account",
            font=("Helvetica", 16), fg_color="transparent", text_color="green"
        )
        self.subtitle_label.pack(pady=(20, 10), padx=20)

        self.first_name_entry = ctk.CTkEntry(self.register_container, placeholder_text="First Name", placeholder_text_color="#606060", width=350, height=50, fg_color=COLORS["bamboo_light"], text_color="black")
        self.first_name_entry.pack(pady=10, padx=20)

        self.last_name_entry = ctk.CTkEntry(self.register_container, placeholder_text="Last Name", placeholder_text_color="#606060", width=350, height=50, fg_color=COLORS["bamboo_light"], text_color="black")
        self.last_name_entry.pack(pady=10, padx=20)

        self.email_register_entry = ctk.CTkEntry(self.register_container, placeholder_text="Email", placeholder_text_color="#606060", width=350, height=50, fg_color=COLORS["bamboo_light"], text_color="black")
        self.email_register_entry.pack(pady=10, padx=20)

        self.password_register_entry = ctk.CTkEntry(self.register_container, placeholder_text="Password", placeholder_text_color="#606060", width=350, height=50, fg_color=COLORS["bamboo_light"], text_color="black")
        self.password_register_entry.pack(pady=10, padx=20)

        self.show_pass_register_button = ctk.CTkButton(
            self.register_container, image=self.images["eye"], 
            width=30, height=30, text="", fg_color="transparent",
            hover_color=COLORS["bamboo_dark"], 
            command=self.toggle_register_password_visibility
        )
        self.show_pass_register_button.pack(pady=5, padx=20)

        self.register_submit_button = ctk.CTkButton(
            self.register_container, text="Register", width=350, height=50,
            corner_radius=10, fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=self.register
        )
        self.register_submit_button.pack(pady=20, padx=20)

        self.back_to_login_button = ctk.CTkButton(
            self.register_container, text="Back to Login", width=150, height=30,
            corner_radius=10, fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=self.show_login_screen
        )
        self.back_to_login_button.pack(pady=10, padx=20)

    def toggle_register_password_visibility(self):
        """Affiche ou masque le mot de passe sur l'inscription."""
        if hasattr(self, 'show_pass') and self.show_pass:
            self.password_register_entry.configure(show="*")
        else:
            self.password_register_entry.configure(show="")
        self.show_pass = not self.show_pass
        
    def register(self):
        """Gestion de l'inscription."""
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        email = self.email_register_entry.get()
        password = self.password_register_entry.get()
        success, message, _ = self.db.register_user(first_name, last_name, email, password)
        if success:
            self.show_login_screen()
        else:
            print("Échec d'inscription: ", message)
    
    
    def clear_screen(self):
        """Supprime tous les widgets de la fenêtre."""
        for widget in self.winfo_children():
            widget.destroy()
    
    def clear_main_content(self):
        """Supprime le contenu principal."""
        for widget in self.main_content.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()