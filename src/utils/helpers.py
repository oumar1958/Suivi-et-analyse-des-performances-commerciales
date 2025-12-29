"""
Module d'utilitaires pour l'application de rapports de ventes.

Ce module fournit des fonctions utilitaires pour formater les données,
générer des rapports et effectuer des opérations courantes.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import logging
import os
from pathlib import Path

# Configuration du logger
logger = logging.getLogger(__name__)

def format_currency(amount: float) -> str:
    """
    Formate un montant en devise avec le symbole € et 2 décimales.
    
    Args:
        amount: Montant à formater
        
    Returns:
        Chaîne formatée du montant (ex: "1 234,56 €")
    """
    try:
        return f"{amount:,.2f} €".replace(",", " ").replace(".", ",").replace(" ", " ")
    except (ValueError, TypeError):
        return "0,00 €"

def format_date(
    date_value: Union[str, date, datetime], 
    format_str: str = "%d/%m/%Y"
) -> str:
    """
    Formate une date selon le format spécifié.
    
    Args:
        date_value: Date à formater (chaîne, date ou datetime)
        format_str: Format de sortie (par défaut: "%d/%m/%Y")
        
    Returns:
        Chaîne formatée de la date
    """
    if not date_value:
        return ""
    
    try:
        if isinstance(date_value, str):
            # Essayer de parser la date si c'est une chaîne
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    date_obj = datetime.strptime(date_value, fmt)
                    return date_obj.strftime(format_str)
                except ValueError:
                    continue
            return date_value  # Retourner la chaîne d'origine si le format n'est pas reconnu
        
        # Si c'est déjà un objet date ou datetime
        if isinstance(date_value, (date, datetime)):
            return date_value.strftime(format_str)
            
        return str(date_value)
    except Exception as e:
        logger.warning(f"Erreur lors du formatage de la date {date_value}: {e}")
        return str(date_value)

def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Vérifie si un répertoire existe, le crée si nécessaire.
    
    Args:
        directory: Chemin du répertoire à vérifier/créer
        
    Returns:
        Objet Path du répertoire
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def get_file_extension(filename: str) -> str:
    """
    Récupère l'extension d'un fichier en minuscules.
    
    Args:
        filename: Nom du fichier
        
    Returns:
        Extension du fichier en minuscules (sans le point)
    """
    return Path(filename).suffix.lower().lstrip('.')

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Effectue une division sécurisée avec gestion de la division par zéro.
    
    Args:
        numerator: Numérateur
        denominator: Dénominateur
        default: Valeur par défaut en cas de division par zéro
        
    Returns:
        Résultat de la division ou valeur par défaut
    """
    try:
        return float(numerator) / float(denominator) if float(denominator) != 0 else default
    except (ValueError, TypeError):
        return default

def format_percentage(
    value: float, 
    decimals: int = 2, 
    include_sign: bool = True
) -> str:
    """
    Formate un nombre en pourcentage.
    
    Args:
        value: Valeur à formater (ex: 0.125 pour 12.5%)
        decimals: Nombre de décimales à afficher
        include_sign: Si True, ajoute le symbole %
        
    Returns:
        Chaîne formatée du pourcentage
    """
    try:
        formatted = f"{value * 100:,.{decimals}f}".replace(",", " ").replace(".", ",")
        return f"{formatted}%" if include_sign else formatted
    except (ValueError, TypeError):
        return f"0,{'0' * decimals}%" if include_sign else f"0,{'0' * decimals}"

def get_file_size(file_path: Union[str, Path]) -> str:
    """
    Retourne la taille d'un fichier dans un format lisible.
    
    Args:
        file_path: Chemin vers le fichier
        
    Returns:
        Chaîne formatée de la taille (ex: "1,23 Mo")
    """
    try:
        size_bytes = os.path.getsize(file_path)
        for unit in ['o', 'Ko', 'Mo', 'Go', 'To']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} Po"
    except OSError:
        return "Taille inconnue"

def clean_string(text: str) -> str:
    """
    Nettoie une chaîne de caractères en supprimant les espaces superflus
    et en normalisant les sauts de ligne.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé
    """
    if not text:
        return ""
    
    # Supprimer les espaces en début et fin de ligne
    lines = [line.strip() for line in text.splitlines()]
    # Supprimer les lignes vides
    lines = [line for line in lines if line]
    # Rejoindre avec des espaces simples
    return " ".join(lines).strip()

def dict_to_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    """
    Convertit une liste de dictionnaires en une table formatée en texte.
    
    Args:
        data: Liste de dictionnaires à afficher
        headers: En-têtes de colonnes (optionnel, utilise les clés du premier dictionnaire si non fourni)
        
    Returns:
        Chaîne formatée représentant la table
    """
    if not data:
        return "Aucune donnée à afficher"
    
    # Utiliser les clés du premier dictionnaire comme en-têtes si non fournis
    if not headers:
        headers = list(data[0].keys())
    
    # Calculer la largeur de chaque colonne
    col_widths = []
    for i, header in enumerate(headers):
        max_len = len(str(header))
        for row in data:
            if header in row:
                max_len = max(max_len, len(str(row[header])))
        col_widths.append(max_len + 2)  # Ajouter un peu d'espace
    
    # Construire la ligne de séparation
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    # Construire la table
    table = [separator]
    
    # Ajouter les en-têtes
    header_row = "| " + " | ".join(f"{h:{w}}" for h, w in zip(headers, col_widths)) + " |"
    table.append(header_row)
    table.append(separator.replace("-", "="))
    
    # Ajouter les données
    for row in data:
        row_data = [str(row.get(header, "")) for header in headers]
        data_row = "| " + " | ".join(f"{d:{w}}" for d, w in zip(row_data, col_widths)) + " |"
        table.append(data_row)
        table.append(separator)
    
    return "\n".join(table)
