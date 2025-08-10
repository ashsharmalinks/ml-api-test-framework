from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "titanic_model.pkl")
model = joblib.load(MODEL_PATH)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    features = data.get("features")  # e.g., [3, 0, 22, 7.25]
    prediction = model.predict([features])
    return jsonify({"prediction": int(prediction[0])})

# 🔥 THIS PART IS REQUIRED
if __name__ == "__main__":
    app.run(debug=True)
