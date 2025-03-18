from .database import Database

class CompteDB:
    def __init__(self):
        self.db = Database()

    def creer_compte(self, utilisateur_id, numero_compte, solde_initial=0.0):
        """Crée un compte bancaire pour un utilisateur."""
        self.db.executer_requete("""
            INSERT INTO compte (utilisateur_id, numero_compte, solde)
            VALUES (?, ?, ?)""", (utilisateur_id, numero_compte, solde_initial))

    def obtenir_comptes_utilisateur(self, utilisateur_id):
        """Récupère tous les comptes d'un utilisateur."""
        return self.db.fetchall("SELECT * FROM compte WHERE utilisateur_id = ?", (utilisateur_id,))
