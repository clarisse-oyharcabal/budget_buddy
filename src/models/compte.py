class CompteBancaire:
    def __init__(self, id_compte, utilisateur_id, numero_compte, solde=0.0):
        self.id = id_compte
        self.utilisateur_id = utilisateur_id
        self.numero_compte = numero_compte
        self.solde = solde

    def deposer(self, montant):
        """Ajoute un montant au solde."""
        if montant > 0:
            self.solde += montant
            return True
        return False

    def retirer(self, montant):
        """Retire un montant si le solde est suffisant."""
        if 0 < montant <= self.solde:
            self.solde -= montant
            return True
        return False
