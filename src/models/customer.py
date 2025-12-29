"""
Module contenant le modèle Customer.

Ce module définit la classe Customer qui représente un client dans le système.
"""

from datetime import datetime
from typing import Optional
from .base import BaseModel

class Customer(BaseModel):
    """
    Modèle représentant un client.
    
    Attributs:
        customer_id: Identifiant unique du client
        first_name: Prénom du client
        last_name: Nom de famille du client
        company: Nom de l'entreprise (optionnel)
        address: Adresse
        city: Ville
        state: État/Région (optionnel)
        country: Pays
        postal_code: Code postal
        phone: Numéro de téléphone (optionnel)
        fax: Numéro de fax (optionnel)
        email: Adresse e-mail
        support_rep_id: Identifiant du représentant commercial
    """
    
    _table_name = 'Customer'
    _primary_key = 'CustomerId'
    _fields = {
        'customer_id': int,  # CustomerId
        'first_name': str,   # FirstName
        'last_name': str,    # LastName
        'company': str,      # Company
        'address': str,      # Address
        'city': str,         # City
        'state': str,        # State
        'country': str,      # Country
        'postal_code': str,  # PostalCode
        'phone': str,        # Phone
        'fax': str,          # Fax
        'email': str,        # Email
        'support_rep_id': int  # SupportRepId
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'CustomerId': 'customer_id',
            'FirstName': 'first_name',
            'LastName': 'last_name',
            'Company': 'company',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Country': 'country',
            'PostalCode': 'postal_code',
            'Phone': 'phone',
            'Fax': 'fax',
            'Email': 'email',
            'SupportRepId': 'support_rep_id'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet du client."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_invoices(self) -> list:
        """
        Récupère les factures associées à ce client.
        
        Returns:
            Liste des factures du client.
        """
        # Cette méthode nécessiterait une implémentation avec un service ou un repository
        # C'est un exemple d'emplacement pour cette logique
        pass
    
    def get_total_spent(self) -> float:
        """
        Calcule le montant total dépensé par le client.
        
        Returns:
            Le montant total des achats du client.
        """
        # À implémenter avec une requête SQL ou un service
        return 0.0
    
    def get_favorite_genres(self, limit: int = 3) -> list:
        """
        Récupère les genres de musique préférés du client.
        
        Args:
            limit: Nombre maximum de genres à retourner
            
        Returns:
            Liste des genres préférés avec le nombre d'achats
        """
        # À implémenter avec une requête SQL ou un service
        return []
    
    def __str__(self) -> str:
        """Représentation en chaîne du client."""
        return self.full_name
