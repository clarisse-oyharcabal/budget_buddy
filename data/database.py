import mysql.connector
import hashlib
import secrets
import datetime
import os
from decimal import Decimal


class Database:
    def __init__(self):
        """
        Initialize the database connection.
        """
        self._create_tables_if_not_exists()
        
    def _get_connection(self):
        """
        Create and return a database connection.
        
        Returns:
            tuple: (connection, cursor)
        """
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="budget"
        )
        cursor = conn.cursor(dictionary=True)  # This enables column access by name
        return conn, cursor
    
    def _create_tables_if_not_exists(self):
        """Create the database tables if they don't already exist."""
        conn, cursor = self._get_connection()
        
        try:
            # Table des utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des comptes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    account_name VARCHAR(100) NOT NULL,
                    balance DECIMAL(15, 2) DEFAULT 0.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Table des catégories de transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    category_name VARCHAR(50) NOT NULL,
                    description TEXT
                )
            """)
            
            # Insérer quelques catégories par défaut
            cursor.execute("""
                INSERT IGNORE INTO categories (category_name, description) VALUES
                    ('Loisir', 'Depenses liees aux activités de loisir'),
                    ('Repas', 'Depenses alimentaires'),
                    ('Transport', 'Depenses liees aux déplacements'),
                    ('Logement', 'Depenses liees au logement'),
                    ('Sante', 'Depenses medicales'),
                    ('Vetements', 'Achats de vetements'),
                    ('Education', 'Frais de scolarite et materiel educatif'),
                    ('Revenu', 'Sources de revenu'),
                    ('Pot-de-vin', 'Cadeaux et pourboires'),
                    ('Autre', 'Autres depenses')
            """)
            
            # Table des types de transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_types (
                    type_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    type_name VARCHAR(50) NOT NULL
                )
            """)
            
            # Insérer les types de transactions
            cursor.execute("""
                INSERT IGNORE INTO transaction_types (type_name) VALUES
                    ('Dépôt'),
                    ('Retrait'),
                    ('Transfert')
            """)
            
            # Table des transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    reference VARCHAR(50) NOT NULL,
                    description TEXT,
                    amount DECIMAL(15, 2) NOT NULL,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    account_id INTEGER NOT NULL,
                    category_id INTEGER,
                    type_id INTEGER NOT NULL,
                    to_account_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
                    FOREIGN KEY (category_id) REFERENCES categories(category_id),
                    FOREIGN KEY (type_id) REFERENCES transaction_types(type_id),
                    FOREIGN KEY (to_account_id) REFERENCES accounts(account_id)
                )
            """)
            
            # Table des paiements programmés
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_payments (
                    payment_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    account_id INTEGER NOT NULL,
                    reference VARCHAR(50) NOT NULL,
                    description TEXT,
                    amount DECIMAL(15, 2) NOT NULL,
                    category_id INTEGER,
                    frequency ENUM('monthly', 'weekly', 'yearly') NOT NULL,
                    next_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )
            """)
            
            # Table des alertes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    account_id INTEGER,
                    alert_type VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
                )
            """)
            
            conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()
    
    def _hash_password(self, password, salt=None):
        """
        Hash a password with a salt using PBKDF2 with SHA-256.
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key.hex(), salt.hex()
    
    def _verify_password(self, stored_hash, stored_salt, provided_password):
        """
        Verify a password against a stored hash and salt.
        """
        salt = bytes.fromhex(stored_salt)
        computed_hash, _ = self._hash_password(provided_password, salt)
        return stored_hash == computed_hash
    
    def validate_password_strength(self, password):
        """
        Validate password strength.
        """
        if len(password) < 10:
            return False, "Le mot de passe doit contenir au moins 10 caractères."
        if not any(c.isupper() for c in password):
            return False, "Le mot de passe doit contenir au moins une majuscule."
        if not any(c.islower() for c in password):
            return False, "Le mot de passe doit contenir au moins une minuscule."
        if not any(c.isdigit() for c in password):
            return False, "Le mot de passe doit contenir au moins un chiffre."
        if not any(not c.isalnum() for c in password):
            return False, "Le mot de passe doit contenir au moins un caractère spécial."
        return True, "Mot de passe valide."
    
    def register_user(self, first_name, last_name, email, password):
        """
        Register a new user.
        """
        is_valid, message = self.validate_password_strength(password)
        if not is_valid:
            return False, message, None
        
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "Cette adresse email est déjà utilisée.", None
            
            hashed_password, salt = self._hash_password(password)
            password_storage = f"{hashed_password}:{salt}"
            
            cursor.execute(
                """
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (%s, %s, %s, %s)
                """,
                (first_name, last_name, email, password_storage)
            )
            
            user_id = cursor.lastrowid
            
            cursor.execute(
                """
                INSERT INTO accounts (user_id, account_name)
                VALUES (%s, %s)
                """,
                (user_id, "Compte principal")
            )
            
            conn.commit()
            conn.close()
            
            return True, "Utilisateur enregistré avec succès.", user_id
            
        except Exception as e:
            return False, f"Erreur lors de l'enregistrement: {e}", None
    
    def login_user(self, email, password):
        """
        Authenticate a user.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute(
                """
                SELECT user_id, first_name, last_name, email, password
                FROM users
                WHERE email = %s
                """,
                (email,)
            )
            
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "Email ou mot de passe incorrect.", None
            
            stored_password = user['password']
            parts = stored_password.split(':')
            
            if len(parts) != 2:
                conn.close()
                return False, "Erreur de format de mot de passe stocké.", None
            
            stored_hash, stored_salt = parts
            
            if not self._verify_password(stored_hash, stored_salt, password):
                conn.close()
                return False, "Email ou mot de passe incorrect.", None
            
            user_data = {
                'user_id': user['user_id'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email']
            }
            
            conn.close()
            return True, "Connexion réussie.", user_data
            
        except Exception as e:
            return False, f"Erreur lors de la connexion: {e}", None
    
    def get_user_accounts(self, user_id):
        """
        Get all accounts for a user.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute(
                """
                SELECT account_id, account_name, balance
                FROM accounts
                WHERE user_id = %s
                """,
                (user_id,)
            )
            
            accounts = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return accounts
            
        except Exception as e:
            print(f"Error getting user accounts: {e}")
            return []
    
    def get_account_transactions(self, account_id, filters=None):
        """
        Get transactions for an account with optional filtering.
        """
        try:
            conn, cursor = self._get_connection()
            
            query = """
                SELECT t.transaction_id, t.reference, t.description, t.amount, 
                    t.transaction_date, t.account_id, t.to_account_id,
                    c.category_name, tt.type_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.category_id
                LEFT JOIN transaction_types tt ON t.type_id = tt.type_id
                WHERE t.account_id = %s
            """
            
            params = [account_id]
            
            if filters:
                if 'start_date' in filters:
                    query += " AND t.transaction_date >= %s"
                    params.append(filters['start_date'])
                
                if 'end_date' in filters:
                    query += " AND t.transaction_date <= %s"
                    params.append(filters['end_date'])
                
                if 'category_id' in filters:
                    query += " AND t.category_id = %s"
                    params.append(filters['category_id'])
                
                if 'type_id' in filters:
                    query += " AND t.type_id = %s"
                    params.append(filters['type_id'])
            
            if filters and 'sort_by' in filters:
                sort_field = filters['sort_by']
                sort_order = filters.get('sort_order', 'asc').upper()
                
                if sort_order not in ('ASC', 'DESC'):
                    sort_order = 'ASC'
                
                valid_fields = {
                    'amount': 't.amount',
                    'date': 't.transaction_date',
                    'type': 'tt.type_name',
                    'category': 'c.category_name'
                }
                
                if sort_field in valid_fields:
                    query += f" ORDER BY {valid_fields[sort_field]} {sort_order}"
                else:
                    query += " ORDER BY t.transaction_date DESC"
            else:
                query += " ORDER BY t.transaction_date DESC"

            # Ajout de la limite si spécifiée
            if filters and 'limit' in filters:
                query += " LIMIT %s"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            
            transactions = []
            for row in cursor.fetchall():
                transaction = dict(row)
                
                # Formater la date pour l'affichage
                if 'transaction_date' in transaction and transaction['transaction_date']:
                    if isinstance(transaction['transaction_date'], str):  # Vérifier si c'est une chaîne
                        date_obj = datetime.datetime.fromisoformat(transaction['transaction_date'])
                    else:  # Si c'est déjà un objet datetime
                        date_obj = transaction['transaction_date']
                    transaction['formatted_date'] = date_obj.strftime('%d/%m/%Y %H:%M')
                
                transactions.append(transaction)
            
            conn.close()
            return transactions
            
        except Exception as e:
            print(f"Error getting account transactions: {e}")
            return []
    
    def get_categories(self):
        """
        Get all transaction categories.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute("SELECT category_id, category_name FROM categories")
            
            categories = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_transaction_types(self):
        """
        Get all transaction types.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute("SELECT type_id, type_name FROM transaction_types")
            
            types = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return types
            
        except Exception as e:
            print(f"Error getting transaction types: {e}")
            return []
    
    def add_transaction(self, account_id, amount, description,  transaction_type, category_id=None, to_account_id=None, reference=None):
        """
        Add a new transaction.
        """
        try:
            conn, cursor = self._get_connection()

            # Générer une référence si non fournie
            if reference is None:
               reference = f"TRX-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
            
            cursor.execute("START TRANSACTION")
            
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            account = cursor.fetchone()
            
            if not account:
                conn.close()
                return False, "Compte introuvable."
            
            current_balance = Decimal(str(account['balance']))  # Convertir en Decimal
            amount = Decimal(str(amount))  # Convertir le montant en Decimal
            
            if transaction_type == 3 and not to_account_id:
                conn.rollback()
                conn.close()
                return False, "Compte de destination requis pour un transfert."
            
            if transaction_type == 3:
                cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (to_account_id,))
                if not cursor.fetchone():
                    conn.rollback()
                    conn.close()
                    return False, "Compte de destination introuvable."
            
            if transaction_type == 1:  # Dépôt
                new_balance = current_balance + amount
                cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (str(new_balance), account_id))  # Convertir en chaîne pour MySQL
                
            elif transaction_type == 2:  # Retrait
                if current_balance < amount:
                    conn.rollback()
                    conn.close()
                    return False, "Solde insuffisant pour effectuer ce retrait."
                
                new_balance = current_balance - amount
                cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (str(new_balance), account_id))  # Convertir en chaîne pour MySQL
                
                if new_balance < 0:
                    cursor.execute("SELECT user_id FROM accounts WHERE account_id = %s", (account_id,))
                    user_id = cursor.fetchone()['user_id']
                    
                    cursor.execute(
                        """
                        INSERT INTO alerts (user_id, account_id, alert_type, message)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (user_id, account_id, "overdraft", f"Attention: votre compte est à découvert ({new_balance:.2f} €)")
                    )
                
            elif transaction_type == 3:  # Transfert
                if current_balance < amount:
                    conn.rollback()
                    conn.close()
                    return False, "Solde insuffisant pour effectuer ce transfert."
                
                new_source_balance = current_balance - amount
                cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (str(new_source_balance), account_id))  # Convertir en chaîne pour MySQL
                
                cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (to_account_id,))
                dest_account = cursor.fetchone()
                new_dest_balance = Decimal(str(dest_account['balance'])) + amount
                cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s", (str(new_dest_balance), to_account_id))  # Convertir en chaîne pour MySQL
                
                if new_source_balance < 0:
                    cursor.execute("SELECT user_id FROM accounts WHERE account_id = %s", (account_id,))
                    user_id = cursor.fetchone()['user_id']
                    
                    cursor.execute(
                        """
                        INSERT INTO alerts (user_id, account_id, alert_type, message)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (user_id, account_id, "overdraft", f"Attention: votre compte est à découvert ({new_source_balance:.2f} €)")
                    )
            
            cursor.execute(
                """
                INSERT INTO transactions (reference, description, amount, account_id, category_id, type_id, to_account_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (reference, description, str(amount), account_id, category_id, transaction_type, to_account_id)  # Convertir en chaîne pour MySQL
            )
            
            conn.commit()
            conn.close()
            
            return True, "Transaction effectuée avec succès."
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"Erreur lors de la transaction: {e}"
    
    def get_account_balance(self, account_id):
        """
        Récupère le solde actuel d'un compte
        """
        try:
            conn, cursor = self._get_connection()
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return Decimal(str(result['balance']))
            return Decimal('0.00')
        except Exception as e:
            print(f"Error getting account balance: {e}")
            return Decimal('0.00')

    def get_monthly_summary(self, user_id):
        """
        Get monthly summary of income and expenses for a user.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
            accounts = cursor.fetchall()
            
            if not accounts:
                conn.close()
                return {}
            
            account_ids = [account['account_id'] for account in accounts]
            account_ids_str = ','.join('%s' for _ in account_ids)
            
            query = f"""
                SELECT 
                    DATE_FORMAT(transaction_date, '%Y-%m') as month,
                    SUM(CASE WHEN type_id = 1 THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN type_id = 2 THEN amount ELSE 0 END) as expenses
                FROM transactions
                WHERE account_id IN ({account_ids_str})
                    AND transaction_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
                ORDER BY month
            """
            
            cursor.execute(query, account_ids)
            
            monthly_data = {}
            for row in cursor.fetchall():
                monthly_data[row['month']] = {
                    'income': row['income'],
                    'expenses': row['expenses'],
                    'net': row['income'] - row['expenses']
                }
            
            conn.close()
            return monthly_data
            
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return {}
    
    def get_category_summary(self, user_id):
        """
        Get expense summary by category for a user.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
            accounts = cursor.fetchall()
            
            if not accounts:
                conn.close()
                return {}
            
            account_ids = [account['account_id'] for account in accounts]
            account_ids_str = ','.join('%s' for _ in account_ids)
            
            query = f"""
                SELECT 
                    c.category_name,
                    SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE t.account_id IN ({account_ids_str})
                    AND t.type_id = 2
                    AND DATE_FORMAT(t.transaction_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
                GROUP BY c.category_name
                ORDER BY total DESC
            """
            
            cursor.execute(query, account_ids)
            
            category_data = {}
            for row in cursor.fetchall():
                category_data[row['category_name']] = row['total']
            
            conn.close()
            return category_data
            
        except Exception as e:
            print(f"Error getting category summary: {e}")
            return {}
    
    def add_external_transfer(self, account_id, amount, beneficiary, iban, description):
        """Enregistre un transfert externe"""
        try:
            conn, cursor = self._get_connection()
            
            # 1. Débit du compte
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", 
                        (amount, account_id))
            
            # 2. Enregistrement spécial
            cursor.execute("""
                INSERT INTO external_transfers 
                (account_id, amount, beneficiary, iban, description, status)
                VALUES (%s, %s, %s, %s, %s, 'PENDING')
            """, (account_id, amount, beneficiary, iban, description))
            
            conn.commit()
            return True, "Transfert programmé"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
    
    def get_alerts(self, user_id):
        """
        Get alerts for a user.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute(
                """
                SELECT a.alert_id, a.alert_type, a.message, a.is_read, a.created_at,
                       acc.account_name
                FROM alerts a
                LEFT JOIN accounts acc ON a.account_id = acc.account_id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
                """,
                (user_id,)
            )
            
            alerts = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return alerts
            
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    def mark_alert_as_read(self, alert_id):
        """
        Mark an alert as read.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute(
                "UPDATE alerts SET is_read = 1 WHERE alert_id = %s",
                (alert_id,)
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error marking alert as read: {e}")
            return False
    
    def get_scheduled_payments(self, account_id):
        """
        Get scheduled payments for an account.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute(
                """
                SELECT sp.payment_id, sp.reference, sp.description, sp.amount, 
                       sp.frequency, sp.next_date, c.category_name
                FROM scheduled_payments sp
                LEFT JOIN categories c ON sp.category_id = c.category_id
                WHERE sp.account_id = %s
                ORDER BY sp.next_date
                """,
                (account_id,)
            )
            
            payments = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return payments
            
        except Exception as e:
            print(f"Error getting scheduled payments: {e}")
            return []
    
    def create_scheduled_payment(self, account_id, reference, description, amount, category_id, frequency, next_date):
        """
        Create a scheduled payment.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute(
                """
                INSERT INTO scheduled_payments 
                (account_id, reference, description, amount, category_id, frequency, next_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (account_id, reference, description, amount, category_id, frequency, next_date)
            )
            
            conn.commit()
            conn.close()
            
            return True, "Paiement programmé créé avec succès."
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"Erreur lors de la création du paiement programmé: {e}"
        
    def get_expenses_by_category(self, user_id):
        """
        Récupère le total des dépenses par catégorie pour un utilisateur donné.
        """
        try:
            conn, cursor = self._get_connection()
            
            query = """
                SELECT c.category_name, SUM(t.amount) AS total
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                JOIN categories c ON t.category_id = c.category_id
                WHERE a.user_id = %s
                AND t.type_id IN (2, 3)  # 2 = Retrait, 3 = Transfert
                GROUP BY c.category_name
                ORDER BY total DESC
            """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            
            expenses = [{"category": row["category_name"], "amount": row["total"]} for row in result] if result else []
            
            conn.close()
            return expenses
        
        except Exception as e:
            print(f"Erreur lors de la récupération des dépenses par catégorie: {e}")
            return []

    def process_due_scheduled_payments(self):
        """
        Process all due scheduled payments.
        """
        try:
            conn, cursor = self._get_connection()
            
            cursor.execute("START TRANSACTION")
            
            cursor.execute(
                """
                SELECT payment_id, account_id, reference, description, amount, category_id, frequency, next_date
                FROM scheduled_payments
                WHERE next_date <= CURDATE()
                """
            )
            
            due_payments = [dict(row) for row in cursor.fetchall()]
            processed_count = 0
            
            for payment in due_payments:
                result = self.add_transaction(
                    payment['account_id'],
                    payment['reference'],
                    payment['description'],
                    payment['amount'],
                    2,  # Retrait (expense)
                    payment['category_id']
                )
                
                if result[0]:
                    current_date = datetime.datetime.fromisoformat(payment['next_date'])
                    
                    if payment['frequency'] == 'monthly':
                        next_date = (current_date + datetime.timedelta(days=30)).date().isoformat()
                    elif payment['frequency'] == 'weekly':
                        next_date = (current_date + datetime.timedelta(days=7)).date().isoformat()
                    elif payment['frequency'] == 'yearly':
                        next_date = (current_date + datetime.timedelta(days=365)).date().isoformat()
                    
                    if next_date:
                        cursor.execute(
                            "UPDATE scheduled_payments SET next_date = %s WHERE payment_id = %s",
                            (next_date, payment['payment_id'])
                        )
                        processed_count += 1
            
            conn.commit()
            conn.close()
            
            return processed_count
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            print(f"Error processing scheduled payments: {e}")
            return 0