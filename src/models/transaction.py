from datetime import datetime

class Transaction:
    TYPES = ["dépôt", "retrait", "transfert"]

    def __init__(self, id_transaction, compte_id, montant, type_transaction, description="", date=None):
        if type_transaction not in self.TYPES:
            raise ValueError("Type de transaction invalide")

        self.id = id_transaction
        self.compte_id = compte_id
        self.montant = montant
        self.type = type_transaction
        self.description = description
        self.date = date if date else datetime.now()

    def __str__(self):
        return f"[{self.date}] {self.type.capitalize()} de {self.montant}€ - {self.description}"
