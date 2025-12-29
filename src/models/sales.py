"""
Module contenant le modèle Sales.

Ce module définit la classe Sales pour représenter les données de vente.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from .base import BaseModel

class Sales(BaseModel):
    """
    Modèle représentant une vente.
    
    Attributs:
        sale_id: Identifiant unique de la vente
        invoice_id: Numéro de facture
        customer_id: Identifiant du client
        invoice_date: Date de la facture
        billing_address: Adresse de facturation
        billing_city: Ville de facturation
        billing_state: État/Région de facturation (optionnel)
        billing_country: Pays de facturation
        billing_postal_code: Code postal de facturation
        total: Montant total de la facture
    """
    
    _table_name = 'Invoice'
    _primary_key = 'InvoiceId'
    _fields = {
        'sale_id': int,          # InvoiceId
        'customer_id': int,      # CustomerId
        'invoice_date': str,     # InvoiceDate (stocké en tant que chaîne ISO)
        'billing_address': str,  # BillingAddress
        'billing_city': str,     # BillingCity
        'billing_state': str,    # BillingState
        'billing_country': str,  # BillingCountry
        'billing_postal_code': str,  # BillingPostalCode
        'total': float,          # Total
    }
    
    def __init__(self, **kwargs):
        # Conversion des noms de colonnes de la base de données vers les noms d'attributs Python
        mapped_kwargs = {}
        for key, value in kwargs.items():
            # Convertir les noms de colonnes comme 'InvoiceId' en 'sale_id'
            if key == 'InvoiceId':
                mapped_kwargs['sale_id'] = value
            elif key == 'CustomerId':
                mapped_kwargs['customer_id'] = value
            elif key == 'InvoiceDate':
                mapped_kwargs['invoice_date'] = value
            elif key == 'BillingAddress':
                mapped_kwargs['billing_address'] = value
            elif key == 'BillingCity':
                mapped_kwargs['billing_city'] = value
            elif key == 'BillingState':
                mapped_kwargs['billing_state'] = value
            elif key == 'BillingCountry':
                mapped_kwargs['billing_country'] = value
            elif key == 'BillingPostalCode':
                mapped_kwargs['billing_postal_code'] = value
            elif key == 'Total':
                mapped_kwargs['total'] = value
        
        super().__init__(**mapped_kwargs)
    
    @classmethod
    def get_sales_by_period(
        cls, 
        start_date: str, 
        end_date: str,
        group_by: str = 'month'
    ) -> List[Dict[str, Any]]:
        """
        Récupère les ventes agrégées par période.
        
        Args:
            start_date: Date de début au format 'YYYY-MM-DD'
            end_date: Date de fin au format 'YYYY-MM-DD'
            group_by: Période de regroupement ('day', 'month', 'year')
            
        Returns:
            Liste de dictionnaires contenant les données de vente agrégées
        """
        if group_by not in ('day', 'month', 'year'):
            raise ValueError("group_by doit être 'day', 'month' ou 'year'")
        
        # Format de date en fonction du groupement
        date_format = {
            'day': '%Y-%m-%d',
            'month': '%Y-%m',
            'year': '%Y'
        }[group_by]
        
        query = f"""
        SELECT 
            strftime('{date_format}', InvoiceDate) AS period,
            COUNT(DISTINCT InvoiceId) AS order_count,
            SUM(Total) AS total_sales,
            AVG(Total) AS avg_order_value,
            COUNT(DISTINCT CustomerId) AS customer_count
        FROM Invoice
        WHERE date(InvoiceDate) BETWEEN ? AND ?
        GROUP BY period
        ORDER BY period
        """
        
        return cls.execute_query(query, (start_date, end_date))
    
    @classmethod
    def get_top_selling_products(
        cls,
        limit: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les produits les plus vendus.
        
        Args:
            limit: Nombre maximum de produits à retourner
            start_date: Date de début au format 'YYYY-MM-DD' (optionnel)
            end_date: Date de fin au format 'YYYY-MM-DD' (optionnel)
            
        Returns:
            Liste des produits les plus vendus avec leurs statistiques
        """
        query = """
        SELECT 
            t.TrackId,
            t.Name AS track_name,
            ar.Name AS artist_name,
            al.Title AS album_title,
            g.Name AS genre,
            COUNT(DISTINCT i.InvoiceId) AS times_ordered,
            SUM(il.Quantity) AS total_quantity,
            SUM(il.UnitPrice * il.Quantity) AS total_sales
        FROM Track t
        JOIN Album al ON t.AlbumId = al.AlbumId
        JOIN Artist ar ON al.ArtistId = ar.ArtistId
        JOIN Genre g ON t.GenreId = g.GenreId
        JOIN InvoiceLine il ON t.TrackId = il.TrackId
        JOIN Invoice i ON il.InvoiceId = i.InvoiceId
        """
        
        params = []
        if start_date and end_date:
            query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += """
        GROUP BY t.TrackId
        ORDER BY total_sales DESC
        LIMIT ?
        """
        params.append(limit)
        
        return cls.execute_query(query, tuple(params))
    
    @classmethod
    def get_sales_by_country(
        cls,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les ventes agrégées par pays.
        
        Args:
            start_date: Date de début au format 'YYYY-MM-DD' (optionnel)
            end_date: Date de fin au format 'YYYY-MM-DD' (optionnel)
            
        Returns:
            Liste des ventes agrégées par pays
        """
        query = """
        SELECT 
            c.Country,
            COUNT(DISTINCT i.InvoiceId) AS order_count,
            COUNT(DISTINCT c.CustomerId) AS customer_count,
            SUM(i.Total) AS total_sales,
            AVG(i.Total) AS avg_order_value
        FROM Invoice i
        JOIN Customer c ON i.CustomerId = c.CustomerId
        """
        
        params = []
        if start_date and end_date:
            query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += """
        GROUP BY c.Country
        ORDER BY total_sales DESC
        """
        
        return cls.execute_query(query, tuple(params) if params else None)
