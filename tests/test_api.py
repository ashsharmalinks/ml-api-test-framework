import requests

url = "http://127.0.0.1:5000/predict"
payload = {
    "features": [3, 0, 22, 7.25]  # [Pclass, Sex, Age, Fare]
}

response = requests.post(url, json=payload)
print("Prediction:", response.json())
