from .database import Database

class TransactionDB:
    def __init__(self):
        self.db = Database()

    def ajouter_transaction(self, compte_id, montant, type_transaction, description=""):
        """Ajoute une transaction et met à jour le solde du compte."""
        self.db.executer_requete("""
            INSERT INTO transaction (compte_id, montant, type, description)
            VALUES (?, ?, ?, ?)""", (compte_id, montant, type_transaction, description))

        # Mettre à jour le solde
        if type_transaction == "dépôt":
            self.db.executer_requete("""
                UPDATE compte SET solde = solde + ? WHERE id = ?""", (montant, compte_id))
        elif type_transaction == "retrait":
            self.db.executer_requete("""
                UPDATE compte SET solde = solde - ? WHERE id = ?""", (montant, compte_id))

    def obtenir_historique(self, compte_id):
        """Récupère l'historique des transactions pour un compte."""
        return self.db.fetchall("SELECT * FROM transaction WHERE compte_id = ? ORDER BY date DESC", (compte_id,))
