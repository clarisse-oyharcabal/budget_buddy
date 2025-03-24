import customtkinter as ctk
from data.database import *
from gui.config import COLORS
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from decimal import Decimal

class HomePageApp(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.title("Budget Buddy - Accueil")
        self.geometry("800x600")
        self.configure(bg="#DFD4C1")
        self.db = Database()
        self.load_images()
        self.user_data = user_data
        self.show_home_screen(self.user_data)

    def load_images(self):
        """Charge les images de fond et icônes."""
        self.images = {
            "background": ctk.CTkImage(Image.open("img/login_background.png"), size=(800, 600))
        }
           
   

    def apply_background(self, parent, image_key="background"):
        """Ajoute l'image de fond à la section spécifiée."""
        self.bg_label = ctk.CTkLabel(parent, image=self.images[image_key], text="", bg_color="#DFD4C1" )
        self.bg_label.place(relwidth=1, relheight=1)
    
    def show_home_screen(self, user_data):
        """Affiche la page d'accueil avec un design cohérent."""
        self.clear_screen()
        self.apply_background(self)
        
        # Barre latérale
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=COLORS["bamboo_dark"])
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Profil utilisateur
        self.profile_label = ctk.CTkLabel(self.sidebar, text=f"{user_data['first_name']} {user_data['last_name']}",
                                        font=("Helvetica", 16, "bold"), text_color="white")
        self.profile_label.pack(pady=20)

        # Boutons de navigation
        buttons = [
            ("Accueil", self.show_home_content),
            ("Comptes", self.show_accounts),
            ("Transactions", self.show_transactions),
            ("Déposer", self.show_deposit_screen),
            ("Retirer", self.show_withdraw_screen),
            ("Transférer", self.show_transfer_screen),
            ("Déconnexion", self.logout)
        ]

        for text, command in buttons:
            ctk.CTkButton(self.sidebar, text=text, fg_color=COLORS["moss"], hover_color=COLORS["forest"],
                        command=lambda cmd=command: cmd(user_data)).pack(pady=5, padx=10, fill="x")
        
        # Contenu principal
        self.main_content = ctk.CTkFrame(self, fg_color=COLORS["bamboo_light"], corner_radius=15)
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.show_home_content(user_data)



    def show_home_content(self, user_data):
        """Affiche le contenu de la page d'accueil."""
        self.clear_main_content()
        self.apply_background(self.main_content)
        
        ctk.CTkLabel(self.main_content, text=f"Bienvenue {user_data['first_name']} !",
                    font=("Helvetica", 24, "bold"), text_color=COLORS["forest"]).pack(pady=20)
        
        # Conteneur du solde total
        summary_frame = ctk.CTkFrame(self.main_content, fg_color=COLORS["moss"], corner_radius=15)
        summary_frame.pack(pady=20, padx=20, fill="x")

        accounts = self.db.get_user_accounts(user_data['user_id'])
        total_balance = sum(account['balance'] for account in accounts)
        ctk.CTkLabel(summary_frame, text=f"Solde total: {total_balance}€", font=("Helvetica", 18), text_color="white").pack(pady=10)
        
        self.display_expense_chart(user_data['user_id'])
        self.display_recent_transactions(user_data['user_id'])


    def show_accounts(self, user_data):
        """Affiche les comptes de l'utilisateur."""
        self.clear_main_content()
        self.apply_background(self.main_content)
        
        ctk.CTkLabel(self.main_content, text="Vos Comptes", font=("Helvetica", 20, "bold"), text_color=COLORS["forest"]).pack(pady=20)
        accounts = self.db.get_user_accounts(user_data['user_id'])
        
        if not accounts:
            ctk.CTkLabel(self.main_content, text="Aucun compte trouvé.", font=("Helvetica", 14)).pack()
        else:
            for account in accounts:
                account_info = f"{account['account_name']} - Solde: {account['balance']}€"
                ctk.CTkLabel(self.main_content, text=account_info, font=("Helvetica", 14)).pack(pady=5)

        
    def show_transactions(self, user_data):
        """Affiche les transactions récentes avec des filtres intégrés."""
        self.clear_main_content()
       
        
        # Titre
        self.transactions_label = ctk.CTkLabel(self.main_content, text="Transactions Récentes", font=("Helvetica", 20))
        self.transactions_label.pack(pady=20)

        # Filtres par date
        self.start_date_entry = ctk.CTkEntry(self.main_content, placeholder_text="Date de début (YYYY-MM-DD)",placeholder_text_color="#606060",text_color="black", width=350, height=50, fg_color=COLORS["bamboo_light"], corner_radius=10, bg_color="#DFD4C1")
        self.start_date_entry.pack(pady=10)

        self.end_date_entry = ctk.CTkEntry(self.main_content, placeholder_text="Date de fin (YYYY-MM-DD)", placeholder_text_color="#606060",text_color="black", width=350, height=50, fg_color=COLORS["bamboo_light"], corner_radius=10, bg_color="#DFD4C1")
        self.end_date_entry.pack(pady=10)

        # Filtres par catégorie
        categories = [cat['category_name'] for cat in self.db.get_categories()]
        self.category_combobox = ctk.CTkComboBox(self.main_content, values=categories)
        self.category_combobox.pack(pady=10)

        # Filtres par type de transaction
        types = [t['type_name'] for t in self.db.get_transaction_types()]
        self.type_combobox = ctk.CTkComboBox(self.main_content, values=types)
        self.type_combobox.pack(pady=10)

        # Tri par montant
        self.sort_order_combobox = ctk.CTkComboBox(self.main_content, values=["Croissant", "Décroissant"])
        self.sort_order_combobox.pack(pady=10)

        # Bouton pour appliquer les filtres
        self.apply_filters_button = self.transfer_button =  ctk.CTkButton(
            self.main_content, 
            text="Déposer", 
            command=lambda: self.deposit(user_data),
            fg_color=COLORS["forest"], 
            hover_color=COLORS["bamboo_dark"],
            text_color="white",
            corner_radius=15,
            font=("Helvetica", 18, "bold")
        )

        # Afficher les transactions filtrées par défaut
        self.apply_transaction_filters(user_data)

    def apply_transaction_filters(self, user_data):
        """Applique les filtres et affiche les transactions correspondantes."""
        filters = {}
        
        start_date = self.start_date_entry.get()
        if start_date:
            filters['start_date'] = start_date
        
        end_date = self.end_date_entry.get()
        if end_date:
            filters['end_date'] = end_date
        
        category = self.category_combobox.get()
        if category:
            categories = {cat['category_name']: cat['category_id'] for cat in self.db.get_categories()}
            filters['category_id'] = categories[category]
        
        transaction_type = self.type_combobox.get()
        if transaction_type:
            types = {t['type_name']: t['type_id'] for t in self.db.get_transaction_types()}
            filters['type_id'] = types[transaction_type]
        
        sort_order = self.sort_order_combobox.get()
        if sort_order:
            filters['sort_by'] = 'amount'
            filters['sort_order'] = 'asc' if sort_order == "Croissant" else 'desc'
        
        accounts = self.db.get_user_accounts(user_data['user_id'])
        for account in accounts:
            transactions = self.db.get_account_transactions(account['account_id'], filters)
            
            # Afficher les transactions filtrées
            if not transactions:
                no_transactions_label = ctk.CTkLabel(self.main_content, text=f"Aucune transaction pour {account['account_name']}.", font=("Helvetica", 14))
                no_transactions_label.pack()
                continue
            
            for transaction in transactions:
                transaction_info = f"{transaction['formatted_date']} - {transaction['description']}: {transaction['amount']}€"
                transaction_label = ctk.CTkLabel(self.main_content, text=transaction_info, font=("Helvetica", 14))
                transaction_label.pack(pady=5)
    
    def display_expense_chart(self, user_id):
        """Affiche un graphique des dépenses par catégorie."""
        category_data = self.db.get_category_summary(user_id)
        
        if not category_data:
            ctk.CTkLabel(self.main_content, text="Aucune donnée disponible.", font=("Helvetica", 14)).pack()
            return
        
        categories = list(category_data.keys())
        amounts = list(category_data.values())
        
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, master=self.main_content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

    
    def display_recent_transactions(self, user_id):
        """Affiche les transactions récentes."""
        accounts = self.db.get_user_accounts(user_id)
        for account in accounts:
            transactions = self.db.get_account_transactions(account['account_id'])
            for transaction in transactions[:5]:
                transaction_info = f"{transaction['formatted_date']} - {transaction['description']}: {transaction['amount']}€"
                ctk.CTkLabel(self.main_content, text=transaction_info, font=("Helvetica", 14)).pack()

    
    def show_deposit_screen(self, user_data):
        """Affiche l'interface pour déposer de l'argent avec un design moderne et zen."""
        self.clear_main_content()
       
        self.deposit_label = ctk.CTkLabel(self.main_content, text="Déposer de l'argent", font=("Helvetica", 24, "bold"), text_color=COLORS["moss"])
        self.deposit_label.pack(pady=20)
        
        self.amount_entry = ctk.CTkEntry(self.main_content, placeholder_text="Montant",placeholder_text_color="#606060",text_color="black", width=350, height=50, fg_color=COLORS["bamboo_light"], corner_radius=10, bg_color="#DFD4C1")
        self.amount_entry.pack(pady=10)
        
        self.account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])], fg_color=COLORS["bamboo_light"], corner_radius=10)
        self.account_combobox.pack(pady=10)
        
        self.deposit_button = ctk.CTkButton(
            self.main_content, 
            text="Déposer", 
            command=lambda: self.deposit(user_data),
            fg_color=COLORS["forest"], 
            hover_color=COLORS["bamboo_dark"],
            text_color="white",
            corner_radius=15,
            font=("Helvetica", 18, "bold")
        )
        self.deposit_button.pack(pady=20)
    
    def deposit(self, user_data):
        """Effectue un dépôt sur le compte sélectionné."""
        try:
            amount = Decimal(self.amount_entry.get())  # Convertir en Decimal
            account_name = self.account_combobox.get()
            accounts = self.db.get_user_accounts(user_data['user_id'])
            account_id = next(acc['account_id'] for acc in accounts if acc['account_name'] == account_name)
            
            success, message = self.db.add_transaction(account_id, "Dépôt", "Dépôt d'argent", amount, 1)
            if success:
                print("Dépôt réussi")
                self.show_home_content(user_data)
            else:
                print("Erreur lors du dépôt:", message)
        except ValueError:
            print("Veuillez saisir un montant valide.")
    
    def show_withdraw_screen(self, user_data):
        """Affiche l'interface pour retirer de l'argent."""
        self.clear_main_content()
       
        self.withdraw_label = ctk.CTkLabel(self.main_content, text="Retirer de l'argent", font=("Helvetica", 24, "bold"), text_color=COLORS["moss"])
        self.withdraw_label.pack(pady=20)
        
        self.amount_entry = ctk.CTkEntry(self.main_content, placeholder_text="Montant", placeholder_text_color="#606060",text_color="black", width=350, height=50, fg_color=COLORS["bamboo_light"], corner_radius=10, bg_color="#DFD4C1")
        self.amount_entry.pack(pady=10)
        
        self.account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.account_combobox.pack(pady=10)
        
        self.withdraw_button = self.transfer_button =  ctk.CTkButton(
            self.main_content, 
            text="Déposer", 
            command=lambda: self.deposit(user_data),
            fg_color=COLORS["forest"], 
            hover_color=COLORS["bamboo_dark"],
            text_color="white",
            corner_radius=15,
            font=("Helvetica", 18, "bold")
        )
        self.withdraw_button.pack(pady=20)
    
    def withdraw(self, user_data):
        """Effectue un retrait sur le compte sélectionné."""
        try:
            # Convertir le montant en Decimal
            amount = Decimal(self.amount_entry.get())
            account_name = self.account_combobox.get()
            
            # Récupérer les comptes de l'utilisateur
            accounts = self.db.get_user_accounts(user_data['user_id'])
            
            # Trouver l'ID du compte sélectionné
            account_id = next(acc['account_id'] for acc in accounts if acc['account_name'] == account_name)
            
            # Effectuer le retrait
            success, message = self.db.add_transaction(account_id, "Retrait", "Retrait d'argent", amount, 2)
            
            if success:
                print("Retrait réussi")
                self.show_home_content(user_data)  # Revenir à l'accueil
            else:
                print("Erreur lors du retrait:", message)
        except ValueError:
            print("Veuillez saisir un montant valide.")
        except Exception as e:
            print(f"Erreur inattendue lors du retrait: {e}")
    
    def show_transfer_screen(self, user_data):
        """Affiche l'interface pour transférer de l'argent."""
        self.clear_main_content()
       
        
        self.transfer_label = ctk.CTkLabel(self.main_content, text="Transférer de l'argent", font=("Helvetica", 24, "bold"), text_color=COLORS["moss"])
        self.transfer_label.pack(pady=20)
        
        self.amount_entry = ctk.CTkEntry(self.main_content, placeholder_text="Montant",placeholder_text_color="#606060",text_color="black", width=350, height=50, fg_color=COLORS["bamboo_light"], corner_radius=10, bg_color="#DFD4C1")
        self.amount_entry.pack(pady=10)
        
        self.from_account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.from_account_combobox.pack(pady=10)
        
        self.to_account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.to_account_combobox.pack(pady=10)
        
        self.transfer_button =  ctk.CTkButton(
            self.main_content, 
            text="Déposer", 
            command=lambda: self.deposit(user_data),
            fg_color=COLORS["forest"], 
            hover_color=COLORS["bamboo_dark"],
            text_color="white",
            corner_radius=15,
            font=("Helvetica", 18, "bold")
        )
        self.transfer_button.pack(pady=20)
    
    def transfer(self, user_data):
        """Effectue un transfert entre deux comptes."""
        try:
            # Convertir le montant en Decimal
            amount = Decimal(self.amount_entry.get())
            from_account_name = self.from_account_combobox.get()
            to_account_name = self.to_account_combobox.get()
            
            # Récupérer les comptes de l'utilisateur
            accounts = self.db.get_user_accounts(user_data['user_id'])
            
            # Trouver les ID des comptes source et destination
            from_account_id = next(acc['account_id'] for acc in accounts if acc['account_name'] == from_account_name)
            to_account_id = next(acc['account_id'] for acc in accounts if acc['account_name'] == to_account_name)
            
            # Effectuer le transfert
            success, message = self.db.add_transaction(from_account_id, "Transfert", "Transfert d'argent", amount, 3, to_account_id=to_account_id)
            
            if success:
                print("Transfert réussi")
                self.show_home_content(user_data)  # Revenir à l'accueil
            else:
                print("Erreur lors du transfert:", message)
        except ValueError:
            print("Veuillez saisir un montant valide.")
        except Exception as e:
            print(f"Erreur inattendue lors du transfert: {e}")
        
    
    def apply_filters(self, user_data):
        """Applique les filtres et affiche les transactions correspondantes."""
        filters = {}
        
        start_date = self.start_date_entry.get()
        if start_date:
            filters['start_date'] = start_date
        
        end_date = self.end_date_entry.get()
        if end_date:
            filters['end_date'] = end_date
        
        category = self.category_combobox.get()
        if category:
            categories = {cat['category_name']: cat['category_id'] for cat in self.db.get_categories()}
            filters['category_id'] = categories[category]
        
        transaction_type = self.type_combobox.get()
        if transaction_type:
            types = {t['type_name']: t['type_id'] for t in self.db.get_transaction_types()}
            filters['type_id'] = types[transaction_type]
        
        sort_order = self.sort_order_combobox.get()
        if sort_order:
            filters['sort_by'] = 'amount'
            filters['sort_order'] = 'asc' if sort_order == "Croissant" else 'desc'
        
        accounts = self.db.get_user_accounts(user_data['user_id'])
        for account in accounts:
            transactions = self.db.get_account_transactions(account['account_id'], filters)
            print(f"Transactions filtrées pour {account['account_name']}: {transactions}")
    
    def logout(self):
        """Ferme la page d'accueil et retourne à l'écran de connexion."""
        self.destroy()  # Ferme la fenêtre actuelle
        from gui.login import LoginApp
        login_app = LoginApp()  # Ouvre la fenêtre de login
        login_app.mainloop()

    def clear_screen(self):
        """Supprime tous les widgets de la fenêtre."""
        for widget in self.winfo_children():
            widget.destroy()

    def clear_main_content(self):
        """Supprime le contenu principal."""
        for widget in self.main_content.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    fake_user = {"first_name": "Test", "last_name": "User"}  # Simuler un utilisateur
    app = HomePageApp(fake_user)
    app.mainloop()