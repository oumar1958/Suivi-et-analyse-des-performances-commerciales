import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord Chinook",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('data/chinook.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour exécuter des requêtes SQL
def run_query(query, params=None):
    conn = get_db_connection()
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Titre de l'application
st.title("🎵 Tableau de Bord Chinook")
st.markdown("---")

# Sélecteurs de dates
date_col1, date_col2 = st.columns(2)
with date_col1:
    start_date = st.date_input("Date de début", datetime(2013, 1, 1))
with date_col2:
    end_date = st.date_input("Date de fin", datetime(2013, 12, 31))

# Conversion des dates en format SQLite
def format_date_for_sql(date):
    return date.strftime('%Y-%m-%d')

# Requête pour les KPI
def get_kpis(start_date, end_date):
    query = """
    SELECT 
        COUNT(DISTINCT i.InvoiceId) as total_ventes,
        SUM(i.Total) as chiffre_affaires,
        COUNT(DISTINCT i.CustomerId) as clients_uniques,
        AVG(i.Total) as panier_moyen
    FROM invoices i
    WHERE date(i.InvoiceDate) BETWEEN ? AND ?
    """
    return run_query(query, (format_date_for_sql(start_date), format_date_for_sql(end_date)))

# Affichage des KPI
st.subheader("Indicateurs Clés")
kpi_data = get_kpis(start_date, end_date)

if not kpi_data.empty and not kpi_data['chiffre_affaires'].isnull().all():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ventes Totales", f"{int(kpi_data['total_ventes'].iloc[0])}" if not pd.isna(kpi_data['total_ventes'].iloc[0]) else "N/A")
    with col2:
        ca = kpi_data['chiffre_affaires'].iloc[0]
        st.metric("Chiffre d'Affaires", f"${ca:,.2f}" if pd.notna(ca) else "N/A")
    with col3:
        st.metric("Clients Uniques", f"{int(kpi_data['clients_uniques'].iloc[0])}" if not pd.isna(kpi_data['clients_uniques'].iloc[0]) else "N/A")
    with col4:
        panier = kpi_data['panier_moyen'].iloc[0]
        st.metric("Panier Moyen", f"${panier:.2f}" if pd.notna(panier) else "N/A")
else:
    st.warning("Aucune donnée trouvée pour la période sélectionnée.")

# Graphique des ventes par mois
def get_sales_by_month(start_date, end_date):
    query = """
    SELECT 
        strftime('%Y-%m', InvoiceDate) as mois,
        SUM(Total) as total_ventes
    FROM invoices
    WHERE date(InvoiceDate) BETWEEN ? AND ?
    GROUP BY mois
    ORDER BY mois
    """
    return run_query(query, (format_date_for_sql(start_date), format_date_for_sql(end_date)))

st.markdown("---")
st.subheader("Évolution des Ventes par Mois")
sales_data = get_sales_by_month(start_date, end_date)

