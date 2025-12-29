"""
Package contenant les modèles de données de l'application.

Ce package contient les classes qui représentent les entités métier
de l'application, comme les clients, les commandes, les produits, etc.
"""

from .base import BaseModel
from .customer import Customer
from .employee import Employee
from .invoice import Invoice, InvoiceLine
from .product import Product, Artist, Album, Genre, MediaType

__all__ = [
    'BaseModel',
    'Customer',
    'Employee',
    'Invoice',
    'InvoiceLine',
    'Product',
    'Artist',
    'Album',
    'Genre',
    'MediaType'
]
