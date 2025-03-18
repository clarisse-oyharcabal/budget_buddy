import sqlite3

class Database:
    def __init__(self, db_name="budget_buddy.db"):
        """Initialise la connexion à la base de données et crée les tables si nécessaire."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.creer_tables()

    def creer_tables(self):
        """Crée les tables nécessaires si elles n'existent pas encore."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS compte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            numero_compte TEXT UNIQUE NOT NULL,
            solde REAL DEFAULT 0.0,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id)
        )""")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compte_id INTEGER NOT NULL,
            montant REAL NOT NULL,
            type TEXT CHECK(type IN ('dépôt', 'retrait', 'transfert')),
            description TEXT,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (compte_id) REFERENCES compte(id)
        )""")

        self.conn.commit()

    def executer_requete(self, requete, params=()):
        """Exécute une requête SQL avec des paramètres."""
        self.cursor.execute(requete, params)
        self.conn.commit()

    def fetchall(self, requete, params=()):
        """Exécute une requête et retourne tous les résultats."""
        self.cursor.execute(requete, params)
        return self.cursor.fetchall()

    def fetchone(self, requete, params=()):
        """Exécute une requête et retourne un seul résultat."""
        self.cursor.execute(requete, params)
        return self.cursor.fetchone()
