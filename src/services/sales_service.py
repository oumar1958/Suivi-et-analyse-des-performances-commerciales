"""
Service de gestion des ventes.

Ce module fournit des méthodes pour interagir avec les données de vente
de la base de données Chinook.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path
import csv

from ..database.connection import execute_query, DatabaseManager
from ..models.sales import Sales
from ..models.customer import Customer

class SalesService:
    """Service pour la gestion des opérations liées aux ventes."""
    
    @staticmethod
    def get_sales_summary(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Récupère un résumé des ventes pour une période donnée.
        
        Args:
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Dictionnaire contenant les statistiques de vente
        """
        # Construction de la requête de base
        query = """
        SELECT 
            COUNT(DISTINCT i.InvoiceId) AS total_orders,
            COUNT(DISTINCT i.CustomerId) AS total_customers,
            SUM(i.Total) AS total_sales,
            AVG(i.Total) AS avg_order_value,
            MIN(i.Total) AS min_order_value,
            MAX(i.Total) AS max_order_value
        FROM Invoice i
        """
        
        # Ajout des filtres de date si spécifiés
        params = []
        if start_date and end_date:
            query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
            params.extend([start_date.isoformat(), end_date.isoformat()])
        
        # Exécution de la requête
        with DatabaseManager() as db:
            result = execute_query(query, tuple(params) if params else None, fetch='one')
        
        # Calcul des métriques supplémentaires
        if result and result['total_orders'] > 0:
            result['total_sales'] = float(result['total_sales'] or 0)
            result['avg_order_value'] = float(result['avg_order_value'] or 0)
            result['min_order_value'] = float(result['min_order_value'] or 0)
            result['max_order_value'] = float(result['max_order_value'] or 0)
        else:
            result = {
                'total_orders': 0,
                'total_customers': 0,
                'total_sales': 0.0,
                'avg_order_value': 0.0,
                'min_order_value': 0.0,
                'max_order_value': 0.0
            }
        
        return result
    
    @staticmethod
    def get_sales_trends(
        period: str = 'month',
        lookback_months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Analyse les tendances des ventes sur une période donnée.
        
        Args:
            period: Période d'analyse ('day', 'week', 'month', 'quarter', 'year')
            lookback_months: Nombre de mois en arrière pour l'analyse
            
        Returns:
            Liste de dictionnaires contenant les données de tendance
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
        
        with DatabaseManager() as db:
            return execute_query(query, (start_date.isoformat(), end_date.isoformat()))
    
    @staticmethod
    def get_top_selling_products(
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
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
            m.Name AS media_type,
            COUNT(DISTINCT i.InvoiceId) AS times_ordered,
            SUM(ii.Quantity) AS total_quantity,
            SUM(ii.UnitPrice * ii.Quantity) AS total_sales,
            ROUND(SUM(ii.UnitPrice * ii.Quantity) / SUM(ii.Quantity), 2) AS avg_price
        FROM Track t
        JOIN Album al ON t.AlbumId = al.AlbumId
        JOIN Artist ar ON al.ArtistId = ar.ArtistId
        JOIN Genre g ON t.GenreId = g.GenreId
        JOIN MediaType m ON t.MediaTypeId = m.MediaTypeId
        JOIN InvoiceLine ii ON t.TrackId = ii.TrackId
        JOIN Invoice i ON ii.InvoiceId = i.InvoiceId
        """
        
        params = []
        if start_date and end_date:
            query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
            params.extend([start_date.isoformat(), end_date.isoformat()])
        
        query += """
        GROUP BY t.TrackId
        ORDER BY total_sales DESC
        LIMIT ?
        """
        params.append(limit)
        
        with DatabaseManager() as db:
            return execute_query(query, tuple(params))
    
    @staticmethod
    def get_sales_by_geography(
        group_by: str = 'country',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyse les ventes par zone géographique.
        
        Args:
            group_by: Niveau de regroupement ('country', 'state', 'city')
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Liste des ventes groupées par zone géographique
        """
        if group_by not in ('country', 'state', 'city'):
            raise ValueError("Le regroupement doit être 'country', 'state' ou 'city'")
        
        # Sélection des champs de groupe en fonction du niveau de regroupement
        group_fields = ['c.Country']
        if group_by in ('state', 'city'):
            group_fields.append('c.State')
        if group_by == 'city':
            group_fields.append('c.City')
        
        group_clause = ', '.join(group_fields)
        
        query = f"""
        SELECT 
            {group_clause},
            COUNT(DISTINCT i.InvoiceId) AS order_count,
            COUNT(DISTINCT c.CustomerId) AS customer_count,
            SUM(i.Total) AS total_sales,
            ROUND(SUM(i.Total) / COUNT(DISTINCT c.CustomerId), 2) AS sales_per_customer,
            ROUND(AVG(i.Total), 2) AS avg_order_value
        FROM Invoice i
        JOIN Customer c ON i.CustomerId = c.CustomerId
        """
        
        params = []
        if start_date and end_date:
            query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
            params.extend([start_date.isoformat(), end_date.isoformat()])
        
        query += f"""
        GROUP BY {group_clause}
        HAVING order_count > 0
        ORDER BY total_sales DESC
        """
        
        with DatabaseManager() as db:
            return execute_query(query, tuple(params) if params else None)
    
    @staticmethod
    def export_sales_report(
        output_path: Union[str, Path],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        format: str = 'csv'
    ) -> str:
        """
        Exporte un rapport des ventes au format spécifié.
        
        Args:
            output_path: Chemin du fichier de sortie
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            format: Format d'export ('csv' ou 'json')
            
        Returns:
            Chemin du fichier généré
        """
        # Récupération des données de vente
        query = """
        SELECT 
            i.InvoiceId,
            i.InvoiceDate,
            c.FirstName || ' ' || c.LastName AS CustomerName,
            c.Country,
            c.City,
            i.Total,
            COUNT(il.InvoiceLineId) AS items_count,
            GROUP_CONCAT(t.Name, '|') AS items
        FROM Invoice i
        JOIN Customer c ON i.CustomerId = c.CustomerId
        JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
        JOIN Track t ON il.TrackId = t.TrackId
        """
        
        params = []
        if start_date and end_date:
            query += " WHERE date(i.InvoiceDate) BETWEEN ? AND ?"
            params.extend([start_date.isoformat(), end_date.isoformat()])
        
        query += """
        GROUP BY i.InvoiceId
        ORDER BY i.InvoiceDate DESC
        """
        
        with DatabaseManager() as db:
            sales_data = execute_query(query, tuple(params) if params else None)
        
        # Création du répertoire de sortie si nécessaire
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export dans le format demandé
        if format.lower() == 'csv':
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if sales_data:
                    # Écriture de l'en-tête
                    fieldnames = list(sales_data[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Écriture des données
                    writer.writerows(sales_data)
        else:
            raise ValueError(f"Format non pris en charge: {format}")
        
        return str(output_path.absolute())
