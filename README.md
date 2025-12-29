# 🎵 Tableau de Bord d'Analyse des Ventes Chinook

## 📋 Description

Ce projet est un tableau de bord interactif construit avec Streamlit qui permet d'analyser les données de vente de la base de données Chinook. Il offre une visualisation complète des performances commerciales avec des graphiques interactifs et des indicateurs clés de performance.

## ✨ Fonctionnalités Principales

- **Tableau de Bord Interactif** : Interface utilisateur intuitive et réactive
- **Indicateurs Clés de Performance** : Suivi en temps réel des métriques importantes
- **Analyses Avancées** :
  - 📈 Évolution des ventes dans le temps
  - 🏆 Classement des meilleurs vendeurs et produits
  - 🌍 Répartition géographique des ventes
  - 👥 Analyse du comportement client
- **Filtres Dynamiques** : Personnalisation des périodes d'analyse
- **Visualisations Interactives** : Graphiques dynamiques avec Plotly

## 🚀 Démarrage Rapide

1. **Cloner le dépôt**
   ```bash
   git clone [URL_DU_REPO]
   cd rapports_ventes_sql
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Accéder au tableau de bord**
   Ouvrez votre navigateur à l'adresse : `http://localhost:8501`

## 🛠️ Structure du Projet

```
rapports_ventes_sql/
├── data/
│   └── chinook.db         # Base de données SQLite
├── config/
│   ├── settings.py        # Paramètres de l'application
│   └── logging.conf       # Configuration des logs
├── src/                   # Code source principal
│   └── services/          # Logique métier
├── queries/               # Requêtes SQL
├── requirements.txt       # Dépendances Python
└── streamlit_app.py       # Application principale Streamlit
```

## 📊 Fonctionnalités Détaillées

### Indicateurs Clés
- Ventes totales
- Chiffre d'affaires
- Nombre de clients uniques
- Panier moyen

### Visualisations
- Graphique d'évolution des ventes mensuelles
- Classement des meilleurs vendeurs
- Top produits les plus vendus
- Répartition géographique des ventes
- Analyse des meilleurs clients

## � Prérequis

- Python 3.8+
- SQLite3
- Base de données Chinook (incluse dans `data/`)
- Bibliothèques Python (voir `requirements.txt`)

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Base de données Chinook pour les données de démonstration
- Streamlit pour l'interface utilisateur
- Plotly pour les visualisations interactives

## 🏗️ Structure du Projet

```
rapports_ventes_sql/
├── data/                   # Fichiers de données
│   └── chinook.db         # Base de données SQLite
├── src/                    # Code source
│   ├── __init__.py
│   ├── database/          # Gestion de la base de données
│   │   ├── __init__.py
│   │   ├── connection.py  # Gestion des connexions
│   │   └── queries/       # Requêtes SQL organisées
│   │       ├── __init__.py
│   │       ├── sales.py
│   │       ├── customers.py
│   │       └── reports.py
│   ├── models/            # Modèles de données
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   └── sales.py
│   ├── services/          # Logique métier
│   │   ├── __init__.py
│   │   ├── sales_service.py
│   │   └── report_service.py
│   └── utils/             # Utilitaires
│       ├── __init__.py
│       └── helpers.py
├── tests/                 # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── test_queries.py
│   └── test_services.py
├── config/                # Fichiers de configuration
│   ├── __init__.py
│   ├── settings.py
│   └── logging.conf
├── docs/                  # Documentation
│   ├── api.md
│   └── setup.md
├── scripts/               # Scripts utilitaires
│   ├── setup_database.py
│   └── generate_reports.py
├── .gitignore
├── requirements.txt
└── README.md
```
├── scripts/                # Scripts utilitaires
└── README.md               # Ce fichier
```

## Installation
1. Cloner le dépôt
2. Installer SQLite3 ou DB Browser for SQLite
3. Copier la base de données Chinook dans le dossier `data/`

## Utilisation
1. Ouvrir la base de données avec un client SQL
2. Exécuter les requêtes du dossier `queries/` selon vos besoins
3. Les résultats peuvent être exportés au format CSV ou PDF pour analyse

## Documentation
Consultez le dossier `docs/` pour :
- Le schéma de la base de données
- Le guide d'utilisation
- Les bonnes pratiques SQL

## Auteur
[Votre Nom] - [Votre Email]

## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