if not sales_data.empty:
    fig = px.line(
        sales_data, 
        x='mois', 
        y='total_ventes',
        labels={'mois': 'Mois', 'total_ventes': 'Ventes ($)'},
        markers=True
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Meilleurs vendeurs
def get_top_sellers(start_date, end_date):
    query = """
    SELECT 
        e.FirstName || ' ' || e.LastName as employe,
        COUNT(i.InvoiceId) as nombre_ventes,
        SUM(i.Total) as total_ventes
    FROM invoices i
    JOIN customers c ON i.CustomerId = c.CustomerId
    JOIN employees e ON c.SupportRepId = e.EmployeeId
    WHERE date(i.InvoiceDate) BETWEEN ? AND ?
    GROUP BY e.EmployeeId
    ORDER BY total_ventes DESC
    LIMIT 5
    """
    return run_query(query, (format_date_for_sql(start_date), format_date_for_sql(end_date)))

st.markdown("---")
st.subheader("Top 5 des Vendeurs")
top_sellers = get_top_sellers(start_date, end_date)

if not top_sellers.empty:
    fig = px.bar(
        top_sellers, 
        x='employe', 
        y='total_ventes',
        labels={'employe': 'Employé', 'total_ventes': 'Ventes ($)'},
        color='total_ventes',
        color_continuous_scale='Blues'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Meilleurs clients
def get_top_customers(start_date, end_date):
    query = """
    SELECT 
        c.FirstName || ' ' || c.LastName as client,
        c.Country as pays,
        COUNT(i.InvoiceId) as nombre_achats,
        SUM(i.Total) as total_depense
    FROM customers c
    JOIN invoices i ON c.CustomerId = i.CustomerId
    WHERE date(i.InvoiceDate) BETWEEN ? AND ?
    GROUP BY c.CustomerId
    ORDER BY total_depense DESC
    LIMIT 10
    """
    return run_query(query, (format_date_for_sql(start_date), format_date_for_sql(end_date)))

st.markdown("---")
st.subheader("Top 10 des Clients")
top_customers = get_top_customers(start_date, end_date)

if not top_customers.empty:
    fig = px.bar(
        top_customers, 
        x='client', 
        y='total_depense',
        color='pays',
        labels={'client': 'Client', 'total_depense': 'Dépenses ($)', 'pays': 'Pays'},
        title="Dépenses totales par client"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Ventes par pays
def get_sales_by_country(start_date, end_date):
    query = """
    SELECT 
        c.Country as pays,
        COUNT(DISTINCT i.CustomerId) as clients_uniques,
        SUM(i.Total) as total_ventes
    FROM invoices i
    JOIN customers c ON i.CustomerId = c.CustomerId
    WHERE date(i.InvoiceDate) BETWEEN ? AND ?
    GROUP BY c.Country
    ORDER BY total_ventes DESC
    """
    return run_query(query, (format_date_for_sql(start_date), format_date_for_sql(end_date)))

st.markdown("---")
st.subheader("Ventes par Pays")
sales_by_country = get_sales_by_country(start_date, end_date)

if not sales_by_country.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            sales_by_country, 
            values='total_ventes', 
            names='pays',
            title='Répartition des ventes par pays',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            sales_by_country.sort_values('total_ventes', ascending=False),
            column_config={
                "pays": "Pays",
                "clients_uniques": "Clients Uniques",
                "total_ventes": st.column_config.NumberColumn(
                    "Ventes Total ($)",
                    format="$%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )

# Meilleurs produits
def get_top_products(start_date, end_date):
    query = """
    SELECT 
        t.Name as produit,
        ar.Name as artiste,
        g.Name as genre,
        COUNT(il.InvoiceLineId) as quantite_vendue,
        SUM(il.UnitPrice * il.Quantity) as chiffre_affaires
    FROM invoice_items il
    JOIN tracks t ON il.TrackId = t.TrackId
    JOIN albums al ON t.AlbumId = al.AlbumId
    JOIN artists ar ON al.ArtistId = ar.ArtistId
    JOIN genres g ON t.GenreId = g.GenreId
    JOIN invoices i ON il.InvoiceId = i.InvoiceId
    WHERE date(i.InvoiceDate) BETWEEN ? AND ?
    GROUP BY t.TrackId
    ORDER BY quantite_vendue DESC
    LIMIT 10
    """
    return run_query(query, (format_date_for_sql(start_date), format_date_for_sql(end_date)))

st.markdown("---")
st.subheader("Top 10 des Produits les Plus Vendus")
top_products = get_top_products(start_date, end_date)

if not top_products.empty:
    st.dataframe(
        top_products,
        column_config={
            "produit": "Produit",
            "artiste": "Artiste",
            "genre": "Genre",
            "quantite_vendue": "Quantité Vendue",
            "chiffre_affaires": st.column_config.NumberColumn(
                "Chiffre d'Affaires",
                format="$%.2f"
            )
        },
        hide_index=True,
        use_container_width=True
    )

# Style CSS personnalisé
st.markdown("""
    <style>
    .stMetricValue {
        font-size: 1.5rem !important;
    }
    .stMetricLabel {
        font-size: 1rem !important;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Pied de page
st.markdown("---")
st.markdown("*Tableau de bord créé avec Streamlit et la base de données Chinook*")
