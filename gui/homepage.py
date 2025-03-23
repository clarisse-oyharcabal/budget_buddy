import customtkinter as ctk
from data.database import *
from gui.config import COLORS
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

class HomePageApp(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()
        self.title("Budget Buddy - Accueil")
        self.geometry("800x600")
        self.db = Database()
        self.load_images()
        self.user_data = user_data
        self.show_home_screen(self.user_data)

    def load_images(self):
        """Charge les images de fond et icônes."""
        self.images = {
            "background": ctk.CTkImage(
                light_image=Image.open("img/login_background.png"),
                dark_image=Image.open("img/login_background.png"),
                size=(800, 600)
            )
        }
   
    def show_home_screen(self, user_data):
        """Affiche la page d'accueil après connexion avec graphiques et transactions."""
        self.clear_screen()

        # Appliquer le même fond d'écran que login
        self.bg_label = ctk.CTkLabel(self, image=self.images["background"])
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Barre latérale
        self.sidebar = ctk.CTkFrame(self, width=200, height=800, fg_color="#07290B", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Profil utilisateur
        self.profile_label = ctk.CTkLabel(self.sidebar, text=f"{user_data['first_name']} {user_data['last_name']}", font=("Helvetica", 16))
        self.profile_label.pack(pady=20)

        # Boutons de navigation avec couleur verte lorsque possible
        self.home_button = ctk.CTkButton(self.sidebar, text="Accueil", fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=lambda: self.show_home_content(user_data))
        self.home_button.pack(pady=10)

        self.accounts_button = ctk.CTkButton(self.sidebar, text="Comptes", fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=lambda: self.show_accounts(user_data))
        self.accounts_button.pack(pady=10)

        self.transactions_button = ctk.CTkButton(self.sidebar, text="Transactions", fg_color=COLORS["moss"], hover_color=COLORS["bamboo_dark"], command=lambda: self.show_transactions(user_data))
        self.transactions_button.pack(pady=10)

        self.deposit_button = ctk.CTkButton(self.sidebar, text="Déposer", fg_color=COLORS["forest"], hover_color=COLORS["bamboo_dark"], command=lambda: self.show_deposit_screen(user_data))
        self.deposit_button.pack(pady=10)

        self.withdraw_button = ctk.CTkButton(self.sidebar, text="Retirer", fg_color=COLORS["forest"], hover_color=COLORS["bamboo_dark"], command=lambda: self.show_withdraw_screen(user_data))
        self.withdraw_button.pack(pady=10)

        self.transfer_button = ctk.CTkButton(self.sidebar, text="Transférer", fg_color=COLORS["forest"], hover_color=COLORS["bamboo_dark"], command=lambda: self.show_transfer_screen(user_data))
        self.transfer_button.pack(pady=10)

        self.logout_button = ctk.CTkButton(self.sidebar, text="Déconnexion", fg_color=COLORS["bamboo_dark"], hover_color=COLORS["bamboo_medium"], command=self.logout)
        self.logout_button.pack(pady=10)

        # Contenu principal
        self.main_content = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Afficher le contenu par défaut (Accueil)
        self.show_home_content(user_data)
    
    def show_home_content(self, user_data):
        """Affiche le contenu de la page d'accueil."""
        self.clear_main_content()
        
        # Bienvenue
        self.welcome_label = ctk.CTkLabel(self.main_content, text=f"Bienvenue {user_data['first_name']} !", font=("Helvetica", 24))
        self.welcome_label.pack(pady=20)
        
        # Afficher le solde total
        accounts = self.db.get_user_accounts(user_data['user_id'])
        total_balance = sum(account['balance'] for account in accounts)
        self.total_balance_label = ctk.CTkLabel(self.main_content, text=f"Solde total: {total_balance}€", font=("Helvetica", 18))
        self.total_balance_label.pack(pady=10)
        
        # Afficher les alertes non lues
        alerts = self.db.get_alerts(user_data['user_id'])
        unread_alerts = [alert for alert in alerts if not alert['is_read']]
        
        if unread_alerts:
            self.alerts_label = ctk.CTkLabel(self.main_content, text="Alertes non lues :", font=("Helvetica", 18))
            self.alerts_label.pack(pady=10)
            
            for alert in unread_alerts:
                alert_text = f"{alert['message']} - {alert['created_at']}"
                alert_label = ctk.CTkLabel(self.main_content, text=alert_text, font=("Helvetica", 14))
                alert_label.pack()
        
        # Afficher les paiements programmés
        for account in accounts:
            scheduled_payments = self.db.get_scheduled_payments(account['account_id'])
            if scheduled_payments:
                self.payments_label = ctk.CTkLabel(self.main_content, text=f"Paiements programmés pour {account['account_name']}:", font=("Helvetica", 18))
                self.payments_label.pack(pady=10)
                
                for payment in scheduled_payments:
                    payment_text = f"{payment['description']} - {payment['amount']}€ - Prochain paiement : {payment['next_date']}"
                    payment_label = ctk.CTkLabel(self.main_content, text=payment_text, font=("Helvetica", 14))
                    payment_label.pack()
        
        # Afficher le résumé mensuel
        monthly_summary = self.db.get_monthly_summary(user_data['user_id'])
        if monthly_summary:
            self.summary_label = ctk.CTkLabel(self.main_content, text="Résumé mensuel :", font=("Helvetica", 18))
            self.summary_label.pack(pady=10)
            
            for month, data in monthly_summary.items():
                summary_text = f"{month} - Revenus: {data['income']}€, Dépenses: {data['expenses']}€, Solde: {data['net']}€"
                summary_label = ctk.CTkLabel(self.main_content, text=summary_text, font=("Helvetica", 14))
                summary_label.pack()
        
        # Graphique des dépenses
        self.display_expense_chart(user_data['user_id'])
        
        # Transactions récentes
        self.display_recent_transactions(user_data['user_id'])
    
    def show_accounts(self, user_data):
        """Affiche les comptes de l'utilisateur."""
        self.clear_main_content()
        
        # Titre
        self.accounts_label = ctk.CTkLabel(self.main_content, text="Vos Comptes", font=("Helvetica", 20))
        self.accounts_label.pack(pady=20)
        
        # Récupérer les comptes
        accounts = self.db.get_user_accounts(user_data['user_id'])
        print(f"Comptes récupérés : {accounts}")  # Debugging
    
        if not accounts:
            no_accounts_label = ctk.CTkLabel(self.main_content, text="Aucun compte trouvé.", font=("Helvetica", 14))
            no_accounts_label.pack()
            return
        
        # Afficher les comptes
        for account in accounts:
            account_info = f"{account['account_name']} - Solde: {account['balance']}€"
            account_label = ctk.CTkLabel(self.main_content, text=account_info, font=("Helvetica", 14))
            account_label.pack(pady=5)
    
    def show_transactions(self, user_data):
        """Affiche les transactions récentes avec des filtres intégrés."""
        self.clear_main_content()
        
        # Titre
        self.transactions_label = ctk.CTkLabel(self.main_content, text="Transactions Récentes", font=("Helvetica", 20))
        self.transactions_label.pack(pady=20)

        # Filtres par date
        self.start_date_entry = ctk.CTkEntry(self.main_content, placeholder_text="Date de début (YYYY-MM-DD)", width=350, height=50)
        self.start_date_entry.pack(pady=10)

        self.end_date_entry = ctk.CTkEntry(self.main_content, placeholder_text="Date de fin (YYYY-MM-DD)", width=350, height=50)
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
        self.apply_filters_button = ctk.CTkButton(self.main_content, text="Appliquer les filtres", command=lambda: self.apply_transaction_filters(user_data))
        self.apply_filters_button.pack(pady=20)

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
        print(f"Données du graphique : {category_data}")  # Debugging
        
        if not category_data:
            no_data_label = ctk.CTkLabel(self.main_content, text="Aucune donnée disponible pour le graphique.", font=("Helvetica", 14))
            no_data_label.pack()
            return
        
        # Créer le graphique
        categories = list(category_data.keys())
        amounts = list(category_data.values())
        
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Cercle parfait
        
        # Intégrer le graphique dans l'interface
        canvas = FigureCanvasTkAgg(fig, master=self.main_content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    
    def display_recent_transactions(self, user_id):
        """Affiche les transactions récentes de l'utilisateur."""
        accounts = self.db.get_user_accounts(user_id)
        for account in accounts:
            transactions = self.db.get_account_transactions(account['account_id'])
            for transaction in transactions[:5]:  # Affiche les 5 plus récentes
                transaction_info = f"{transaction['formatted_date']} - {transaction['description']}: {transaction['amount']}€"
                transaction_label = ctk.CTkLabel(self.main_content, text=transaction_info)
                transaction_label.pack()
    
    def show_deposit_screen(self, user_data):
        """Affiche l'interface pour déposer de l'argent."""
        self.clear_main_content()
        
        self.deposit_label = ctk.CTkLabel(self.main_content, text="Déposer de l'argent", font=("Helvetica", 20))
        self.deposit_label.pack(pady=20)
        
        self.amount_entry = ctk.CTkEntry(self.main_content, placeholder_text="Montant", width=350, height=50)
        self.amount_entry.pack(pady=10)
        
        self.account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.account_combobox.pack(pady=10)
        
        self.deposit_button = ctk.CTkButton(self.main_content, text="Déposer", command=lambda: self.deposit(user_data))
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
        
        self.withdraw_label = ctk.CTkLabel(self.main_content, text="Retirer de l'argent", font=("Helvetica", 20))
        self.withdraw_label.pack(pady=20)
        
        self.amount_entry = ctk.CTkEntry(self.main_content, placeholder_text="Montant", width=350, height=50)
        self.amount_entry.pack(pady=10)
        
        self.account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.account_combobox.pack(pady=10)
        
        self.withdraw_button = ctk.CTkButton(self.main_content, text="Retirer", command=lambda: self.withdraw(user_data))
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
        
        self.transfer_label = ctk.CTkLabel(self.main_content, text="Transférer de l'argent", font=("Helvetica", 20))
        self.transfer_label.pack(pady=20)
        
        self.amount_entry = ctk.CTkEntry(self.main_content, placeholder_text="Montant", width=350, height=50)
        self.amount_entry.pack(pady=10)
        
        self.from_account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.from_account_combobox.pack(pady=10)
        
        self.to_account_combobox = ctk.CTkComboBox(self.main_content, values=[acc['account_name'] for acc in self.db.get_user_accounts(user_data['user_id'])])
        self.to_account_combobox.pack(pady=10)
        
        self.transfer_button = ctk.CTkButton(self.main_content, text="Transférer", command=lambda: self.transfer(user_data))
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