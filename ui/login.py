import customtkinter as ctk
from src.database.utilisateur_db import UtilisateurDB
from src.models.utilisateur import Utilisateur
from ui.dashboard import Dashboard

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Buddy - Connexion")
        self.geometry("400x500")

        self.utilisateur_db = UtilisateurDB()

        # Interface
        self.label_titre = ctk.CTkLabel(self, text="Connexion", font=("Arial", 24, "bold"))
        self.label_titre.pack(pady=20)

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email")
        self.entry_email.pack(pady=10)

        self.entry_mot_de_passe = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*")
        self.entry_mot_de_passe.pack(pady=10)

        self.bouton_connexion = ctk.CTkButton(self, text="Se connecter", command=self.connexion)
        self.bouton_connexion.pack(pady=20)

        self.label_inscription = ctk.CTkLabel(self, text="Pas encore de compte ?")
        self.label_inscription.pack()

        self.bouton_inscription = ctk.CTkButton(self, text="Créer un compte", command=self.inscription)
        self.bouton_inscription.pack(pady=10)

    def connexion(self):
        email = self.entry_email.get()
        mot_de_passe = self.entry_mot_de_passe.get()

        utilisateur = self.utilisateur_db.obtenir_utilisateur(email)
        if utilisateur and Utilisateur(utilisateur[0], utilisateur[1], utilisateur[2], utilisateur[3], utilisateur[4]).verifier_mot_de_passe(mot_de_passe):
            self.destroy()
            Dashboard(utilisateur)
        else:
            ctk.CTkLabel(self, text="Identifiants incorrects", text_color="red").pack()

    def inscription(self):
        self.destroy()
        InscriptionApp().mainloop()

class InscriptionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inscription")
        self.geometry("400x500")

        self.utilisateur_db = UtilisateurDB()

        # Interface
        self.label_titre = ctk.CTkLabel(self, text="Inscription", font=("Arial", 24, "bold"))
        self.label_titre.pack(pady=20)

        self.entry_nom = ctk.CTkEntry(self, placeholder_text="Nom")
        self.entry_nom.pack(pady=10)

        self.entry_prenom = ctk.CTkEntry(self, placeholder_text="Prénom")
        self.entry_prenom.pack(pady=10)

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email")
        self.entry_email.pack(pady=10)

        self.entry_mot_de_passe = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*")
        self.entry_mot_de_passe.pack(pady=10)

        self.bouton_inscription = ctk.CTkButton(self, text="S'inscrire", command=self.creer_utilisateur)
        self.bouton_inscription.pack(pady=20)

    def creer_utilisateur(self):
        nom = self.entry_nom.get()
        prenom = self.entry_prenom.get()
        email = self.entry_email.get()
        mot_de_passe = Utilisateur.hasher_mot_de_passe(self.entry_mot_de_passe.get())

        if self.utilisateur_db.ajouter_utilisateur(nom, prenom, email, mot_de_passe):
            self.destroy()
            LoginApp().mainloop()
        else:
            ctk.CTkLabel(self, text="Erreur d'inscription", text_color="red").pack()

