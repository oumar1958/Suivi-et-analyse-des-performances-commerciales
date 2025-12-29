"""
Requêtes SQL pour les opérations liées aux clients.

Ce module contient des fonctions pour récupérer des données clients
depuis la base de données Chinook.
"""

from typing import List, Dict, Optional, Tuple
from datetime import date, datetime
from ...database.connection import execute_query

def get_top_customers(limit: int = 10, start_date: date = None, end_date: date = None) -> List[Dict]:
    """
    Récupère les clients les plus rentables.
    
    Args:
        limit: Nombre maximum de clients à retourner
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        
    Returns:
        Liste des clients avec leurs statistiques d'achat
    """
    query = """
    SELECT 
        c.CustomerId,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.Email,
        c.Country,
        COUNT(DISTINCT i.InvoiceId) AS order_count,
        SUM(i.Total) AS total_spent,
        MAX(i.InvoiceDate) AS last_order_date
    FROM Customer c
    JOIN Invoice i ON c.CustomerId = i.CustomerId
    """
    
    params = []
    if start_date and end_date:
        query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    
    query += """
    GROUP BY c.CustomerId
    ORDER BY total_spent DESC
    LIMIT ?
    """
    params.append(limit)
    
    return execute_query(query, tuple(params))

def get_customer_retention() -> List[Dict]:
    """
    Calcule le taux de rétention des clients.
    
    Returns:
        Statistiques de rétention des clients
    """
    query = """
    WITH customer_activity AS (
        SELECT 
            CustomerId,
            MIN(date(InvoiceDate)) AS first_purchase,
            MAX(date(InvoiceDate)) AS last_purchase,
            COUNT(DISTINCT strftime('%Y-%m', InvoiceDate)) AS active_months,
            (julianday(MAX(InvoiceDate)) - julianday(MIN(InvoiceDate))) / 30.0 AS months_since_first_purchase
        FROM Invoice
        GROUP BY CustomerId
    )
    SELECT 
        COUNT(*) AS total_customers,
        AVG(active_months) AS avg_active_months,
        AVG(CASE 
            WHEN months_since_first_purchase > 0 
            THEN active_months / months_since_first_purchase 
            ELSE 0 
        END) AS avg_retention_rate,
        COUNT(DISTINCT CASE 
            WHEN date('now', '-3 months') <= date(last_purchase) 
            THEN CustomerId 
        END) AS active_last_3_months,
        COUNT(DISTINCT CASE 
            WHEN date('now', '-6 months') <= date(last_purchase) 
            THEN CustomerId 
        END) AS active_last_6_months
    FROM customer_activity
    """
    
    return execute_query(query, fetch='one')

def get_customer_acquisition(start_date: date, end_date: date) -> List[Dict]:
    """
    Analyse l'acquisition des clients sur une période donnée.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        Statistiques d'acquisition des clients
    """
    query = """
    WITH new_customers AS (
        SELECT 
            strftime('%Y-%m', MIN(i.InvoiceDate)) AS acquisition_month,
            COUNT(DISTINCT c.CustomerId) AS new_customers
        FROM Customer c
        JOIN Invoice i ON c.CustomerId = i.CustomerId
        WHERE date(i.InvoiceDate) BETWEEN ? AND ?
        GROUP BY acquisition_month
    )
    SELECT 
        acquisition_month,
        new_customers,
        SUM(new_customers) OVER (ORDER BY acquisition_month) AS total_customers
    FROM new_customers
    ORDER BY acquisition_month
    """
    
    return execute_query(query, (start_date, end_date))
