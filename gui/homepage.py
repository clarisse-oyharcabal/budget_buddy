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
        self.geometry("1000x700")
        
        # Définition des couleurs et du style
        self.COLORS = {
            "background": "#DFD4C1",  # Fond principal clair
            "sidebar": "#07290B",     # Vert forêt pour la barre latérale
            "accent": "#4CAF50",      # Vert plus clair pour les éléments interactifs
            "highlight": "#81C784",   # Vert clair pour les survols
            "text_dark": "#263238",   # Texte foncé
            "text_light": "#FFFFFF",  # Texte clair
            "card": "#FFFFFF",        # Fond des cartes
            "chart": ["#2E7D32", "#4CAF50", "#81C784", "#A5D6A7", "#C8E6C9"]  # Palette pour graphiques
            
        }
        
        # Configuration du thème global
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        self.configure(fg_color=self.COLORS["background"])
        self.db = Database()
        self.load_images()
        self.user_data = user_data
        self.show_home_screen(self.user_data)
        
    def load_images(self):
        """Charge les images de fond et icônes."""
        self.images = {
            "background": ctk.CTkImage(Image.open("img/login_background.png"), size=(1000, 700)),
            "content_background": ctk.CTkImage(Image.open("img/background.png"), size=(1000, 700))
        }
    
    def show_home_screen(self, user_data):
        """Affiche la page d'accueil après connexion avec graphiques et transactions."""
        self.clear_screen()
        
        # Création de la structure principale
        # Barre latérale
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=self.COLORS["sidebar"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Logo ou titre de l'application
        self.app_title = ctk.CTkLabel(
            self.sidebar, 
            text="Zen Bank",
            font=("Helvetica", 22, "bold"),
            text_color=self.COLORS["text_light"]
        )
        self.app_title.pack(pady=(30, 20))
        
        # Séparateur
        self.separator = ctk.CTkFrame(self.sidebar, height=2, width=200, fg_color=self.COLORS["highlight"])
        self.separator.pack(pady=(0, 20))
        
        # Profil utilisateur
        self.profile_label = ctk.CTkLabel(
            self.sidebar, 
            text=f"{user_data['first_name']} {user_data['last_name']}", 
            font=("Helvetica", 16, "bold"),
            text_color=self.COLORS["text_light"]
        )
        self.profile_label.pack(pady=(0, 30))
        
        # Style commun pour tous les boutons
        button_style = {
            "corner_radius": 8,
            "font": ("Helvetica", 14),
            "text_color": self.COLORS["text_light"],
            "hover_color": self.COLORS["highlight"],
            "fg_color": "transparent",
            "anchor": "w",
            "width": 200,
            "height": 40
        }
        
        # Boutons de navigation
        self.home_button = ctk.CTkButton(
            self.sidebar, text="🏠 Accueil",
            command=lambda: self.show_home_content(user_data),
            **button_style
        )
        self.home_button.pack(pady=5)
        
        self.accounts_button = ctk.CTkButton(
            self.sidebar, text="💼 Comptes",
            command=lambda: self.show_accounts(user_data),
            **button_style
        )
        self.accounts_button.pack(pady=5)
        
        self.transactions_button = ctk.CTkButton(
            self.sidebar, text="📊 Transactions",
            command=lambda: self.show_transactions(user_data),
            **button_style
        )
        self.transactions_button.pack(pady=5)
        
        # Séparateur pour les opérations
        self.separator2 = ctk.CTkFrame(self.sidebar, height=1, width=200, fg_color=self.COLORS["highlight"])
        self.separator2.pack(pady=20)
        
        # Opérations (avec style légèrement différent)
        operation_button_style = button_style.copy()
        operation_button_style["fg_color"] = self.COLORS["accent"]
        
        self.deposit_button = ctk.CTkButton(
            self.sidebar, text="⬆️ Déposer",
            command=lambda: self.show_deposit_screen(user_data),
            **operation_button_style
        )
        self.deposit_button.pack(pady=5)
        
        self.withdraw_button = ctk.CTkButton(
            self.sidebar, text="⬇️ Retirer",
            command=lambda: self.show_withdraw_screen(user_data),
            **operation_button_style
        )
        self.withdraw_button.pack(pady=5)
        
        self.transfer_button = ctk.CTkButton(
            self.sidebar, text="↔️ Transférer",
            command=lambda: self.show_transfer_screen(user_data),
            **operation_button_style
        )
        self.transfer_button.pack(pady=5)
        
        # Déconnexion en bas de la sidebar
        self.logout_button = ctk.CTkButton(
            self.sidebar, text="🚪 Déconnexion",
            command=self.logout,
            fg_color="#E57373",
            hover_color="#EF5350",
            text_color=self.COLORS["text_light"],
            corner_radius=8,
            font=("Helvetica", 14),
            width=200
        )
        self.logout_button.pack(pady=(80, 20), side="bottom")
        
        # Contenu principal
        self.main_content = ctk.CTkFrame(
            self, 
            fg_color=self.COLORS["background"],
            corner_radius=0
        )
        self.main_content.pack(side="right", fill="both", expand=True)
        
        user_data['accounts'] = self.db.get_user_accounts(user_data['user_id'])

        # Afficher le contenu par défaut (Accueil)
        self.show_home_content(user_data)
    
    def show_home_content(self, user_data):
        """Affiche le contenu de la page d'accueil avec des cartes et des graphiques modernes."""
        self.clear_main_content()
        
        # Scroll container pour le contenu
        self.content_scroll = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color=self.COLORS["background"],
            corner_radius=0
        )
        self.content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # En-tête avec bienvenue et date
        header_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        welcome_text = ctk.CTkLabel(
            header_frame, 
            text=f"Bonjour, {user_data['first_name']} !",
            font=("Helvetica", 28, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        welcome_text.pack(side="left")
        
        # Rangée de résumé avec 3 cartes
        summary_row = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        summary_row.pack(fill="x", pady=10)
        
        # Récupération des données
        accounts = self.db.get_user_accounts(user_data['user_id'])
        total_balance = sum(account['balance'] for account in self.db.get_user_accounts(user_data['user_id']))
        
        # Fonction pour créer une carte de statistique
        def create_stat_card(parent, title, value, icon="", color=self.COLORS["accent"]):
            card = ctk.CTkFrame(parent, fg_color=self.COLORS["card"], corner_radius=10)
            card.pack(side="left", fill="x", expand=True, padx=10)
            
            card_title = ctk.CTkLabel(
                card, 
                text=f"{icon} {title}",
                font=("Helvetica", 14),
                text_color=self.COLORS["text_dark"]
            )
            card_title.pack(pady=(15, 5), padx=15, anchor="w")
            
            card_value = ctk.CTkLabel(
                card, 
                text=value,
                font=("Helvetica", 24, "bold"),
                text_color=color
            )
            card_value.pack(pady=(0, 15), padx=15, anchor="w")
            
            return card
        
        # Cartes de statistiques
        create_stat_card(summary_row, "Solde Total", f"{total_balance}€", "💰")
        
        # Essaie de récupérer les données de résumé mensuel
        monthly_summary = self.db.get_monthly_summary(user_data['user_id'])
        if monthly_summary and list(monthly_summary.keys()):
            latest_month = list(monthly_summary.keys())[0]
            income = monthly_summary[latest_month]['income']
            expenses = monthly_summary[latest_month]['expenses']
            
            create_stat_card(summary_row, f"Revenus ({latest_month})", f"{income}€", "📈", "#4CAF50")
            create_stat_card(summary_row, f"Dépenses ({latest_month})", f"{expenses}€", "📉", "#F44336")
        else:
            create_stat_card(summary_row, "Revenus (Mois)", "0€", "📈", "#4CAF50")
            create_stat_card(summary_row, "Dépenses (Mois)", "0€", "📉", "#F44336")
        
        # Rangée pour les graphiques et transactions
        data_row = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        data_row.pack(fill="x", pady=20)
        
        # Colonne de gauche pour le graphique
        chart_frame = ctk.CTkFrame(data_row, fg_color=self.COLORS["card"], corner_radius=10)
        chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        chart_title = ctk.CTkLabel(
            chart_frame, 
            text="Répartition des Dépenses",
            font=("Helvetica", 16, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        chart_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Graphique des dépenses
        self.display_expense_chart(user_data['user_id'], chart_frame)
        
        # Colonne de droite pour les transactions
        trans_frame = ctk.CTkFrame(data_row, fg_color=self.COLORS["card"], corner_radius=10)
        trans_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        trans_title = ctk.CTkLabel(
            trans_frame, 
            text="Transactions Récentes",
            font=("Helvetica", 16, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        trans_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Transactions récentes
        self.display_recent_transactions(user_data['user_id'], trans_frame)
        
        # Section pour les alertes
        alerts = self.db.get_alerts(user_data['user_id'])
        unread_alerts = [alert for alert in alerts if not alert['is_read']]
        
        if unread_alerts:
            alerts_frame = ctk.CTkFrame(self.content_scroll, fg_color=self.COLORS["card"], corner_radius=10)
            alerts_frame.pack(fill="x", pady=20)
            
            alerts_title = ctk.CTkLabel(
                alerts_frame, 
                text="⚠️ Alertes",
                font=("Helvetica", 16, "bold"),
                text_color="#FF9800"
            )
            alerts_title.pack(pady=(15, 10), padx=15, anchor="w")
            
            for alert in unread_alerts:
                alert_frame = ctk.CTkFrame(alerts_frame, fg_color="#FFF3E0", corner_radius=5)
                alert_frame.pack(fill="x", padx=15, pady=5)
                
                alert_text = ctk.CTkLabel(
                    alert_frame, 
                    text=f"{alert['message']}",
                    font=("Helvetica", 14),
                    text_color="#E65100"
                )
                alert_text.pack(pady=10, padx=10, anchor="w")
                
                alert_date = ctk.CTkLabel(
                    alert_frame, 
                    text=f"{alert['created_at']}",
                    font=("Helvetica", 12),
                    text_color="#9E9E9E"
                )
                alert_date.pack(pady=(0, 10), padx=10, anchor="e")
        
        # Section pour les paiements programmés
        has_scheduled_payments = False
        
        for account in accounts:
            scheduled_payments = self.db.get_scheduled_payments(account['account_id'])
            if scheduled_payments:
                has_scheduled_payments = True
                break
        
        if has_scheduled_payments:
            payments_frame = ctk.CTkFrame(self.content_scroll, fg_color=self.COLORS["card"], corner_radius=10)
            payments_frame.pack(fill="x", pady=20)
            
            payments_title = ctk.CTkLabel(
                payments_frame, 
                text="🔄 Paiements Programmés",
                font=("Helvetica", 16, "bold"),
                text_color=self.COLORS["text_dark"]
            )
            payments_title.pack(pady=(15, 10), padx=15, anchor="w")
            
            for account in accounts:
                scheduled_payments = self.db.get_scheduled_payments(account['account_id'])
                if scheduled_payments:
                    account_label = ctk.CTkLabel(
                        payments_frame, 
                        text=f"📁 {account['account_name']}",
                        font=("Helvetica", 14, "bold"),
                        text_color=self.COLORS["accent"]
                    )
                    account_label.pack(pady=(10, 5), padx=15, anchor="w")
                    
                    for payment in scheduled_payments:
                        payment_frame = ctk.CTkFrame(payments_frame, fg_color="#F1F8E9", corner_radius=5)
                        payment_frame.pack(fill="x", padx=15, pady=5)
                        
                        payment_desc = ctk.CTkLabel(
                            payment_frame, 
                            text=f"{payment['description']}",
                            font=("Helvetica", 14),
                            text_color=self.COLORS["text_dark"]
                        )
                        payment_desc.pack(pady=(10, 5), padx=10, anchor="w")
                        
                        payment_info = ctk.CTkLabel(
                            payment_frame, 
                            text=f"{payment['amount']}€ - Prochain: {payment['next_date']}",
                            font=("Helvetica", 12),
                            text_color="#757575"
                        )
                        payment_info.pack(pady=(0, 10), padx=10, anchor="w")
    
    def show_accounts(self, user_data):
        """Affiche les comptes de l'utilisateur."""
        self.clear_main_content()
        
        # Titre de la page
        title_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        page_title = ctk.CTkLabel(
            title_frame, 
            text="💼 Vos Comptes",
            font=("Helvetica", 28, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        page_title.pack(anchor="w")
        
        # Récupérer les comptes
        accounts = self.db.get_user_accounts(user_data['user_id'])
        
        if not accounts:
            no_accounts_frame = ctk.CTkFrame(self.main_content, fg_color=self.COLORS["card"], corner_radius=10)
            no_accounts_frame.pack(fill="x", padx=30, pady=20)
            
            no_accounts_label = ctk.CTkLabel(
                no_accounts_frame, 
                text="Aucun compte trouvé. Créez votre premier compte!",
                font=("Helvetica", 16),
                text_color=self.COLORS["text_dark"]
            )
            no_accounts_label.pack(pady=30)
            return
        
        # Afficher les comptes
        accounts_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        accounts_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        for i, account in enumerate(accounts):
            # Carte de compte avec ombrage et bordure
            account_card = ctk.CTkFrame(
                accounts_container, 
                fg_color=self.COLORS["card"], 
                corner_radius=10,
                border_width=1,
                border_color="#E0E0E0"
            )
            account_card.pack(fill="x", pady=10, ipady=15)
            
            # Zone supérieure avec nom et solde
            header_frame = ctk.CTkFrame(account_card, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            # Nom du compte
            account_name = ctk.CTkLabel(
                header_frame, 
                text=account['account_name'],
                font=("Helvetica", 20, "bold"),
                text_color=self.COLORS["accent"]
            )
            account_name.pack(side="left")
            
            # Solde
            account_balance = ctk.CTkLabel(
                header_frame, 
                text=f"{account['balance']}€",
                font=("Helvetica", 24, "bold"),
                text_color=self.COLORS["text_dark"]
            )
            account_balance.pack(side="right")
            
            # Ligne de séparation
            separator = ctk.CTkFrame(account_card, height=1, fg_color="#E0E0E0")
            separator.pack(fill="x", padx=20, pady=10)
            
            # Boutons d'action
            action_frame = ctk.CTkFrame(account_card, fg_color="transparent")
            action_frame.pack(fill="x", padx=20, pady=10)
            
            # Style des boutons d'action
            action_style = {
                "corner_radius": 6,
                "font": ("Helvetica", 12),
                "text_color": self.COLORS["text_light"],
                "width": 120,
                "height": 32
            }
            
            # Boutons d'opérations
            details_btn = ctk.CTkButton(
                action_frame, 
                text="Détails",
                fg_color="#78909C",
                hover_color="#607D8B",
                **action_style
            )
            details_btn.pack(side="left", padx=(0, 10))
            
            deposit_btn = ctk.CTkButton(
                action_frame, 
                text="Déposer",
                fg_color=self.COLORS["accent"],
                hover_color=self.COLORS["highlight"],
                command=lambda: self.show_deposit_screen(user_data),
                **action_style
            )
            deposit_btn.pack(side="left", padx=10)
            
            withdraw_btn = ctk.CTkButton(
                action_frame, 
                text="Retirer",
                fg_color="#FF7043",
                hover_color="#F4511E",
                command=lambda: self.show_withdraw_screen(user_data),
                **action_style
            )
            withdraw_btn.pack(side="left", padx=10)

    def show_transactions(self, user_data):
        """Affiche les transactions récentes avec des filtres intégrés."""
        self.clear_main_content()
        
        # Titre de la page
        title_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        page_title = ctk.CTkLabel(
            title_frame, 
            text="📊 Transactions",
            font=("Helvetica", 28, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        page_title.pack(anchor="w")
        
        # Panneau de filtres
        filter_panel = ctk.CTkFrame(self.main_content, fg_color=self.COLORS["card"], corner_radius=10)
        filter_panel.pack(fill="x", padx=30, pady=10)
        
        filter_title = ctk.CTkLabel(
            filter_panel, 
            text="Filtres",
            font=("Helvetica", 16, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        filter_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        # Grille pour les filtres
        filter_grid = ctk.CTkFrame(filter_panel, fg_color="transparent")
        filter_grid.pack(fill="x", padx=20, pady=10)
        
        # Ligne 1: Dates
        date_frame = ctk.CTkFrame(filter_grid, fg_color="transparent")
        date_frame.pack(fill="x", pady=5)
        
        date_label = ctk.CTkLabel(
            date_frame, 
            text="Période:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=80
        )
        date_label.pack(side="left", padx=(0, 10))
        
        self.start_date_entry = ctk.CTkEntry(
            date_frame, 
            placeholder_text="Date début (YYYY-MM-DD)",
            width=220,
            font=("Helvetica", 12),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.start_date_entry.pack(side="left", padx=10)
        
        self.end_date_entry = ctk.CTkEntry(
            date_frame, 
            placeholder_text="Date fin (YYYY-MM-DD)",
            width=220,
            font=("Helvetica", 12),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.end_date_entry.pack(side="left", padx=10)
        
        # Ligne 2: Catégorie et type
        category_frame = ctk.CTkFrame(filter_grid, fg_color="transparent")
        category_frame.pack(fill="x", pady=5)
        
        category_label = ctk.CTkLabel(
            category_frame, 
            text="Filtres:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=80
        )
        category_label.pack(side="left", padx=(0, 10))
        
        # Récupérer les catégories et types
        categories = [cat['category_name'] for cat in self.db.get_categories()]
        categories.insert(0, "Toutes catégories")
        
        types = [t['type_name'] for t in self.db.get_transaction_types()]
        types.insert(0, "Tous types")
        
        self.category_combobox = ctk.CTkComboBox(
            category_frame, 
            values=categories,
            width=220,
            font=("Helvetica", 12),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.category_combobox.pack(side="left", padx=10)
        self.category_combobox.set("Toutes catégories")
        
        self.type_combobox = ctk.CTkComboBox(
            category_frame, 
            values=types,
            width=220,
            font=("Helvetica", 12),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.type_combobox.pack(side="left", padx=10)
        self.type_combobox.set("Tous types")
        
        # Ligne 3: Tri et bouton
        sort_frame = ctk.CTkFrame(filter_grid, fg_color="transparent")
        sort_frame.pack(fill="x", pady=5)
        
        sort_label = ctk.CTkLabel(
            sort_frame, 
            text="Trier par:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=80
        )
        sort_label.pack(side="left", padx=(0, 10))
        
        self.sort_order_combobox = ctk.CTkComboBox(
            sort_frame, 
            values=["Date (récent)", "Date (ancien)", "Montant (croissant)", "Montant (décroissant)"],
            width=220,
            font=("Helvetica", 12),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.sort_order_combobox.pack(side="left", padx=10)
        self.sort_order_combobox.set("Date (récent)")
        
        self.apply_filters_button = ctk.CTkButton(
            sort_frame, 
            text="Appliquer les filtres",
            font=("Helvetica", 12, "bold"),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["highlight"],
            text_color=self.COLORS["text_light"],
            corner_radius=6,
            width=220,
            command=lambda: self.apply_transaction_filters(user_data)
        )
        self.apply_filters_button.pack(side="left", padx=10)
        
        # Conteneur pour les résultats des transactions
        self.transactions_container = ctk.CTkScrollableFrame(
            self.main_content, 
            fg_color=self.COLORS["background"],
            corner_radius=0
        )
        self.transactions_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Appliquer les filtres par défaut
        self.apply_transaction_filters(user_data)
    
    def apply_transaction_filters(self, user_data):
        """Applique les filtres et affiche les transactions correspondantes."""
        # Nettoyer le conteneur de transactions
        for widget in self.transactions_container.winfo_children():
            widget.destroy()
        
        # Construire les filtres
        filters = {}
        
        start_date = self.start_date_entry.get()
        if start_date:
            filters['start_date'] = start_date
        
        end_date = self.end_date_entry.get()
        if end_date:
            filters['end_date'] = end_date
        
        category = self.category_combobox.get()
        if category and category != "Toutes catégories":
            categories = {cat['category_name']: cat['category_id'] for cat in self.db.get_categories()}
            filters['category_id'] = categories[category]
        
        transaction_type = self.type_combobox.get()
        if transaction_type and transaction_type != "Tous types":
            types = {t['type_name']: t['type_id'] for t in self.db.get_transaction_types()}
            filters['type_id'] = types[transaction_type]
        
        sort_order = self.sort_order_combobox.get()
        if sort_order:
            if "Montant" in sort_order:
                filters['sort_by'] = 'amount'
                filters['sort_order'] = 'asc' if "croissant" in sort_order else 'desc'
            else:  # Date
                filters['sort_by'] = 'date'
                filters['sort_order'] = 'desc' if "récent" in sort_order else 'asc'
        
        # Récupérer les comptes et transactions
        accounts = self.db.get_user_accounts(user_data['user_id'])
        all_transactions = []
        
        for account in accounts:
            transactions = self.db.get_account_transactions(account['account_id'], filters)
            for transaction in transactions:
                transaction['account_name'] = account['account_name']
                all_transactions.append(transaction)
        
        # Trier toutes les transactions par date si nécessaire
        if filters.get('sort_by') == 'date':
            all_transactions.sort(
                key=lambda x: x['formatted_date'], 
                reverse=(filters.get('sort_order') == 'desc')
            )
        
        # Afficher les transactions filtrées
        if not all_transactions:
            no_trans_frame = ctk.CTkFrame(self.transactions_container, fg_color=self.COLORS["card"], corner_radius=10)
            no_trans_frame.pack(fill="x", pady=10)
            
            no_trans_label = ctk.CTkLabel(
                no_trans_frame, 
                text="Aucune transaction ne correspond à vos critères.",
                font=("Helvetica", 14),
                text_color=self.COLORS["text_dark"]
            )
            no_trans_label.pack(pady=20)
            return
        
        # Afficher les transactions
        for transaction in all_transactions:
            self.create_transaction_item(transaction)
    
    def create_transaction_item(self, transaction):
        # Couleurs selon le type de transaction
        if transaction['type_name'] == 'Dépôt':
            amount_color = "#4CAF50"  # Vert pour les dépôts
            amount_prefix = "+"
        elif transaction['type_name'] == 'Retrait':
            amount_color = "#F44336"  # Rouge pour les retraits
            amount_prefix = "-"
        else:  # Transfert
            amount_color = "#FF9800"  # Orange pour les transferts
            amount_prefix = "→" if transaction['amount'] > 0 else "←"
        
        # Création du cadre
        trans_card = ctk.CTkFrame(
            self.transactions_container,
            fg_color=self.COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0"
        )
        trans_card.pack(fill="x", pady=5, ipady=5)

        # Ligne principale (date, description, montant)
        main_frame = ctk.CTkFrame(trans_card, fg_color="transparent")
        main_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        date_label = ctk.CTkLabel(
            main_frame, 
            text=transaction['formatted_date'],
            font=("Helvetica", 12),
            text_color="#757575",
            width=100
        )
        date_label.pack(side="left")
        
        # Ajouter le type de transaction dans la description
        desc_text = f"[{transaction['type_name']}] {transaction['description']}"
        if transaction['type_name'] == 'Transfert' and transaction['to_account_id']:
            desc_text += f" → Compte {transaction['to_account_id']}"
        
        desc_label = ctk.CTkLabel(
            main_frame, 
            text=desc_text,
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS["text_dark"],
            anchor="w"
        )
        desc_label.pack(side="left", fill="x", expand=True, padx=10)
        
        amount_label = ctk.CTkLabel(
            main_frame, 
            text=f"{amount_prefix}{display_amount}€",
            font=("Helvetica", 14, "bold"),
            text_color=amount_color
        )
        amount_label.pack(side="right")
        
        # ... (le reste de la méthode reste inchangé) ...
        
        # Ligne de détails avec catégorie et compte
        details_frame = ctk.CTkFrame(trans_card, fg_color="transparent")
        details_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Afficher catégorie avec badge
        if 'category' in transaction and transaction['category']:
            category_badge = ctk.CTkFrame(
                details_frame, 
                fg_color="#E1F5FE",
                corner_radius=4
            )
            category_badge.pack(side="left")
            
            category_label = ctk.CTkLabel(
                category_badge, 
                text=f"📂 {transaction['category']}",
                font=("Helvetica", 12),
                text_color="#0277BD",
            )
            category_label.pack(pady=2, padx=8)
        
        # Afficher le compte
        account_badge = ctk.CTkFrame(
            details_frame, 
            fg_color="#F1F8E9",
            corner_radius=4
        )
        account_badge.pack(side="left", padx=(10, 0))
        
        account_label = ctk.CTkLabel(
            account_badge, 
            text=f"💼 {transaction['account_name']}",
            font=("Helvetica", 12),
            text_color="#558B2F",
        )
        account_label.pack(pady=2, padx=8)
    
    def show_deposit_screen(self, user_data):
        """Affiche l'écran pour effectuer un dépôt."""
        self.clear_main_content()
        
        # Titre de la page
        title_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        page_title = ctk.CTkLabel(
            title_frame, 
            text="Déposer de l'argent",
            font=("Helvetica", 28, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        page_title.pack(anchor="w")
        
        # Formulaire de dépôt
        form_card = ctk.CTkFrame(
            self.main_content, 
            fg_color=self.COLORS["card"],
            corner_radius=10
        )
        form_card.pack(fill="x", padx=30, pady=10)
        
        # Récupérer les comptes
        accounts = self.db.get_user_accounts(user_data['user_id'])
        account_names = [account['account_name'] for account in accounts]
        
        # Sélection du compte
        account_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        account_frame.pack(fill="x", padx=20, pady=15)
        
        account_label = ctk.CTkLabel(
            account_frame, 
            text="Compte:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        account_label.pack(side="left")
        
        self.account_deposit_combobox = ctk.CTkComboBox(
            account_frame,
            values=account_names,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.account_deposit_combobox.pack(side="left", padx=10)
        if account_names:
            self.account_deposit_combobox.set(account_names[0])
        
        # Montant
        amount_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        amount_frame.pack(fill="x", padx=20, pady=15)
        
        amount_label = ctk.CTkLabel(
            amount_frame, 
            text="Montant (€):",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        amount_label.pack(side="left")
        
        self.amount_deposit_entry = ctk.CTkEntry(
            amount_frame,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.amount_deposit_entry.pack(side="left", padx=10)
        
        # Description
        desc_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=15)
        
        desc_label = ctk.CTkLabel(
            desc_frame, 
            text="Description:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        desc_label.pack(side="left")
        
        self.desc_deposit_entry = ctk.CTkEntry(
            desc_frame,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6,
            placeholder_text="Salaire, remboursement, etc."
        )
        self.desc_deposit_entry.pack(side="left", padx=10)
        
        # Catégorie
        categories = self.db.get_categories()
        category_names = [cat['category_name'] for cat in categories]
        category_names = list(set(category_names))  # Supprimer les doublons

        category_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        category_frame.pack(fill="x", padx=20, pady=15)
        
        category_label = ctk.CTkLabel(
            category_frame, 
            text="Catégorie:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        category_label.pack(side="left")
        
        self.category_deposit_combobox = ctk.CTkComboBox(
            category_frame,
            values=category_names,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.category_deposit_combobox.pack(side="left", padx=10)
        if category_names:
            self.category_deposit_combobox.set(category_names[0])
        
        # Boutons
        buttons_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(15, 25))
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            font=("Helvetica", 14),
            fg_color="#E0E0E0",
            hover_color="#BDBDBD",
            text_color="#212121",
            corner_radius=8,
            width=150,
            command=lambda: self.show_home_content(user_data)
        )
        cancel_button.pack(side="left", padx=(110, 20))
        
        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Confirmer",
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["highlight"],
            text_color=self.COLORS["text_light"],
            corner_radius=8,
            width=150,
            command=lambda: self.process_deposit(user_data)
        )
        confirm_button.pack(side="left")
    
    def process_deposit(self, user_data):
        """Traite le dépôt d'argent sur un compte."""
        account_name = self.account_deposit_combobox.get()
        amount_str = self.amount_deposit_entry.get()
        description = self.desc_deposit_entry.get()
        category = self.category_deposit_combobox.get()
        
        # Vérifications
        if not account_name:
            self.show_error("Veuillez sélectionner un compte.")
            return
        
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                self.show_error("Le montant doit être supérieur à zéro.")
                return
        except:
            self.show_error("Veuillez entrer un montant valide.")
            return
        
        if not description:
            self.show_error("Veuillez ajouter une description.")
            return
        
        # Récupérer l'ID du compte
        accounts = self.db.get_user_accounts(user_data['user_id'])
        account_id = None
        for account in accounts:
            if account['account_name'] == account_name:
                account_id = account['account_id']
                break
        
        if account_id is None:
            self.show_error("Compte non trouvé.")
            return
        
        # Récupérer l'ID de catégorie
        categories = self.db.get_categories()
        category_id = None
        for cat in categories:
            if cat['category_name'] == category:
                category_id = cat['category_id']
                break
        
        # Effectuer le dépôt
        success = self.db.add_transaction(
            account_id, 
            amount, 
            description, 
            1,  # Type dépôt
            category_id
        )
        
        if success:
            self.show_success("Dépôt effectué avec succès!")
            self.show_home_content(user_data)
        else:
            self.show_error("Erreur lors du dépôt. Veuillez réessayer.")
    
    def process_withdraw(self, user_data):
        """Traite le retrait d'argent d'un compte."""
        account_name = self.account_withdraw_combobox.get()
        amount_str = self.amount_withdraw_entry.get()
        description = self.desc_withdraw_entry.get()
        category = self.category_withdraw_combobox.get()

        # Vérifications
        if not account_name:
            self.show_error("Veuillez sélectionner un compte.")
            return

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                self.show_error("Le montant doit être supérieur à zéro.")
                return
        except:
            self.show_error("Veuillez entrer un montant valide.")
            return

        if not description:
            self.show_error("Veuillez ajouter une description.")
            return

        # Récupérer l'ID du compte
        accounts = self.db.get_user_accounts(user_data['user_id'])
        account_id = None
        current_balance = Decimal('0.00')

        for account in accounts:
            if account['account_name'] == account_name:
                account_id = account['account_id']
                current_balance = Decimal(str(account['balance']))
                break

        if account_id is None:
            self.show_error("Compte non trouvé.")
            return

        # Récupérer l'ID de catégorie
        categories = self.db.get_categories()
        category_id = None
        for cat in categories:
            if cat['category_name'] == category:
                category_id = cat['category_id']
                break

        # Vérifier le solde suffisant
        if current_balance < amount:
            self.show_error("Fonds insuffisants pour effectuer ce retrait.")
            return

        # Effectuer le retrait
        success = self.db.add_transaction(
            account_id, 
            amount, 
            description, 
            2,  # Type retrait
            category_id
        )

        if success:
            self.show_success("Retrait effectué avec succès!")
            self.show_home_content(user_data)
        else:
            self.show_error("Erreur lors du retrait. Veuillez réessayer.")

    def process_transfer(self, user_data):

        """Traite complètement le transfert avec toutes les validations"""
        try:
            # Récupération des valeurs
            from_acc_name = self.from_account_combobox.get()
            to_acc_name = self.to_account_combobox.get()
            amount_str = self.amount_transfer_entry.get()
            description = self.desc_transfer_entry.get()

            # Validation des champs obligatoires
            if not from_acc_name or not to_acc_name:
                raise ValueError("Veuillez sélectionner les comptes source et destination")
            
            if from_acc_name == to_acc_name:
                raise ValueError("Les comptes source et destination doivent être différents")

            if not amount_str:
                raise ValueError("Veuillez saisir un montant")
            
            # Conversion et validation du montant
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Le montant doit être positif")
            except:
                raise ValueError("Montant invalide. Utilisez un nombre (ex: 125.50)")

            if not description:
                raise ValueError("Veuillez saisir une description")

            # Récupération des comptes
            accounts = self.db.get_user_accounts(user_data['user_id'])
            from_account = next((a for a in accounts if a['account_name'] == from_acc_name), None)
            
            if not from_account:
                raise ValueError("Compte source introuvable")

            # Vérification du solde
            if Decimal(str(from_account['balance'])) < amount:
                raise ValueError(f"Solde insuffisant (disponible: {from_account['balance']}€)")

            # CAS 1: Transfert vers compte externe
            if to_acc_name == "Compte externe":
                if not hasattr(self, 'iban_entry') or not self.iban_entry.get():
                    raise ValueError("Veuillez saisir l'IBAN du bénéficiaire")
                
                iban = self.iban_entry.get().strip().upper()
                if not self._validate_iban(iban):
                    raise ValueError("IBAN invalide. Format: FRXX XXXX...")

                # Enregistrement du transfert externe
                success, msg = self.db.add_external_transfer(
                    account_id=from_account['account_id'],
                    amount=amount,
                    beneficiary_name=to_acc_name,
                    iban=iban,
                    description=description
                )
                
                if not success:
                    raise Exception(msg)
                
                self.show_success(f"Transfert de {amount}€ vers compte externe programmé !")
            
            # CAS 2: Transfert interne
            else:
                to_account = next((a for a in accounts if a['account_name'] == to_acc_name), None)
                if not to_account:
                    raise ValueError("Compte destination introuvable")

                # Exécution des transactions
                success1, msg1 = self.db.add_transaction(
                    account_id=from_account['account_id'],
                    amount=-amount,
                    description=f"Vers {to_acc_name}: {description}",
                    transaction_type=3,
                    to_account_id=to_account['account_id']
                )
                
                success2, msg2 = self.db.add_transaction(
                    account_id=to_account['account_id'],
                    amount=amount,
                    description=f"De {from_acc_name}: {description}",
                    transaction_type=3,
                    to_account_id=from_account['account_id']
                )
                
                if not (success1 and success2):
                    raise Exception(msg1 if not success1 else msg2)
                
                self.show_success(f"Transfert de {amount}€ effectué avec succès !")
            
            # Retour à l'accueil après succès
            self.show_home_content(user_data)

        except ValueError as ve:
            self.show_error(str(ve))
        except Exception as e:
            self.show_error(f"Erreur lors du transfert: {str(e)}")

    def _validate_iban(self, iban):
        """Valide le format de l'IBAN"""
        iban = iban.replace(" ", "").upper()
        if len(iban) < 15 or len(iban) > 34:
            return False
        if not iban[:2].isalpha():  # Code pays
            return False
        if not iban[2:].isalnum():  # Le reste doit être alphanumérique
            return False
        return True

    def _handle_virtual_transfer(self, source_account, amount, description):
        """Gère les transferts vers un compte fictif (épargne virtuelle)"""
        success, msg = self.db.add_transaction(
            account_id=source_account['account_id'],
            amount=-amount,
            description=f"Épargne virtuelle: {description}",
            transaction_type=2  # Traité comme un retrait
        )
        
        if success:
            self.show_success(f"{amount}€ mis de côté dans l'épargne virtuelle !")
        else:
            self.show_error(msg)

    def _handle_virtual_deposit(self, target_account, amount, description):
        """Gère les dépôts depuis un compte fictif (rétrait d'épargne)"""
        success, msg = self.db.add_transaction(
            account_id=target_account['account_id'],
            amount=amount,
            description=f"Utilisation épargne: {description}",
            transaction_type=1  # Traité comme un dépôt
        )
    
        if success:
            self.show_success(f"{amount}€ récupérés de l'épargne virtuelle !")
        else:
            self.show_error(msg)

    def show_withdraw_screen(self, user_data):
        """Affiche l'écran pour effectuer un retrait."""
        self.clear_main_content()
        
        # Titre de la page
        title_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=30)
        
        page_title = ctk.CTkLabel(
            title_frame, 
            text="Retirer de l'argent",
            font=("Helvetica", 28, "bold"),
            text_color=self.COLORS["text_dark"]
        )
        page_title.pack(anchor="w")
        
        # Formulaire de retrait
        form_card = ctk.CTkFrame(
            self.main_content, 
            fg_color=self.COLORS["card"],
            corner_radius=10
        )
        form_card.pack(fill="x", padx=30, pady=10)
        
        # Récupérer les comptes
        accounts = self.db.get_user_accounts(user_data['user_id'])
        account_names = [account['account_name'] for account in accounts]
        
        # Sélection du compte
        account_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        account_frame.pack(fill="x", padx=20, pady=15)
        
        account_label = ctk.CTkLabel(
            account_frame, 
            text="Compte:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        account_label.pack(side="left")
        
        self.account_withdraw_combobox = ctk.CTkComboBox(
            account_frame,
            values=account_names,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.account_withdraw_combobox.pack(side="left", padx=10)
        if account_names:
            self.account_withdraw_combobox.set(account_names[0])
        
        # Montant
        amount_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        amount_frame.pack(fill="x", padx=20, pady=15)
        
        amount_label = ctk.CTkLabel(
            amount_frame, 
            text="Montant (€):",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        amount_label.pack(side="left")
        
        self.amount_withdraw_entry = ctk.CTkEntry(
            amount_frame,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.amount_withdraw_entry.pack(side="left", padx=10)
        
        # Description
        desc_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=15)
        
        desc_label = ctk.CTkLabel(
            desc_frame, 
            text="Description:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        desc_label.pack(side="left")
        
        self.desc_withdraw_entry = ctk.CTkEntry(
            desc_frame,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6,
            placeholder_text="Achat, facture, etc."
        )
        self.desc_withdraw_entry.pack(side="left", padx=10)
        
        # Catégorie (seulement les catégories de dépenses)
        categories = self.db.get_categories()
        # Filtrer pour ne garder que les catégories de dépenses (à adapter selon votre structure)
        expense_categories = [cat for cat in categories if cat['category_name'] not in ['Revenu']]
        category_names = [cat['category_name'] for cat in expense_categories]
        category_names = list(set(category_names))  # Supprimer les doublons
        
        category_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        category_frame.pack(fill="x", padx=20, pady=15)
        
        category_label = ctk.CTkLabel(
            category_frame, 
            text="Catégorie:",
            font=("Helvetica", 14),
            text_color=self.COLORS["text_dark"],
            width=100
        )
        category_label.pack(side="left")
        
        self.category_withdraw_combobox = ctk.CTkComboBox(
            category_frame,
            values=category_names,
            width=300,
            font=("Helvetica", 13),
            fg_color="#F5F5F5",
            text_color=self.COLORS["text_dark"],
            corner_radius=6
        )
        self.category_withdraw_combobox.pack(side="left", padx=10)
        if category_names:
            self.category_withdraw_combobox.set(category_names[0])
        
        # Boutons
        buttons_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(15, 25))
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            font=("Helvetica", 14),
            fg_color="#E0E0E0",
            hover_color="#BDBDBD",
            text_color="#212121",
            corner_radius=8,
            width=150,
            command=lambda: self.show_home_content(user_data)
        )
        cancel_button.pack(side="left", padx=(110, 20))
        
        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Confirmer",
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["highlight"],
            text_color=self.COLORS["text_light"],
            corner_radius=8,
            width=150,
            command=lambda: self.process_withdraw(user_data)
        )
        confirm_button.pack(side="left")

    def show_transfer_screen(self, user_data):
        """Affiche l'écran complet pour effectuer un transfert"""
        self.clear_main_content()
        
        # Frame principale
        main_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            title_frame, 
            text="Effectuer un Transfert",
            font=("Helvetica", 24, "bold")
        ).pack(anchor="w")

        # Carte du formulaire
        form_card = ctk.CTkFrame(
            main_frame,
            fg_color=self.COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color="#E0E0E0"
        )
        form_card.pack(fill="x", pady=10)

        # Compte source
        from_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        from_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            from_frame,
            text="Compte source:",
            font=("Helvetica", 14),
            width=120
        ).pack(side="left")
        
        accounts = self.db.get_user_accounts(user_data['user_id'])
        self.from_account_combobox = ctk.CTkComboBox(
            from_frame,
            values=[acc['account_name'] for acc in accounts],
            font=("Helvetica", 14),
            width=300,
            dropdown_font=("Helvetica", 12),
            state="readonly"
        )
        self.from_account_combobox.pack(side="left", padx=10)
        if accounts:
            self.from_account_combobox.set(accounts[0]['account_name'])

        # Compte destination
        to_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        to_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            to_frame,
            text="Compte destination:",
            font=("Helvetica", 14),
            width=120
        ).pack(side="left")
        
        self.to_account_combobox = ctk.CTkComboBox(
            to_frame,
            values=[acc['account_name'] for acc in accounts] + ["Compte externe"],
            font=("Helvetica", 14),
            width=300,
            dropdown_font=("Helvetica", 12),
            state="readonly",
            command=self._toggle_external_fields
        )
        self.to_account_combobox.pack(side="left", padx=10)
        if len(accounts) > 1:
            self.to_account_combobox.set(accounts[1]['account_name'])

        # Montant
        amount_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        amount_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            amount_frame,
            text="Montant (€):",
            font=("Helvetica", 14),
            width=120
        ).pack(side="left")
        
        self.amount_transfer_entry = ctk.CTkEntry(
            amount_frame,
            font=("Helvetica", 14),
            width=300,
            placeholder_text="00.00"
        )
        self.amount_transfer_entry.pack(side="left", padx=10)

        # Description
        desc_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            desc_frame,
            text="Description:",
            font=("Helvetica", 14),
            width=120
        ).pack(side="left")
        
        self.desc_transfer_entry = ctk.CTkEntry(
            desc_frame,
            font=("Helvetica", 14),
            width=300,
            placeholder_text="Motif du transfert"
        )
        self.desc_transfer_entry.pack(side="left", padx=10)

        # Boutons
        buttons_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            font=("Helvetica", 14),
            width=120,
            height=40,
            fg_color="#E0E0E0",
            text_color="#000000",
            command=lambda: self.show_home_content(user_data)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Confirmer",
            font=("Helvetica", 14, "bold"),
            width=120,
            height=40,
            fg_color=self.COLORS["accent"],
            command=lambda: self.process_transfer(user_data)
        ).pack(side="left", padx=10)

    def _toggle_external_fields(self, event=None):
        """Affiche/masque dynamiquement les champs pour compte externe"""
        # Suppression sécurisée des champs existants
        if hasattr(self, 'external_fields_frame'):
            if hasattr(self, 'iban_entry'):
                self.iban_entry.destroy()
                del self.iban_entry
            self.external_fields_frame.destroy()
            del self.external_fields_frame
            
        # Affichage si compte externe sélectionné
        if self.to_account_combobox.get() == "Compte externe":
            self.external_fields_frame = ctk.CTkFrame(
                self.main_content,
                fg_color="transparent"
            )
            self.external_fields_frame.pack(fill="x", padx=30, pady=(0, 20))
            
            # Frame pour l'IBAN
            iban_frame = ctk.CTkFrame(
                self.external_fields_frame,
                fg_color="transparent"
            )
            iban_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                iban_frame,
                text="IBAN du bénéficiaire:",
                font=("Helvetica", 14),
                width=150
            ).pack(side="left")
            
            self.iban_entry = ctk.CTkEntry(
                iban_frame,
                font=("Helvetica", 14),
                width=300,
                placeholder_text="FR76 3000 1000 0100..."
            )
            self.iban_entry.pack(side="left", padx=10)

        def validate_accounts():
            from_acc = self.from_account_combobox.get()
            to_acc = self.to_account_combobox.get()
            if from_acc and to_acc and from_acc == to_acc:
                self.show_error("Les comptes doivent être différents", temporary=True)
                confirm_button.configure(state="disabled")
            else:
                confirm_button.configure(state="normal")

        self.from_account_combobox.configure(command=lambda _: validate_accounts())
        self.to_account_combobox.configure(command=lambda _: validate_accounts())

    def display_expense_chart(self, user_id, parent_frame):
        """Affiche un graphique circulaire des dépenses par catégorie."""
        # Récupérer les données de dépenses par catégorie
        expense_data = self.db.get_expenses_by_category(user_id)
        
        if not expense_data:
            no_data_label = ctk.CTkLabel(
                parent_frame,
                text="Pas assez de données pour afficher un graphique.",
                font=("Helvetica", 14),
                text_color="#757575"
            )
            no_data_label.pack(pady=50)
            return
        
        # Créer le graphique circulaire
        figure, ax = plt.subplots(figsize=(5, 4))
        figure.patch.set_facecolor(self.COLORS["card"])
        
        categories = [item['category'] for item in expense_data]
        amounts = [abs(item['amount']) for item in expense_data]
        colors = self.COLORS["chart"][:len(expense_data)]
        
        wedges, texts, autotexts = ax.pie(
            amounts, 
            labels=None, 
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        # Améliorer l'apparence du graphique
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
        
        ax.axis('equal')
        ax.set_facecolor(self.COLORS["card"])
        
        # Ajouter une légende
        ax.legend(
            wedges, 
            categories,
            loc="center left",
            bbox_to_anchor=(0.9, 0.5),
            fontsize=9
        )
        
        # Intégrer le graphique dans l'interface Tkinter
        canvas = FigureCanvasTkAgg(figure, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
    
    def display_recent_transactions(self, user_id, parent_frame):
        """Affiche les transactions récentes dans un cadre donné."""
        # Récupérer les comptes et les transactions récentes
        accounts = self.db.get_user_accounts(user_id)
        all_transactions = []
        
        for account in accounts:
            transactions = self.db.get_account_transactions(account['account_id'], {'limit': 5})
            for transaction in transactions:
                transaction['account_name'] = account['account_name']
                all_transactions.append(transaction)
        
        # Trier par date (plus récent d'abord)
        all_transactions.sort(key=lambda x: x['formatted_date'], reverse=True)
        
        if not all_transactions:
            no_trans_label = ctk.CTkLabel(
                parent_frame,
                text="Aucune transaction récente.",
                font=("Helvetica", 14),
                text_color="#757575"
            )
            no_trans_label.pack(pady=50)
            return
        
        # Limiter à 5 transactions
        shown_transactions = all_transactions[:5]
        
        for transaction in shown_transactions:
            trans_frame = ctk.CTkFrame(
                parent_frame, 
                fg_color="#F5F5F5", 
                corner_radius=6
            )
            trans_frame.pack(fill="x", padx=15, pady=5)
            
            # Déterminer la couleur selon le type
            if transaction['type_name'] == 'Retrait':  # Vérifie si c'est une dépense
               amount_color = "#F44336"  # Rouge pour les retraits
               amount_prefix = "-"  # Signe négatif pour les dépenses
            else:
                amount_color = "#4CAF50"  # Vert pour les revenus
                amount_prefix = "+"  # Signe positif pour les revenus
            
            
            # Ligne principale avec date et description
            main_line = ctk.CTkFrame(trans_frame, fg_color="transparent")
            main_line.pack(fill="x", padx=10, pady=(8, 4))
            
            date_label = ctk.CTkLabel(
                main_line, 
                text=transaction['formatted_date'],
                font=("Helvetica", 11),
                text_color="#757575",
                width=90
            )
            date_label.pack(side="left")
            
            desc_label = ctk.CTkLabel(
                main_line, 
                text=transaction['description'],
                font=("Helvetica", 12, "bold"),
                text_color=self.COLORS["text_dark"],
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True)
            
            # Seconde ligne avec compte et montant
            details_line = ctk.CTkFrame(trans_frame, fg_color="transparent")
            details_line.pack(fill="x", padx=10, pady=(0, 8))
            
            account_label = ctk.CTkLabel(
                details_line, 
                text=f"💼 {transaction['account_name']}",
                font=("Helvetica", 11),
                text_color="#558B2F",
            )
            account_label.pack(side="left", padx=(90, 0))
            
            amount_label = ctk.CTkLabel(
                details_line, 
                text=f"{amount_prefix}{transaction['amount']}€",
                font=("Helvetica", 12, "bold"),
                text_color=amount_color
            )
            amount_label.pack(side="right")
    
    def show_success(self, message):
        """Affiche un message de succès."""
        # Créer une fenêtre modale pour le message
        modal = ctk.CTkToplevel(self)
        modal.title("Succès")
        modal.geometry("300x150")
        modal.resizable(False, False)
        
        # Centrer la fenêtre
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() - modal.winfo_width()) // 2
        y = (modal.winfo_screenheight() - modal.winfo_height()) // 2
        modal.geometry(f"+{x}+{y}")
        
        # Contenu
        frame = ctk.CTkFrame(modal, fg_color="#E8F5E9")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        icon_label = ctk.CTkLabel(
            frame, 
            text="✅",
            font=("Helvetica", 32),
            text_color="#2E7D32"
        )
        icon_label.pack(pady=(10, 5))
        
        message_label = ctk.CTkLabel(
            frame, 
            text=message,
            font=("Helvetica", 14),
            text_color="#2E7D32"
        )
        message_label.pack(pady=5)
        
        # Bouton de fermeture
        close_button = ctk.CTkButton(
            frame,
            text="Fermer",
            font=("Helvetica", 12),
            fg_color="#4CAF50",
            hover_color="#2E7D32",
            text_color="white",
            corner_radius=6,
            command=modal.destroy
        )
        close_button.pack(pady=10)
        
        # Rendre modale
        modal.transient(self)
        modal.grab_set()
        self.wait_window(modal)
    
    def show_error(self, message):
        """Affiche un message d'erreur."""
        # Similaire à show_success mais avec des couleurs différentes
        modal = ctk.CTkToplevel(self)
        modal.title("Erreur")
        modal.geometry("300x150")
        modal.resizable(False, False)
        
        # Centrer la fenêtre
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() - modal.winfo_width()) // 2
        y = (modal.winfo_screenheight() - modal.winfo_height()) // 2
        modal.geometry(f"+{x}+{y}")
        
        # Contenu
        frame = ctk.CTkFrame(modal, fg_color="#FFEBEE")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        icon_label = ctk.CTkLabel(
            frame, 
            text="❌",
            font=("Helvetica", 32),
            text_color="#C62828"
        )
        icon_label.pack(pady=(10, 5))
        
        message_label = ctk.CTkLabel(
            frame, 
            text=message,
            font=("Helvetica", 14),
            text_color="#C62828"
        )
        message_label.pack(pady=5)
        
        # Bouton de fermeture
        close_button = ctk.CTkButton(
            frame,
            text="Fermer",
            font=("Helvetica", 12),
            fg_color="#F44336",
            hover_color="#C62828",
            text_color="white",
            corner_radius=6,
            command=modal.destroy
        )
        close_button.pack(pady=10)
        
        # Rendre modale
        modal.transient(self)
        modal.grab_set()
        self.wait_window(modal)
    
    def clear_screen(self):
        """Nettoie tous les widgets de l'écran principal."""
        for widget in self.winfo_children():
            widget.destroy()
    
    def clear_main_content(self):
        """Nettoie uniquement le contenu principal sans affecter la barre latérale."""
        if hasattr(self, 'main_content'):
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def logout(self):
        """Ferme la page d'accueil et retourne à l'écran de connexion."""
        self.destroy()  # Ferme la fenêtre actuelle
        from gui.login import LoginApp
        login_app = LoginApp()  # Ouvre la fenêtre de login
        login_app.mainloop()

if __name__ == "__main__":
    fake_user = {"first_name": "Test", "last_name": "User"}  # Simuler un utilisateur
    app = HomePageApp(fake_user)
    app.mainloop()