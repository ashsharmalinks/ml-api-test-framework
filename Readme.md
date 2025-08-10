
ML API Test Framework – Step-by-Step Execution Guide
====================================================

✅ Prerequisites:
- Python 3.10 installed (⚠️ not 3.13)
- Git, pip, and virtualenv available

----------------------------------------------------
1. 📁 Clone or Navigate to the Project
----------------------------------------------------

cd C:/your/folder/path

----------------------------------------------------
2. 🐍 Create and Activate Virtual Environment
----------------------------------------------------

python -m venv venv
venv\Scripts\activate               # Windows
# OR
source venv/bin/activate             # macOS/Linux

----------------------------------------------------
3. 📦 Install All Required Packages
----------------------------------------------------

pip install --upgrade pip
pip install -r requirements.txt

(Includes: pandas, scikit-learn, flask, pytest, pandera, great_expectations, mlflow, requests)

----------------------------------------------------
4. ✅ Validate Input Data (Great Expectations)
----------------------------------------------------

python validate_data.py

Checks:
- Null values in 'Age'
- Fare within bounds
- Valid categories in 'Sex'

----------------------------------------------------
5. 🧠 Train the ML Model (MLflow Logging Enabled)
----------------------------------------------------

python train_model.py

Saves model to: model/titanic_model.pkl
MLflow logs parameters, accuracy, and model

----------------------------------------------------
6. 🌐 Start the API Server (Flask)
----------------------------------------------------

cd app
python model_api.py

Server runs at:
http://127.0.0.1:5000/predict

Sample Payload:
{
  "features": [3, 0, 22, 7.25]
}

----------------------------------------------------
7. 🧪 Run All Tests (API, Schema, Model)
----------------------------------------------------

cd ..
pytest

Runs:
- API tests
- Accuracy test
- Pandera schema checks

----------------------------------------------------
8. 📊 Launch MLflow UI
----------------------------------------------------

mlflow ui

Open in browser:
http://localhost:5000

