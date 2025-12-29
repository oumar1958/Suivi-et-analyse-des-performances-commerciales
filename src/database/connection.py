"""
Module de gestion des connexions à la base de données.

Fournit une interface pour se connecter à la base de données SQLite
et exécuter des requêtes de manière sécurisée.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict, List, Union
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemin vers la base de données
def get_db_path() -> Path:
    """Retourne le chemin vers le fichier de la base de données."""
    return Path(__file__).parent.parent.parent / "data" / "chinook.db"

def get_db_connection() -> sqlite3.Connection:
    """
    Établit une connexion à la base de données SQLite.
    
    Returns:
        sqlite3.Connection: Une connexion à la base de données.
        
    Raises:
        sqlite3.Error: Si la connexion à la base de données échoue.
    """
    db_path = get_db_path()
    if not db_path.exists():
        logger.error(f"Le fichier de base de données n'existe pas : {db_path}")
        raise FileNotFoundError(f"Le fichier de base de données est introuvable : {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Permet l'accès aux colonnes par nom
        logger.info(f"Connexion établie avec la base de données : {db_path.name}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur de connexion à la base de données : {e}")
        raise

def execute_query(
    query: str, 
    params: Optional[Union[tuple, dict]] = None, 
    fetch: str = 'all'
) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
    """
    Exécute une requête SQL et retourne les résultats.
    
    Args:
        query: La requête SQL à exécuter.
        params: Paramètres pour la requête (optionnel).
        fetch: Type de récupération : 'all', 'one' ou 'none'.
        
    Returns:
        Selon la valeur de 'fetch' :
        - 'all' : Liste de dictionnaires représentant les lignes
        - 'one' : Un dictionnaire représentant une seule ligne
        - 'none' : Aucun résultat (pour les INSERT, UPDATE, DELETE)
        
    Raises:
        sqlite3.Error: Si une erreur survient lors de l'exécution de la requête.
        ValueError: Si la valeur de 'fetch' n'est pas valide.
    """
    if fetch not in ('all', 'one', 'none'):
        raise ValueError("Le paramètre 'fetch' doit être 'all', 'one' ou 'none'.")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.debug(f"Exécution de la requête : {query}")
        if params:
            logger.debug(f"Avec les paramètres : {params}")
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch == 'none':
            conn.commit()
            return None
            
        rows = cursor.fetchall()
        
        if fetch == 'one':
            return dict(rows[0]) if rows else None
            
        return [dict(row) for row in rows]
        
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'exécution de la requête : {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

class DatabaseManager:
    """Classe utilitaire pour gérer les connexions à la base de données."""
    
    def __init__(self):
        self.connection = None
    
    def __enter__(self):
        """Ouvre une connexion à la base de données."""
        self.connection = get_db_connection()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme la connexion à la base de données."""
        if self.connection:
            if exc_type is not None:  # Une exception s'est produite
                self.connection.rollback()
            else:
                self.connection.commit()
            self.connection.close()
            logger.info("Connexion à la base de données fermée")
