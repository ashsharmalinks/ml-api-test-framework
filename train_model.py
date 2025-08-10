import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile

from preprocessing.pipeline import get_preprocessing_pipeline

# Set MLflow tracking (local file-based or remote if needed)
mlflow.set_tracking_uri("http://localhost:5000")

# Optional: autolog (or log manually)
mlflow.sklearn.autolog()

# Create model directory if not exists
os.makedirs("model", exist_ok=True)

# Load dataset
df = pd.read_csv("data/train.csv")
X = df.drop(columns=["Survived"])
y = df["Survived"]

# Build preprocessing pipeline
preprocessor = get_preprocessing_pipeline(X)
X_processed = preprocessor.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

# 👉 Start MLflow run and set environment tags here:
with mlflow.start_run():
    mlflow.set_tag("env", "local")  # 👈 Choose: dev, test, prod, local
    mlflow.set_tag("framework", "sklearn")
    mlflow.set_tag("project", "titanic_model")

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)

    # Save model and log as artifact
    model_path = "model/titanic_model.pkl"
    joblib.dump(model, model_path)
    mlflow.log_artifact(model_path, artifact_path="model")

    # Print and log classification report
    print(f"✅ Trained and logged model with accuracy: {accuracy:.2f}")
    print("\n📊 Classification Report:\n")
    report = classification_report(y_test, preds, output_dict=True)
    print(classification_report(y_test, preds))

    # Confusion matrix
    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["Not Survived", "Survived"], yticklabels=["Not Survived", "Survived"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")

    # Save and log confusion matrix image
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        plt.savefig(temp.name)
        mlflow.log_artifact(temp.name, artifact_path="plots")

    plt.close()
