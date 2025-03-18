import hashlib

class Utilisateur:
    def __init__(self, id_utilisateur, nom, prenom, email, mot_de_passe):
        self.id = id_utilisateur
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe

    @staticmethod
    def hasher_mot_de_passe(mot_de_passe):
        """Hache le mot de passe avant stockage."""
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()

    def verifier_mot_de_passe(self, mot_de_passe):
        """Vérifie si le mot de passe correspond au hash stocké."""
        return self.hasher_mot_de_passe(mot_de_passe) == self.mot_de_passe
