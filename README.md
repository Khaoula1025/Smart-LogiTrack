# 🚕 Taxi ETA Prediction - End-to-End ML Pipeline

## 📋 Description

Système complet de prédiction du temps d'arrivée (ETA) pour les trajets de taxi urbains, utilisant un pipeline distribué de traitement de données et Machine Learning.

## 🎯 Objectifs

- Pipeline ETL distribué avec Apache Airflow et PySpark
- Nettoyage et enrichissement des données (architecture Bronze → Silver)
- Modèle de régression ML pour estimer la durée des trajets
- API REST sécurisée (JWT) pour servir les prédictions
- Analytics avancés avec requêtes SQL
- Monitoring et logging des prédictions

## 🏗️ Architecture

```
Bronze (Raw Data) → Silver (Clean Data) → ML Model → FastAPI → Predictions
```

## 📁 Structure du Projet

```
TAXI-ETA-PREDICTION/
├── airflow/              # DAGs et configuration Airflow
├── app/                  # Application FastAPI
│   ├── api/
│   │   └── v1/          # Endpoints API version 1
│   │       ├── __init__.py
│   │       └── deps.py
│   ├── core/            # Configuration et logique métier
│   │   ├── __init__.py
│   │   ├── ml_model.py  # Gestion du modèle ML
│   │   └── security.py  # Authentification JWT
│   ├── db/              # Gestion base de données
│   │   ├── __init__.py
│   │   └── session.py
│   ├── models/          # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── eta_predictions.py
│   │   └── user.py
│   └── schemas/         # Schémas Pydantic
│       ├── __init__.py
│       └── auth.py
├── dags/                # DAGs Airflow
├── data/
│   ├── bronze/          # Données brutes
│   │   └── dataset.parquet
│   ├── raw/             # Données sources
│   └── silver/          # Données nettoyées
├── docs/                # Documentation
├── libs/                # Bibliothèques personnalisées
├── logs/                # Logs d'exécution
├── notebooks/           # Notebooks d'exploration
├── plugins/             # Plugins Airflow
├── postgres/            # Scripts PostgreSQL
├── scripts/             # Scripts utilitaires
├── spark/               # Jobs PySpark
├── tests/               # Tests unitaires
├── docker-compose.yml   # Configuration Docker
├── requirements.txt     # Dépendances Python
└── README.md
```

## 🚀 Technologies

- **Orchestration**: Apache Airflow
- **Processing**: PySpark
- **Database**: PostgreSQL
- **ML**: Scikit-learn
- **API**: FastAPI
- **Auth**: JWT (JSON Web Tokens)
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest

## 📊 Dataset - NYC Taxi Trips

**Colonnes principales:**
- `VendorID`: Identifiant du fournisseur (1 ou 2)
- `tpep_pickup_datetime`: Date/heure de départ
- `tpep_dropoff_datetime`: Date/heure d'arrivée
- `passenger_count`: Nombre de passagers
- `trip_distance`: Distance en miles
- `PULocationID` / `DOLocationID`: Zones de départ/arrivée
- `payment_type`: Type de paiement (0=Cash, 1=Card, etc.)
- `fare_amount`, `total_amount`: Montants

**Target**: `duration_minutes` = dropoff_datetime - pickup_datetime

## 🔧 Installation

### Prérequis
- Docker & Docker Compose
- Python 3.9+
- 8GB RAM minimum

### Démarrage

```bash
# Cloner le repository
git clone <repository-url>
cd TAXI-ETA-PREDICTION

# Copier le fichier d'environnement
cp .env.example .env

# Démarrer les services
docker-compose up -d

# Initialiser la base de données
docker-compose exec postgres bash /docker-entrypoint-initdb.d/init-db.sh
```

### Accès aux services

- **Airflow UI**: http://localhost:8080 (admin/admin)
- **FastAPI Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432 (user: postgres)

## 📈 Pipeline de Données (DAG Airflow)

1. **Tâche 1**: Téléchargement du dataset
2. **Tâche 2**: Stockage Bronze (données brutes)
3. **Tâche 3**: Nettoyage et Feature Engineering → Stockage Silver
4. **Tâche 4**: Entraînement du modèle ML
5. **Tâche 5** (Bonus): Logging des prédictions

### Feature Engineering

**Features temporelles générées:**
- `pickup_hour`: Heure de départ (0-23)
- `day_of_week`: Jour de la semaine (0-6)
- `month`: Mois (1-12)

**Règles de nettoyage:**
- Distance: 0 < distance ≤ 200 miles
- Durée: duration > 0 minutes
- Passagers: passenger_count > 0

## 🔌 API Endpoints

### Authentification

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}

Response: { "access_token": "...", "token_type": "bearer" }
```

### Prédiction

```bash
POST /predict
Authorization: Bearer <token>
Content-Type: application/json

{
  "trip_distance": 5.2,
  "passenger_count": 2,
  "pickup_hour": 14,
  "day_of_week": 3,
  "PULocationID": 142,
  "DOLocationID": 236
}

Response: { "estimated_duration": 18.5 }
```

### Analytics

#### Durée moyenne par heure
```bash
GET /analytics/avg-duration-by-hour
Authorization: Bearer <token>

Response: [
  { "pickup_hour": 8, "avg_duration": 18.4 },
  { "pickup_hour": 9, "avg_duration": 22.1 }
]
```

#### Analyse par type de paiement
```bash
GET /analytics/payment-analysis
Authorization: Bearer <token>

Response: [
  {
    "payment_type": 1,
    "total_trips": 125430,
    "avg_duration": 21.6
  }
]
```

## 🗄️ Base de Données

### Tables PostgreSQL

**`silver_taxi_trips`**: Données nettoyées pour ML
- Colonnes nettoyées et features temporelles
- Prêt pour entraînement et analytics

**`eta_predictions`**: Logs des prédictions
- Timestamp, features, prédiction, version du modèle
- Pour monitoring et analyse de performance

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install -r requirements.txt

# Lancer les tests
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html
```

## 📝 Métriques du Modèle

Le modèle est évalué avec:
- **RMSE** (Root Mean Square Error)
- **MAE** (Mean Absolute Error)
- **R² Score**

Métriques sauvegardées dans `logs/model_metrics.json`

## 🔐 Sécurité

- Authentification JWT pour tous les endpoints protégés
- Variables d'environnement pour secrets (.env)
- Validation des entrées avec Pydantic
- Rate limiting (à configurer)

## 📦 Dépendances Principales

```
fastapi>=0.104.0
pyspark>=3.5.0
apache-airflow>=2.7.0
scikit-learn>=1.3.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
pyjwt>=2.8.0
pytest>=7.4.0
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 👥 Auteurs

Projet développé dans le cadre d'une formation en Data Engineering et Machine Learning.

## 📞 Support

Pour toute question ou problème:
- Ouvrir une issue sur GitHub
- Consulter la documentation dans `/docs`

---

**Période de développement**: 05/01/2026 - 16/01/2026