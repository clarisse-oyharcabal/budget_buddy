-- Création de la base de données Budget Buddy
CREATE DATABASE IF NOT EXISTS budget;
USE budget;

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des comptes
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Table des catégories de transactions
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Insérer quelques catégories par défaut
INSERT INTO categories (category_name, description) VALUES
    ('Loisir', 'Dépenses liées aux activités de loisir'),
    ('Repas', 'Dépenses alimentaires'),
    ('Transport', 'Dépenses liées aux déplacements'),
    ('Logement', 'Dépenses liées au logement'),
    ('Santé', 'Dépenses médicales'),
    ('Vêtements', 'Achats de vêtements'),
    ('Éducation', 'Frais de scolarité et matériel éducatif'),
    ('Revenu', 'Sources de revenu'),
    ('Pot-de-vin', 'Cadeaux et pourboires'),
    ('Autre', 'Autres dépenses');

-- Table des types de transactions
CREATE TABLE IF NOT EXISTS transaction_types (
    type_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) NOT NULL
);

-- Insérer les types de transactions
INSERT INTO transaction_types (type_name) VALUES
    ('Dépôt'),
    ('Retrait'),
    ('Transfert');

-- Table des transactions
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
);

-- Table pour les banquiers (partie "pour aller plus loin")
CREATE TABLE IF NOT EXISTS bankers (
    banker_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de relation entre banquiers et clients
CREATE TABLE IF NOT EXISTS banker_clients (
    banker_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (banker_id, user_id),
    FOREIGN KEY (banker_id) REFERENCES bankers(banker_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Table des alertes et notifications
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
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(type_id);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_users_email ON users(email);
