"""
Package de gestion de la base de données.

Ce package contient les modules pour la connexion à la base de données
et l'exécution des requêtes SQL.
"""

from .connection import get_db_connection

__all__ = ['get_db_connection']
