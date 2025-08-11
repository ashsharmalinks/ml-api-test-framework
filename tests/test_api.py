# tests/test_api.py
import requests

base_url = "http://127.0.0.1:8000/v1/predict/titanic"   # add the model name

def test_prediction():
    # Option A: send a dict (recommended)
    payload = {"features": {"Pclass": 3, "Sex": 0, "Age": 22, "Fare": 7.25}}
    # Option B: send a list (must match training order):
    # payload = {"features": [3, 0, 22, 7.25]}

    r = requests.post(f"{base_url}", json=payload)
    # print for debug
    print("Status:", r.status_code)
    print("Body:", r.text)

    assert r.status_code == 200, f"API error: {r.text}"
    data = r.json()
    assert "prediction" in data
    assert data["prediction"] in [0, 1]
