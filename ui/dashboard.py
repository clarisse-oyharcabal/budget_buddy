import customtkinter as ctk

class Dashboard(ctk.CTk):
    def __init__(self, utilisateur):
        super().__init__()
        self.title("Budget Buddy - Tableau de Bord")
        self.geometry("600x400")

        self.label_bienvenue = ctk.CTkLabel(self, text=f"Bienvenue {utilisateur[1]} {utilisateur[2]} !", font=("Arial", 20, "bold"))
        self.label_bienvenue.pack(pady=20)

        self.bouton_transactions = ctk.CTkButton(self, text="Gérer mes transactions", command=self.ouvrir_transactions)
        self.bouton_transactions.pack(pady=10)

        self.bouton_deconnexion = ctk.CTkButton(self, text="Se déconnecter", command=self.deconnexion)
        self.bouton_deconnexion.pack(pady=10)

    def ouvrir_transactions(self):
        from ui.transactions import TransactionsApp  # Import local
        self.destroy()
        TransactionsApp().mainloop()
    
    def ouvrir_login(self):
        from ui.login import LoginApp  # Import local pour éviter l'import circulaire
        self.destroy()
        LoginApp().mainloop()

    def deconnexion(self):
        self.destroy()
        LoginApp().mainloop()
