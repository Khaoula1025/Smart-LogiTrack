# Taxi ETA Prediction Pipeline

## 📋 Description

Système complet de prédiction de durée de trajet (ETA) pour taxis urbains avec pipeline ETL distribué, Machine Learning et API sécurisée.

## 🏗️ Architecture

- **Airflow**: Orchestration du pipeline ETL
- **PySpark**: Traitement distribué des données
- **PostgreSQL**: Stockage des données Silver et prédictions
- **FastAPI**: API de prédiction sécurisée (JWT)
- **Docker Compose**: Déploiement de l'infrastructure

## 🚀 Quick Start

```bash
# Cloner le projet
git clone <repo-url>
cd taxi-eta-prediction

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# Lancer l'infrastructure
docker-compose up -d

# Accéder à Airflow
# http://localhost:8080
# User: airflow / Pass: airflow

# Accéder à l'API
# http://localhost:8000/docs
```

## 📊 Pipeline

1. **Bronze**: Ingestion des données brutes
2. **Silver**: Nettoyage et feature engineering
3. **ML**: Entraînement du modèle de prédiction
4. **API**: Exposition des prédictions

## 🔒 Authentification

L'API utilise JWT pour l'authentification. Voir `/docs` pour tester les endpoints.

## 📝 Documentation

- [Architecture](docs/architecture.md)
- [API Documentation](docs/api_documentation.md)
- [Rapport Technique](docs/rapport_technique.md)

## 🧪 Tests

```bash
# Tests unitaires
pytest api/tests/

# Tests d'intégration
pytest tests/integration/
```

## 📦 Livrables

- ✅ Pipeline Airflow (Bronze → Silver → ML)
- ✅ Modèle ML entraîné (model.pkl)
- ✅ API FastAPI avec JWT
- ✅ Endpoints Analytics avec SQL avancé
- ✅ Base PostgreSQL
- ✅ Tests Pytest
- ✅ Docker Compose

## 👥 Auteur

[Votre nom]

## 📅 Date

05/01/2026 - 10/01/2026
