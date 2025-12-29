"""
Requêtes SQL pour les opérations liées aux ventes.

Ce module contient des fonctions pour récupérer des données de vente
depuis la base de données Chinook.
"""

from typing import List, Dict, Optional, Tuple
from datetime import date
from ...database.connection import execute_query


def get_sales_by_period(
    start_date: date, 
    end_date: date,
    group_by: str = 'month'
) -> List[Dict]:
    """
    Récupère les ventes agrégées par période.
    
    Args:
        start_date: Date de début de la période
        end_date: Date de fin de la période
        group_by: Période d'agrégation ('day', 'month', 'year')
        
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
        strftime('{date_format}', i.InvoiceDate) AS period,
        COUNT(DISTINCT i.InvoiceId) AS order_count,
        SUM(i.Total) AS total_sales,
        AVG(i.Total) AS avg_order_value,
        COUNT(DISTINCT i.CustomerId) AS customer_count
    FROM Invoice i
    WHERE date(i.InvoiceDate) BETWEEN ? AND ?
    GROUP BY period
    ORDER BY period
    """
    
    return execute_query(
        query, 
        (start_date.isoformat(), end_date.isoformat()),
        fetch='all'
    )


def get_sales_by_country(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict]:
    """
    Récupère les ventes agrégées par pays.
    
    Args:
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        
    Returns:
        Liste de dictionnaires contenant les ventes par pays
    """
    query = """
    SELECT 
        i.BillingCountry AS country,
        COUNT(DISTINCT i.InvoiceId) AS order_count,
        SUM(i.Total) AS total_sales,
        COUNT(DISTINCT i.CustomerId) AS customer_count
    FROM Invoice i
    """
    
    params = []
    where_clauses = []
    
    if start_date:
        where_clauses.append("date(i.InvoiceDate) >= ?")
        params.append(start_date.isoformat())
    
    if end_date:
        where_clauses.append("date(i.InvoiceDate) <= ?")
        params.append(end_date.isoformat())
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += """
    GROUP BY i.BillingCountry
    ORDER BY total_sales DESC
    """
    
    return execute_query(query, tuple(params) if params else None, fetch='all')


def get_top_selling_products(
    limit: int = 10,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict]:
    """
    Récupère les produits les plus vendus.
    
    Args:
        limit: Nombre maximum de produits à retourner
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        
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
        COUNT(il.InvoiceLineId) AS quantity_sold,
        SUM(il.UnitPrice * il.Quantity) AS revenue
    FROM Track t
    JOIN Album al ON t.AlbumId = al.AlbumId
    JOIN Artist ar ON al.ArtistId = ar.ArtistId
    JOIN Genre g ON t.GenreId = g.GenreId
    JOIN InvoiceLine il ON t.TrackId = il.TrackId
    JOIN Invoice i ON il.InvoiceId = i.InvoiceId
    """
    
    params = []
    where_clauses = []
    
    if start_date:
        where_clauses.append("date(i.InvoiceDate) >= ?")
        params.append(start_date.isoformat())
    
    if end_date:
        where_clauses.append("date(i.InvoiceDate) <= ?")
        params.append(end_date.isoformat())
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += """
    GROUP BY t.TrackId
    ORDER BY quantity_sold DESC
    LIMIT ?
    """
    params.append(limit)
    
    return execute_query(query, tuple(params), fetch='all')


def get_sales_by_employee(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict]:
    """
    Récupère les ventes par employé.
    
    Args:
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
        
    Returns:
        Liste des employés avec leurs statistiques de vente
    """
    query = """
    SELECT 
        e.EmployeeId,
        e.FirstName || ' ' || e.LastName AS employee_name,
        e.Title,
        e.HireDate,
        COUNT(DISTINCT i.InvoiceId) AS order_count,
        SUM(i.Total) AS total_sales,
        COUNT(DISTINCT c.CustomerId) AS customer_count,
        AVG(i.Total) AS avg_order_value
    FROM Employee e
    LEFT JOIN Customer c ON e.EmployeeId = c.SupportRepId
    LEFT JOIN Invoice i ON c.CustomerId = i.CustomerId
    """
    
    params = []
    where_clauses = ["e.Title LIKE '%Sales%'"]
    
    if start_date:
        where_clauses.append("date(i.InvoiceDate) >= ?")
        params.append(start_date.isoformat())
    
    if end_date:
        where_clauses.append("date(i.InvoiceDate) <= ?")
        params.append(end_date.isoformat())
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += """
    GROUP BY e.EmployeeId
    ORDER BY total_sales DESC
    """
    
    return execute_query(
        query, 
        tuple(params) if params else None, 
        fetch='all'
    )


def get_recent_orders(limit: int = 10) -> List[Dict]:
    """
    Récupère les commandes les plus récentes.
    
    Args:
        limit: Nombre maximum de commandes à retourner
        
    Returns:
        Liste des commandes récentes avec les détails
    """
    query = """
    SELECT 
        i.InvoiceId,
        i.InvoiceDate,
        c.FirstName || ' ' || c.LastName AS customer_name,
        c.Country,
        i.Total,
        e.FirstName || ' ' || e.LastName AS employee_name,
        (
            SELECT COUNT(*) 
            FROM InvoiceLine 
            WHERE InvoiceId = i.InvoiceId
        ) AS item_count
    FROM Invoice i
    JOIN Customer c ON i.CustomerId = c.CustomerId
    JOIN Employee e ON c.SupportRepId = e.EmployeeId
    ORDER BY i.InvoiceDate DESC
    LIMIT ?
    """
    
    return execute_query(query, (limit,), fetch='all')
