import sqlite3
import pandas as pd

def get_table_info(db_path):
    """Affiche les informations sur les tables de la base de données"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Récupérer la liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables dans la base de données:")
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        print("-" * 50)
        
        # Récupérer les informations sur les colonnes
        try:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Colonnes:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                
            # Afficher un échantillon de données
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample = cursor.fetchall()
            print("\nExemple de données:")
            for row in sample:
                print(f"  {row}")
                
        except sqlite3.Error as e:
            print(f"  Erreur lors de la lecture de la table: {e}")
    
    conn.close()

if __name__ == "__main__":
    db_path = "data/chinook.db"
    print(f"Inspection de la base de données: {db_path}")
    get_table_info(db_path)
