import customtkinter as ctk
from src.database.transaction_db import TransactionDB

class TransactionsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Buddy - Transactions")
        self.geometry("600x400")

        self.transaction_db = TransactionDB()

        self.label_titre = ctk.CTkLabel(self, text="Transactions", font=("Arial", 20, "bold"))
        self.label_titre.pack(pady=20)

        self.entry_montant = ctk.CTkEntry(self, placeholder_text="Montant")
        self.entry_montant.pack(pady=10)

        self.bouton_depot = ctk.CTkButton(self, text="Déposer", command=lambda: self.ajouter_transaction("dépôt"))
        self.bouton_depot.pack(pady=5)

        self.bouton_retrait = ctk.CTkButton(self, text="Retirer", command=lambda: self.ajouter_transaction("retrait"))
        self.bouton_retrait.pack(pady=5)

    def ajouter_transaction(self, type_transaction):
        montant = float(self.entry_montant.get())
        self.transaction_db.ajouter_transaction(1, montant, type_transaction, "Transaction manuelle")
