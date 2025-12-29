#!/usr/bin/env python3
"""
Tableau de bord interactif pour l'analyse des ventes Chinook
"""
import dash
from dash import dcc, html, Input, Output, dash_table, no_update
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os
from pathlib import Path

# Configuration
DB_PATH = 'data/chinook.db'

# Initialisation de l'application Dash
app = dash.Dash(__name__, title="Tableau de Bord des Ventes")
server = app.server  # Nécessaire pour le déploiement

# Mise en page du tableau de bord
app.layout = html.Div([
    html.H1("Tableau de Bord des Ventes Chinook", className="header-title"),
    
    # Filtres
    html.Div([
        html.Div([
            html.Label("Période"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed='2009-01-01',
                max_date_allowed='2013-12-31',
                start_date='2013-01-01',
                end_date='2013-12-31'
            )
        ], className="filter-item"),
        
        html.Div([
            html.Label("Pays"),
            dcc.Dropdown(
                id='country-dropdown',
                multi=True,
                placeholder="Sélectionnez un ou plusieurs pays"
            )
        ], className="filter-item"),
    ], className="filters"),
    
    # KPI
    html.Div([
        html.Div([
            html.Div(id='total-sales-kpi', className="kpi-value"),
            html.Div("Chiffre d'affaires", className="kpi-label")
        ], className="kpi"),
        
        html.Div([
            html.Div(id='total-orders-kpi', className="kpi-value"),
            html.Div("Commandes", className="kpi-label")
        ], className="kpi"),
        
        html.Div([
            html.Div(id='avg-order-value-kpi', className="kpi-value"),
            html.Div("Panier moyen", className="kpi-label")
        ], className="kpi"),
        
        html.Div([
            html.Div(id='customer-count-kpi', className="kpi-value"),
            html.Div("Clients uniques", className="kpi-label")
        ], className="kpi"),
    ], className="kpi-container"),
    
    # Graphiques principaux
    html.Div([
        dcc.Graph(id='sales-trend', className="chart"),
        dcc.Graph(id='sales-by-country', className="chart")
    ], className="row"),
    
    html.Div([
        dcc.Graph(id='top-products', className="chart"),
        dcc.Graph(id='sales-by-employee', className="chart")
    ], className="row"),
    
    # Tableau des dernières commandes
    html.Div([
        html.H3("Dernières Commandes"),
        dash_table.DataTable(
            id='recent-orders',
            page_size=5,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], className="recent-orders"),
    
    # Pied de page
    html.Div([
        html.P("Dernière mise à jour: " + datetime.now().strftime("%Y-%m-%d %H:%M")),
        html.P("© 2025 Tableau de Bord des Ventes - Tous droits réservés")
    ], className="footer")
])

# Fonction pour exécuter les requêtes SQL
def run_query(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()

# Mise à jour des options du filtre de pays
@app.callback(
    Output('country-dropdown', 'options'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_country_dropdown(start_date, end_date):
    query = """
    SELECT DISTINCT BillingCountry as value, BillingCountry as label 
    FROM Invoice
    WHERE InvoiceDate BETWEEN ? AND ?
    ORDER BY BillingCountry
    """
    params = (start_date, end_date)
    df = run_query(query, params)
    return df.to_dict('records')

# Mise à jour des KPI
@app.callback(
    [Output('total-sales-kpi', 'children'),
     Output('total-orders-kpi', 'children'),
     Output('avg-order-value-kpi', 'children'),
     Output('customer-count-kpi', 'children')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('country-dropdown', 'value')]
)
def update_kpis(start_date, end_date, countries):
    # Construction de la requête en fonction des filtres
    query = """
    SELECT 
        ROUND(SUM(Total), 2) as total_sales,
        COUNT(DISTINCT InvoiceId) as total_orders,
        ROUND(SUM(Total) / COUNT(DISTINCT CustomerId), 2) as avg_order_value,
        COUNT(DISTINCT CustomerId) as customer_count
    FROM Invoice
    WHERE InvoiceDate BETWEEN ? AND ?
    """
    
    params = [start_date, end_date]
    
    # Ajout du filtre par pays si sélectionné
    if countries and len(countries) > 0:
        placeholders = ','.join(['?'] * len(countries))
        query += f" AND BillingCountry IN ({placeholders})"
        params.extend(countries)
    
    df = run_query(query, params)
    
    if not df.empty:
        return (
            f"${df['total_sales'].iloc[0]:,.2f}",
            f"{df['total_orders'].iloc[0]:,}",
            f"${df['avg_order_value'].iloc[0]:,.2f}",
            f"{df['customer_count'].iloc[0]:,}"
        )
    return "$0.00", "0", "$0.00", "0"

# Mise à jour du graphique des ventes par mois
@app.callback(
    Output('sales-trend', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('country-dropdown', 'value')]
)
def update_sales_trend(start_date, end_date, countries):
    query = """
    SELECT 
        strftime('%Y-%m', InvoiceDate) as month,
        SUM(Total) as total_sales,
        COUNT(DISTINCT InvoiceId) as order_count
    FROM Invoice
    WHERE InvoiceDate BETWEEN ? AND ?
    """
    
    params = [start_date, end_date]
    
    if countries and len(countries) > 0:
        placeholders = ','.join(['?'] * len(countries))
        query += f" AND BillingCountry IN ({placeholders})"
        params.extend(countries)
    
    query += " GROUP BY strftime('%Y-%m', InvoiceDate) ORDER BY month"
    
    df = run_query(query, params)
    
    fig = px.line(
        df, 
        x='month', 
        y='total_sales',
        title='Évolution des Ventes par Mois',
        labels={'month': 'Mois', 'total_sales': 'Ventes ($)'}
    )
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode='x unified')
    
    return fig

# Mise à jour du graphique des ventes par pays
@app.callback(
    Output('sales-by-country', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_sales_by_country(start_date, end_date):
    query = """
    SELECT 
        BillingCountry as country,
        SUM(Total) as total_sales,
        COUNT(DISTINCT InvoiceId) as order_count
    FROM Invoice
    WHERE InvoiceDate BETWEEN ? AND ?
    GROUP BY BillingCountry
    ORDER BY total_sales DESC
    """
    
    df = run_query(query, [start_date, end_date])
    
    fig = px.bar(
        df,
        x='country',
        y='total_sales',
        title='Ventes par Pays',
        labels={'country': 'Pays', 'total_sales': 'Ventes ($)'}
    )
    
    return fig

# Mise à jour du graphique des meilleurs produits
@app.callback(
    Output('top-products', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_top_products(start_date, end_date):
    query = """
    SELECT 
        t.Name as track_name,
        ar.Name as artist_name,
        SUM(il.Quantity) as quantity_sold,
        SUM(il.UnitPrice * il.Quantity) as revenue
    FROM InvoiceLine il
    JOIN Track t ON il.TrackId = t.TrackId
    JOIN Album al ON t.AlbumId = al.AlbumId
    JOIN Artist ar ON al.ArtistId = ar.ArtistId
    JOIN Invoice i ON il.InvoiceId = i.InvoiceId
    WHERE i.InvoiceDate BETWEEN ? AND ?
    GROUP BY t.TrackId
    ORDER BY revenue DESC
    LIMIT 10
    """
    
    df = run_query(query, [start_date, end_date])
    df['track_artist'] = df['track_name'] + ' - ' + df['artist_name']
    
    fig = px.bar(
        df,
        x='revenue',
        y='track_artist',
        orientation='h',
        title='Top 10 des Produits par Chiffre d\'Affaires',
        labels={'revenue': 'Chiffre d\'affaires ($)', 'track_artist': 'Morceau - Artiste'}
    )
    
    return fig

# Mise à jour du graphique des ventes par employé
@app.callback(
    Output('sales-by-employee', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_sales_by_employee(start_date, end_date):
    query = """
    SELECT 
        e.FirstName || ' ' || e.LastName as employee_name,
        e.Title as title,
        SUM(i.Total) as total_sales,
        COUNT(DISTINCT i.InvoiceId) as order_count
    FROM Employee e
    JOIN Customer c ON e.EmployeeId = c.SupportRepId
    JOIN Invoice i ON c.CustomerId = i.CustomerId
    WHERE i.InvoiceDate BETWEEN ? AND ?
    GROUP BY e.EmployeeId
    ORDER BY total_sales DESC
    """
    
    df = run_query(query, [start_date, end_date])
    
    fig = px.pie(
        df,
        values='total_sales',
        names='employee_name',
        title='Répartition des Ventes par Employé',
        hover_data=['title'],
        labels={'employee_name': 'Employé', 'total_sales': 'Ventes ($)'}
    )
    
    return fig

# Mise à jour du tableau des dernières commandes
@app.callback(
    Output('recent-orders', 'data'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_recent_orders(start_date, end_date):
    query = """
    SELECT 
        i.InvoiceId as id_commande,
        i.InvoiceDate as date_commande,
        c.FirstName || ' ' || c.LastName as client,
        c.Country as pays,
        i.Total as montant,
        e.FirstName || ' ' || e.LastName as vendeur
    FROM Invoice i
    JOIN Customer c ON i.CustomerId = c.CustomerId
    JOIN Employee e ON c.SupportRepId = e.EmployeeId
    WHERE i.InvoiceDate BETWEEN ? AND ?
    ORDER BY i.InvoiceDate DESC
    LIMIT 10
    """
    
    df = run_query(query, [start_date, end_date])
    
    # Formatage des dates et des montants pour l'affichage
    if not df.empty:
        df['date_commande'] = pd.to_datetime(df['date_commande']).dt.strftime('%Y-%m-%d %H:%M')
        df['montant'] = df['montant'].apply(lambda x: f"${x:,.2f}")
    
    return df.to_dict('records')

# Styles CSS
app.layout = html.Div([
    # En-tête
    html.H1("Tableau de Bord des Ventes Chinook", className="header-title"),
    
    # Filtres
    html.Div([
        html.Div([
            html.Label("Période"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed='2009-01-01',
                max_date_allowed='2013-12-31',
                start_date='2013-01-01',
                end_date='2013-12-31'
            )
        ], className="filter-item"),
        
        html.Div([
            html.Label("Pays"),
            dcc.Dropdown(
                id='country-dropdown',
                multi=True,
                placeholder="Sélectionnez un ou plusieurs pays"
            )
        ], className="filter-item"),
    ], className="filters"),
    
    # KPI
    html.Div([
        html.Div([
            html.Div(id='total-sales-kpi', className="kpi-value"),
            html.Div("Chiffre d'affaires", className="kpi-label")
        ], className="kpi"),
        
        html.Div([
            html.Div(id='total-orders-kpi', className="kpi-value"),
            html.Div("Commandes", className="kpi-label")
        ], className="kpi"),
        
        html.Div([
            html.Div(id='avg-order-value-kpi', className="kpi-value"),
            html.Div("Panier moyen", className="kpi-label")
        ], className="kpi"),
        
        html.Div([
            html.Div(id='customer-count-kpi', className="kpi-value"),
            html.Div("Clients uniques", className="kpi-label")
        ], className="kpi"),
    ], className="kpi-container"),
    
    # Graphiques principaux
    html.Div([
        dcc.Graph(id='sales-trend', className="chart"),
        dcc.Graph(id='sales-by-country', className="chart")
    ], className="row"),
    
    html.Div([
        dcc.Graph(id='top-products', className="chart"),
        dcc.Graph(id='sales-by-employee', className="chart")
    ], className="row"),
    
    # Tableau des dernières commandes
    html.Div([
        html.H3("Dernières Commandes"),
        dash_table.DataTable(
            id='recent-orders',
            page_size=5,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], className="recent-orders"),
    
    # Pied de page
    html.Div([
        html.P("Dernière mise à jour: " + datetime.now().strftime("%Y-%m-%d %H:%M")),
        html.P("© 2025 Tableau de Bord des Ventes - Tous droits réservés")
    ], className="footer"),
    
    # Styles CSS
    html.Link(
        rel='stylesheet',
        href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    )
])

# Ajout des styles CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Tableau de Bord des Ventes Chinook</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-color: #2c3e50;
                --secondary-color: #3498db;
                --background-color: #f8f9fa;
                --card-bg: #ffffff;
                --text-color: #333333;
                --border-color: #e1e4e8;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: var(--background-color);
                color: var(--text-color);
            }
            
            .header-title {
                text-align: center;
                color: var(--primary-color);
                margin: 20px 0;
                padding-bottom: 15px;
                border-bottom: 2px solid var(--border-color);
            }
            
            .filters {
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 20px;
                margin: 20px 0;
                padding: 15px;
                background-color: var(--card-bg);
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .filter-item {
                flex: 1;
                min-width: 200px;
            }
            
            .kpi-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .kpi {
                background-color: var(--card-bg);
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .kpi:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            
            .kpi-value {
                font-size: 24px;
                font-weight: bold;
                color: var(--secondary-color);
                margin-bottom: 5px;
            }
            
            .kpi-label {
                font-size: 14px;
                color: #666;
            }
            
            .row {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin: 20px 0;
            }
            
            .chart {
                flex: 1 1 45%;
                min-width: 300px;
                background-color: var(--card-bg);
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .recent-orders {
                margin: 20px 0;
                background-color: var(--card-bg);
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .footer {
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                color: #666;
                font-size: 14px;
                border-top: 1px solid var(--border-color);
            }
            
            @media (max-width: 768px) {
                .filters {
                    flex-direction: column;
                }
                
                .filter-item {
                    width: 100%;
                }
                
                .kpi-container {
                    grid-template-columns: 1fr 1fr;
                }
                
                .chart {
                    flex: 1 1 100%;
                }
            }
            
            @media (max-width: 480px) {
                .kpi-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Configuration du serveur
app.config.suppress_callback_exceptions = True

if __name__ == '__main__':
    # Vérification de l'existence de la base de données
    if not os.path.exists(DB_PATH):
        print(f"Erreur: La base de données {DB_PATH} est introuvable.")
        print("Veuillez placer le fichier de base de données dans le dossier 'data/'.")
    else:
        # Création du dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)
        
        # Lancement du tableau de bord sur le port 8052
        port = 8052
        print("Démarrage du tableau de bord...")
        print(f"Ouvrez votre navigateur à l'adresse : http://127.0.0.1:{port}/")
        app.run(debug=True, port=port, host='0.0.0.0')
