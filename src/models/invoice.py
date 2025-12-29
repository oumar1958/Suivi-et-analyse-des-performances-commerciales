"""
Module contenant les modèles liés aux factures.

Ce module définit les classes Invoice et InvoiceLine qui représentent
respectivement une facture et une ligne de facture dans le système.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from .base import BaseModel

class InvoiceLine(BaseModel):
    """
    Modèle représentant une ligne de facture.
    
    Attributs:
        invoice_line_id: Identifiant unique de la ligne
        invoice_id: Identifiant de la facture associée
        track_id: Identifiant de la piste musicale
        unit_price: Prix unitaire
        quantity: Quantité
    """
    
    _table_name = 'InvoiceLine'
    _primary_key = 'InvoiceLineId'
    _fields = {
        'invoice_line_id': int,  # InvoiceLineId
        'invoice_id': int,       # InvoiceId
        'track_id': int,         # TrackId
        'unit_price': float,     # UnitPrice
        'quantity': int,         # Quantity
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'InvoiceLineId': 'invoice_line_id',
            'InvoiceId': 'invoice_id',
            'TrackId': 'track_id',
            'UnitPrice': 'unit_price',
            'Quantity': 'quantity'
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
    def total(self) -> float:
        """Calcule le total de la ligne (prix unitaire × quantité)."""
        return self.unit_price * self.quantity
    
    def get_track(self) -> Optional['Track']:
        """
        Récupère la piste musicale associée à cette ligne.
        
        Returns:
            L'objet Track associé ou None si non trouvé
        """
        # À implémenter avec un service ou un repository
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la ligne de facture en dictionnaire.
        
        Returns:
            Dictionnaire contenant les données de la ligne de facture
        """
        data = super().to_dict()
        data['total'] = self.total
        return data


class Invoice(BaseModel):
    """
    Modèle représentant une facture.
    
    Attributs:
        invoice_id: Identifiant unique de la facture
        customer_id: Identifiant du client
        invoice_date: Date de la facture
        billing_address: Adresse de facturation
        billing_city: Ville de facturation
        billing_state: État/Région de facturation (optionnel)
        billing_country: Pays de facturation
        billing_postal_code: Code postal de facturation (optionnel)
        total: Montant total de la facture
    """
    
    _table_name = 'Invoice'
    _primary_key = 'InvoiceId'
    _fields = {
        'invoice_id': int,          # InvoiceId
        'customer_id': int,         # CustomerId
        'invoice_date': datetime,   # InvoiceDate
        'billing_address': str,     # BillingAddress
        'billing_city': str,        # BillingCity
        'billing_state': str,       # BillingState
        'billing_country': str,     # BillingCountry
        'billing_postal_code': str, # BillingPostalCode
        'total': float              # Total
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'InvoiceId': 'invoice_id',
            'CustomerId': 'customer_id',
            'InvoiceDate': 'invoice_date',
            'BillingAddress': 'billing_address',
            'BillingCity': 'billing_city',
            'BillingState': 'billing_state',
            'BillingCountry': 'billing_country',
            'BillingPostalCode': 'billing_postal_code',
            'Total': 'total'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
        self._lines = None
    
    def get_customer(self) -> Optional['Customer']:
        """
        Récupère le client associé à cette facture.
        
        Returns:
            L'objet Customer associé ou None si non trouvé
        """
        # À implémenter avec un service ou un repository
        return None
    
    def get_lines(self, force_refresh: bool = False) -> List[InvoiceLine]:
        """
        Récupère les lignes de la facture.
        
        Args:
            force_refresh: Si True, force le rechargement depuis la base de données
            
        Returns:
            Liste des lignes de la facture
        """
        if self._lines is None or force_refresh:
            # À implémenter avec un service ou un repository
            # Exemple: self._lines = invoice_service.get_invoice_lines(self.invoice_id)
            self._lines = []
        
        return self._lines
    
    def add_line(self, track_id: int, unit_price: float, quantity: int = 1) -> InvoiceLine:
        """
        Ajoute une ligne à la facture.
        
        Args:
            track_id: Identifiant de la piste musicale
            unit_price: Prix unitaire
            quantity: Quantité (par défaut: 1)
            
        Returns:
            La ligne de facture créée
        """
        line = InvoiceLine(
            invoice_id=self.invoice_id,
            track_id=track_id,
            unit_price=unit_price,
            quantity=quantity
        )
        
        if self._lines is None:
            self._lines = []
        
        self._lines.append(line)
        return line
    
    def calculate_total(self) -> float:
        """
        Calcule le total de la facture en additionnant toutes les lignes.
        
        Returns:
            Le montant total de la facture
        """
        if not self._lines:
            return 0.0
        
        return sum(line.total for line in self._lines)
    
    def to_dict(self, include_lines: bool = True) -> Dict[str, Any]:
        """
        Convertit la facture en dictionnaire.
        
        Args:
            include_lines: Si True, inclut les lignes de la facture
            
        Returns:
            Dictionnaire contenant les données de la facture
        """
        data = super().to_dict()
        
        if include_lines:
            data['lines'] = [line.to_dict() for line in self.get_lines()]
        
        return data
    
    def __str__(self) -> str:
        """Représentation en chaîne de la facture."""
        return f"Facture #{self.invoice_id} - {self.total:.2f} €"
