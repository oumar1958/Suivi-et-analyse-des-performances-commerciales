"""
Module contenant le modèle Employee.

Ce module définit la classe Employee qui représente un employé dans le système.
"""

from datetime import datetime
from typing import Optional, List
from .base import BaseModel

class Employee(BaseModel):
    """
    Modèle représentant un employé.
    
    Attributs:
        employee_id: Identifiant unique de l'employé
        last_name: Nom de famille
        first_name: Prénom
        title: Titre du poste
        reports_to: Identifiant du supérieur hiérarchique (optionnel)
        birth_date: Date de naissance (optionnel)
        hire_date: Date d'embauche (optionnel)
        address: Adresse (optionnel)
        city: Ville (optionnel)
        state: État/Région (optionnel)
        country: Pays (optionnel)
        postal_code: Code postal (optionnel)
        phone: Numéro de téléphone (optionnel)
        fax: Numéro de fax (optionnel)
        email: Adresse e-mail (optionnel)
    """
    
    _table_name = 'Employee'
    _primary_key = 'EmployeeId'
    _fields = {
        'employee_id': int,      # EmployeeId
        'last_name': str,       # LastName
        'first_name': str,      # FirstName
        'title': str,           # Title
        'reports_to': int,      # ReportsTo
        'birth_date': datetime, # BirthDate
        'hire_date': datetime,  # HireDate
        'address': str,         # Address
        'city': str,            # City
        'state': str,           # State
        'country': str,         # Country
        'postal_code': str,     # PostalCode
        'phone': str,           # Phone
        'fax': str,             # Fax
        'email': str,           # Email
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'EmployeeId': 'employee_id',
            'LastName': 'last_name',
            'FirstName': 'first_name',
            'Title': 'title',
            'ReportsTo': 'reports_to',
            'BirthDate': 'birth_date',
            'HireDate': 'hire_date',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Country': 'country',
            'PostalCode': 'postal_code',
            'Phone': 'phone',
            'Fax': 'fax',
            'Email': 'email'
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
        """Retourne le nom complet de l'employé."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_manager(self) -> bool:
        """Vérifie si l'employé est un manager."""
        return 'manager' in self.title.lower() if self.title else False
    
    def get_subordinates(self) -> List['Employee']:
        """
        Récupère les subordonnés directs de cet employé.
        
        Returns:
            Liste des employés qui rapportent à cet employé
        """
        # À implémenter avec une requête SQL ou un service
        return []
    
    def get_customers(self) -> List['Customer']:
        """
        Récupère les clients assignés à cet employé (pour les commerciaux).
        
        Returns:
            Liste des clients gérés par cet employé
        """
        # À implémenter avec une requête SQL ou un service
        return []
    
    def get_sales_summary(self, start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> dict:
        """
        Récupère un résumé des ventes pour cet employé.
        
        Args:
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Dictionnaire contenant les statistiques de vente
        """
        # À implémenter avec une requête SQL ou un service
        return {
            'total_sales': 0.0,
            'order_count': 0,
            'average_order_value': 0.0,
            'customer_count': 0
        }
    
    def __str__(self) -> str:
        """Représentation en chaîne de l'employé."""
        return f"{self.full_name} ({self.title or 'No Title'})"
