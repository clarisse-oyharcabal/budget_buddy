from .database import Database

class UtilisateurDB:
    def __init__(self):
        self.db = Database()

    def ajouter_utilisateur(self, nom, prenom, email, mot_de_passe):
        """Ajoute un nouvel utilisateur à la base de données."""
        try:
            self.db.executer_requete("""
                INSERT INTO utilisateur (nom, prenom, email, mot_de_passe)
                VALUES (?, ?, ?, ?)""", (nom, prenom, email, mot_de_passe))
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'utilisateur : {e}")
            return False

    def obtenir_utilisateur(self, email):
        """Récupère un utilisateur par email."""
        return self.db.fetchone("SELECT * FROM utilisateur WHERE email = ?", (email,))
