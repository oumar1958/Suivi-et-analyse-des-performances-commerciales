"""
Requêtes SQL pour la génération de rapports.

Ce module contient des fonctions pour générer des rapports avancés
à partir de la base de données Chinook.
"""

from typing import List, Dict, Optional, Tuple
from datetime import date, datetime, timedelta
from ...database.connection import execute_query

def get_sales_trends(
    period: str = 'month',
    lookback_months: int = 12
) -> List[Dict]:
    """
    Analyse les tendances des ventes sur une période donnée.
    
    Args:
        period: Période d'analyse ('day', 'week', 'month', 'quarter', 'year')
        lookback_months: Nombre de mois en arrière pour l'analyse
        
    Returns:
        Données de tendance des ventes
    """
    if period not in ('day', 'week', 'month', 'quarter', 'year'):
        raise ValueError("La période doit être 'day', 'week', 'month', 'quarter' ou 'year'")
    
    # Calcul des dates de début et de fin
    end_date = datetime.now().date()
    start_date = (datetime.now() - timedelta(days=lookback_months*30)).date()
    
    # Format de date en fonction de la période
    date_formats = {
        'day': '%Y-%m-%d',
        'week': '%Y-%W',
        'month': '%Y-%m',
        'quarter': '%Y-%q',
        'year': '%Y'
    }
    
    query = f"""
    WITH sales_data AS (
        SELECT 
            strftime('{date_formats[period]}', i.InvoiceDate) AS period,
            COUNT(DISTINCT i.InvoiceId) AS order_count,
            SUM(i.Total) AS total_sales,
            COUNT(DISTINCT i.CustomerId) AS customer_count,
            SUM(ii.Quantity) AS items_sold
        FROM Invoice i
        JOIN InvoiceLine ii ON i.InvoiceId = ii.InvoiceId
        WHERE date(i.InvoiceDate) BETWEEN ? AND ?
        GROUP BY period
    )
    SELECT 
        period,
        order_count,
        total_sales,
        customer_count,
        items_sold,
        ROUND(total_sales / NULLIF(customer_count, 0), 2) AS avg_sale_per_customer,
        ROUND(total_sales / NULLIF(order_count, 0), 2) AS avg_order_value,
        ROUND(items_sold / NULLIF(order_count, 0), 2) AS avg_items_per_order,
        LAG(total_sales, 1) OVER (ORDER BY period) AS prev_period_sales,
        ROUND(
            ((total_sales - LAG(total_sales, 1) OVER (ORDER BY period)) / 
            NULLIF(LAG(total_sales, 1) OVER (ORDER BY period), 0)) * 100, 
            2
        ) AS sales_growth_percentage
    FROM sales_data
    ORDER BY period
    """
    
    return execute_query(query, (start_date, end_date))

def get_product_performance(
    category: str = None,
    min_sales: float = 0,
    min_quantity: int = 0
) -> List[Dict]:
    """
    Analyse la performance des produits.
    
    Args:
        category: Filtre par catégorie (optionnel)
        min_sales: Montant minimum des ventes pour filtrer
        min_quantity: Quantité minimale vendue pour filtrer
        
    Returns:
        Données de performance des produits
    """
    query = """
    WITH product_sales AS (
        SELECT 
            t.TrackId,
            t.Name AS track_name,
            ar.Name AS artist_name,
            al.Title AS album_title,
            g.Name AS genre,
            m.Name AS media_type,
            COUNT(DISTINCT i.InvoiceId) AS times_ordered,
            SUM(ii.Quantity) AS total_quantity,
            SUM(ii.UnitPrice * ii.Quantity) AS total_sales,
            COUNT(DISTINCT i.CustomerId) AS customer_count,
            MIN(i.InvoiceDate) AS first_sale_date,
            MAX(i.InvoiceDate) AS last_sale_date
        FROM Track t
        JOIN Album al ON t.AlbumId = al.AlbumId
        JOIN Artist ar ON al.ArtistId = ar.ArtistId
        JOIN Genre g ON t.GenreId = g.GenreId
        JOIN MediaType m ON t.MediaTypeId = m.MediaTypeId
        JOIN InvoiceLine ii ON t.TrackId = ii.TrackId
        JOIN Invoice i ON ii.InvoiceId = i.InvoiceId
        GROUP BY t.TrackId
        HAVING total_sales >= ? AND total_quantity >= ?
    )
    SELECT 
        TrackId,
        track_name,
        artist_name,
        album_title,
        genre,
        media_type,
        times_ordered,
        total_quantity,
        total_sales,
        customer_count,
        first_sale_date,
        last_sale_date,
        ROUND(total_sales / NULLIF(times_ordered, 0), 2) AS avg_sale_per_order,
        ROUND(total_quantity / NULLIF(times_ordered, 0), 2) AS avg_quantity_per_order,
        ROUND(total_sales / NULLIF(total_quantity, 0), 2) AS avg_price_per_unit
    FROM product_sales
    WHERE 1=1
    """
    
    params = [min_sales, min_quantity]
    
    if category:
        query += " AND genre = ?"
        params.append(category)
    
    query += " ORDER BY total_sales DESC"
    
    return execute_query(query, tuple(params))

def get_geographic_analysis() -> List[Dict]:
    """
    Analyse géographique des ventes.
    
    Returns:
        Données d'analyse géographique des ventes
    """
    query = """
    SELECT 
        c.Country,
        c.State,
        c.City,
        COUNT(DISTINCT c.CustomerId) AS customer_count,
        COUNT(DISTINCT i.InvoiceId) AS order_count,
        SUM(i.Total) AS total_sales,
        ROUND(SUM(i.Total) / COUNT(DISTINCT c.CustomerId), 2) AS sales_per_customer,
        ROUND(AVG(i.Total), 2) AS avg_order_value,
        MIN(i.InvoiceDate) AS first_order_date,
        MAX(i.InvoiceDate) AS last_order_date
    FROM Customer c
    JOIN Invoice i ON c.CustomerId = i.CustomerId
    GROUP BY c.Country, c.State, c.City
    HAVING order_count > 0
    ORDER BY total_sales DESC
    """
    
    return execute_query(query)
