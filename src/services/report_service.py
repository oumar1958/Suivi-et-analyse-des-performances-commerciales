"""
Service de génération de rapports.

Ce module fournit des méthodes pour générer différents types de rapports
d'analyse des ventes à partir des données de la base de données Chinook.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ..database.connection import execute_query
from ..models.sales import Sales

class ReportService:
    """Service pour la génération de rapports d'analyse des ventes."""
    
    @staticmethod
    def generate_sales_trend_report(
        period: str = 'month',
        lookback_months: int = 12
    ) -> Dict[str, Any]:
        """
        Génère un rapport d'analyse des tendances des ventes.
        
        Args:
            period: Période d'analyse ('day', 'week', 'month', 'quarter', 'year')
            lookback_months: Nombre de mois en arrière pour l'analyse
            
        Returns:
            Dictionnaire contenant les données du rapport
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_months*30)
        
        # Récupération des données de tendance
        sales_data = Sales.get_sales_by_period(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            group_by=period
        )
        
        # Calcul des métriques clés
        total_sales = sum(item['total_sales'] for item in sales_data) if sales_data else 0
        avg_order_value = sum(item['total_sales'] for item in sales_data) / len(sales_data) if sales_data else 0
        
        # Préparation des données pour le graphique
        periods = [item['period'] for item in sales_data]
        sales_values = [item['total_sales'] for item in sales_data]
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_sales': round(total_sales, 2),
            'avg_order_value': round(avg_order_value, 2),
            'periods': periods,
            'sales_values': sales_values,
            'data': sales_data
        }
    
    @staticmethod
    def generate_product_performance_report(
        category: Optional[str] = None,
        min_sales: float = 0,
        min_quantity: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Génère un rapport d'analyse de la performance des produits.
        
        Args:
            category: Catégorie de produit à filtrer (optionnel)
            min_sales: Montant minimum des ventes pour filtrer
            min_quantity: Quantité minimale vendue pour filtrer
            limit: Nombre maximum de produits à inclure
            
        Returns:
            Dictionnaire contenant les données du rapport
        """
        # Récupération des données des produits
        products = Sales.get_top_selling_products(limit=limit)
        
        # Filtrage des produits selon les critères
        filtered_products = [
            p for p in products 
            if p['total_sales'] >= min_sales and p['total_quantity'] >= min_quantity
            and (not category or p['genre'] == category)
        ]
        
        # Calcul des métriques globales
        total_sales = sum(p['total_sales'] for p in filtered_products)
        total_quantity = sum(p['total_quantity'] for p in filtered_products)
        
        return {
            'category': category,
            'total_products': len(filtered_products),
            'total_sales': round(total_sales, 2),
            'total_quantity': total_quantity,
            'products': filtered_products
        }
    
    @staticmethod
    def generate_geographic_analysis_report() -> Dict[str, Any]:
        """
        Génère un rapport d'analyse géographique des ventes.
        
        Returns:
            Dictionnaire contenant les données du rapport géographique
        """
        # Récupération des données géographiques
        geo_data = execute_query("""
            SELECT 
                c.Country,
                COUNT(DISTINCT c.CustomerId) AS customer_count,
                COUNT(DISTINCT i.InvoiceId) AS order_count,
                SUM(i.Total) AS total_sales,
                ROUND(SUM(i.Total) / COUNT(DISTINCT c.CustomerId), 2) AS sales_per_customer
            FROM Customer c
            JOIN Invoice i ON c.CustomerId = i.CustomerId
            GROUP BY c.Country
            HAVING order_count > 0
            ORDER BY total_sales DESC
        """)
        
        # Calcul des métriques globales
        total_countries = len(geo_data)
        total_sales = sum(item['total_sales'] for item in geo_data)
        
        return {
            'total_countries': total_countries,
            'total_sales': round(total_sales, 2),
            'countries': geo_data,
            'top_countries': geo_data[:5] if geo_data else []
        }
    
    @staticmethod
    def generate_customer_analysis_report() -> Dict[str, Any]:
        """
        Génère un rapport d'analyse des clients.
        
        Returns:
            Dictionnaire contenant les données d'analyse des clients
        """
        # Récupération des données des clients
        customers = execute_query("""
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
            GROUP BY c.CustomerId
            ORDER BY total_spent DESC
        """)
        
        # Calcul des métriques clés
        total_customers = len(customers)
        total_sales = sum(c['total_spent'] for c in customers)
        avg_order_value = sum(c['total_spent'] for c in customers) / sum(c['order_count'] for c in customers) if customers else 0
        
        # Top clients
        top_customers = customers[:5] if customers else []
        
        # Récupérer la distribution des clients par pays
        country_distribution = execute_query("""
            SELECT Country, COUNT(*) AS customer_count
            FROM Customer
            GROUP BY Country
            ORDER BY customer_count DESC
        """)
        
        # Créer le dictionnaire de distribution par pays
        by_country = {}
        for c in country_distribution:
            by_country[c['Country']] = c['customer_count']
        
        # Retourner le résultat final
        return {
            'total_customers': total_customers,
            'total_sales': round(total_sales, 2),
            'avg_order_value': round(avg_order_value, 2),
            'top_customers': top_customers,
            'customer_distribution': {
                'by_country': by_country
            }
        }
    
    @staticmethod
    def export_report_to_csv(report_data: Dict[str, Any], output_path: Union[str, Path]) -> str:
        """
        Exporte les données du rapport vers un fichier CSV.
        
        Args:
            report_data: Données du rapport à exporter
            output_path: Chemin du fichier de sortie
            
        Returns:
            Chemin du fichier généré
        """
        # Conversion des données en DataFrame
        if 'products' in report_data:
            df = pd.DataFrame(report_data['products'])
        elif 'countries' in report_data:
            df = pd.DataFrame(report_data['countries'])
        elif 'data' in report_data:
            df = pd.DataFrame(report_data['data'])
        else:
            raise ValueError("Format de données de rapport non pris en charge")
        
        # Création du répertoire de sortie si nécessaire
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export en CSV
        df.to_csv(output_path, index=False)
        return str(output_path.absolute())
    
    @staticmethod
    def plot_sales_trend(report_data: Dict[str, Any], output_path: Union[str, Path]) -> str:
        """
        Génère un graphique de tendance des ventes.
        
        Args:
            report_data: Données du rapport de tendance
            output_path: Chemin de sortie pour l'image
            
        Returns:
            Chemin du fichier d'image généré
        """
        if 'periods' not in report_data or 'sales_values' not in report_data:
            raise ValueError("Données de tendance des ventes manquantes")
        
        # Configuration du style
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(12, 6))
        
        # Création du graphique
        ax = sns.lineplot(
            x=report_data['periods'],
            y=report_data['sales_values'],
            marker='o',
            linewidth=2.5
        )
        
        # Personnalisation du graphique
        plt.title(f"Tendance des ventes par {report_data['period']}", fontsize=14, pad=20)
        plt.xlabel('Période', fontsize=12)
        plt.ylabel('Ventes totales', fontsize=12)
        plt.xticks(rotation=45)
        
        # Ajustement des marges
        plt.tight_layout()
        
        # Enregistrement du graphique
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_path.absolute())
