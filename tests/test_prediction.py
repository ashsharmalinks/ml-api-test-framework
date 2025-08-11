# tests/test_prediction.py
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8000/v1/predict/titanic"

def test_valid_prediction(base_url):
    response = requests.post(base_url, json={"features": [3, 0, 22, 7.25]})
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_missing_features(base_url):
    response = requests.post(base_url, json={})
    assert response.status_code != 200

def test_invalid_datatype(base_url):
    response = requests.post(base_url, json={"features": "abc"})
    assert response.status_code != 200

def test_wrong_feature_count(base_url):
    response = requests.post(base_url, json={"features": [1, 2]})
    assert response.status_code != 200

def test_non_json_input(base_url):
    response = requests.post(base_url, data="just text")
    assert response.status_code != 200

def test_edge_values(base_url):
    response = requests.post(base_url, json={"features": [1, 1, 0.0, 0.0]})
    assert response.status_code == 200
    assert "prediction" in response.json()
