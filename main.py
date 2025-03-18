import os
import customtkinter as ctk
from src.database.utilisateur_db import UtilisateurDB
from src.database.compte_db import CompteDB
from src.database.transaction_db import TransactionDB
from src.models.utilisateur import Utilisateur
from src.models.compte import CompteBancaire
from src.models.transaction import Transaction
from ui.login import LoginApp

#Ajustements pour Windows 
if os.name == "nt":
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)

# Configuration CustomTkinter
ctk.set_appearance_mode("system")  # Mode clair/sombre selon le système
ctk.set_default_color_theme("blue")  # Thème CustomTkinter par défaut

from ui.login import LoginApp  # Import après configuration

def main():
    utilisateur_db = UtilisateurDB()
    compte_db = CompteDB()
    transaction_db = TransactionDB()

    # Création d'un utilisateur
    email = "test@example.com"
    mot_de_passe = "SecurePass123!"

    if not utilisateur_db.obtenir_utilisateur(email):
        utilisateur_db.ajouter_utilisateur("John", "Doe", email, Utilisateur.hasher_mot_de_passe(mot_de_passe))
        print("Utilisateur créé avec succès.")

    utilisateur = utilisateur_db.obtenir_utilisateur(email)

    # Création d'un compte bancaire
    compte_id = None
    comptes = compte_db.obtenir_comptes_utilisateur(utilisateur[0])

    if not comptes:
        compte_db.creer_compte(utilisateur[0], "FR123456789", 500.0)
        print("Compte bancaire créé.")
        comptes = compte_db.obtenir_comptes_utilisateur(utilisateur[0])

    compte_id = comptes[0][0]
    
    # Ajout d'une transaction
    transaction_db.ajouter_transaction(compte_id, 100, "dépôt", "Salaire")
    transaction_db.ajouter_transaction(compte_id, 50, "retrait", "Courses")

    # Affichage des transactions
    transactions = transaction_db.obtenir_historique(compte_id)
    print("\nHistorique des transactions :")
    for t in transactions:
        print(f"- {t}")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
