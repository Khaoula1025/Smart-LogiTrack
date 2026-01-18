import pytest
from fastapi.testclient import TestClient
import os

from app.main import app


client = TestClient(app)

MODEL_PATH = "notebooks/models/GradientBoostedTrees_model"
def test_model_is_loaded():
    from app.api.v1.endpoints import model
    # Vérifier que le chemin du modèle existe
    assert os.path.exists(MODEL_PATH), f"Le modèle n'existe pas à {MODEL_PATH}"
    # Vérifier que le modèle est chargé en mémoire
    assert model is not None, "Le modèle n'est pas chargé en mémoire" 
    # Vérifier que c'est bien un PipelineModel
    from pyspark.ml import PipelineModel
    assert isinstance(model, PipelineModel), "Le modèle n'est pas un PipelineModel"

def test_prediction_endpoint():
    # Étape 1: Se connecter avec l'utilisateur de test
    login_data = {
        "identifier": "testuser",
        "password": "testpass123"
    }
    
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200, f"Échec login: {login_response.text}"
    # Étape 2: Récupérer le cookie access_token
    cookies = login_response.cookies
    assert "access_token" in cookies, "Cookie access_token manquant"
    
    access_token = cookies.get("access_token")
    # Étape 3: Préparer des données de trajet valides
    trip_data = {
        "passenger_count": 2,
        "trip_distance": 5.2,
        "RatecodeID": 1,
        "fare_amount": 15.5,
        "tip_amount": 3.0,
        "tolls_amount": 0.0,
        "Airport_fee": 0.0,
        "pickup_hour": 14
    }
    
    # Étape 4: Faire la prédiction avec le cookie
    response = client.post(
        "/predict", 
        json=trip_data,
        cookies={"access_token": access_token}
    )
    
    # Étape 5: Vérifier la réponse
    assert response.status_code == 200, f"Erreur API: {response.status_code} - {response.text}"
    


