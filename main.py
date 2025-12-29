#!/usr/bin/env python3
"""
Système d'Automatisation des Rapports de Ventes
Ce script permet d'exécuter des requêtes SQL sur la base de données Chinook
et de générer des rapports au format CSV, Excel ou PDF.
"""

import os
import sys
import configparser
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Création des dossiers nécessaires
os.makedirs(config['REPORTS']['OUTPUT_DIR'], exist_ok=True)

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None):
        """Exécute une requête et retourne les résultats sous forme de DataFrame"""
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            return df
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            return None

class ReportGenerator:
    """Générateur de rapports"""
    
    def __init__(self, output_dir, output_format='csv'):
        self.output_dir = output_dir
        self.output_format = output_format
    
    def save_report(self, df, report_name):
        """Sauvegarde le rapport dans le format spécifié"""
        if df is None or df.empty:
            print(f"Aucune donnée à exporter pour le rapport {report_name}")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_name}_{timestamp}.{self.output_format}"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if self.output_format == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            elif self.output_format == 'xlsx':
                df.to_excel(filepath, index=False, sheet_name=report_name[:31])
            elif self.output_format == 'json':
                df.to_json(filepath, orient='records', force_ascii=False, indent=2)
            else:
                raise ValueError(f"Format de sortie non supporté: {self.output_format}")
            
            print(f"Rapport sauvegardé: {filepath}")
            return filepath
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du rapport {report_name}: {e}")
            return None

def load_sql_query(query_name):
    """Charge une requête SQL depuis le dossier queries"""
    query_path = os.path.join('queries', f"{query_name}.sql")
    try:
        with open(query_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erreur: Le fichier de requête {query_path} est introuvable.")
        return None

def generate_reports():
    """Génère tous les rapports configurés"""
    db_path = config['DATABASE']['DB_PATH']
    output_format = config['REPORTS']['OUTPUT_FORMAT']
    
    # Vérification de l'existence de la base de données
    if not os.path.exists(db_path):
        print(f"Erreur: La base de données {db_path} est introuvable.")
        return
    
    # Initialisation des gestionnaires
    report_gen = ReportGenerator(
        output_dir=config['REPORTS']['OUTPUT_DIR'],
        output_format=output_format
    )
    
    with DatabaseManager(db_path) as db:
        # Exemple d'exécution de requêtes et génération de rapports
        reports = [
            ('clients_par_pays', 'Clients par pays'),
            ('ventes_par_annee', 'Ventes par année'),
            ('meilleurs_agents', 'Meilleurs agents de vente'),
            ('produits_plus_vendus', 'Produits les plus vendus')
        ]
        
        for query_name, report_name in reports:
            query = load_sql_query(query_name)
            if query:
                print(f"Génération du rapport: {report_name}")
                df = db.execute_query(query)
                if df is not None:
                    report_gen.save_report(df, report_name.replace(' ', '_').lower())

def main():
    """Fonction principale"""
    print("=== Système d'Automatisation des Rapports de Ventes ===\n")
    
    # Création des dossiers nécessaires
    os.makedirs(config['REPORTS']['OUTPUT_DIR'], exist_ok=True)
    
    # Génération des rapports
    generate_reports()
    
    print("\nTraitement terminé avec succès!")

if __name__ == "__main__":
    main()
