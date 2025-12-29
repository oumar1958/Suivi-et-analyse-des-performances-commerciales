"""
Package pour les requêtes SQL organisées par domaine fonctionnel.

Ce package contient des modules avec des requêtes SQL spécifiques
à différents domaines (ventes, clients, produits, etc.).
"""

# Importez ici les modules de requêtes pour les exposer au niveau du package
from .sales import (
    get_sales_by_period,
    get_sales_by_country,
    get_top_selling_products,
    get_sales_by_employee,
    get_recent_orders
)

__all__ = [
    'get_sales_by_period',
    'get_sales_by_country',
    'get_top_selling_products',
    'get_sales_by_employee',
    'get_recent_orders'
]
